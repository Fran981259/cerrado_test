"""
Reescreve TODO o acervo publicado no padrão profissional enxuto
(pirâmide invertida, 350-500 palavras, sem rótulos de seção),
aplica correção de categorias e normaliza assinatura para
"Por <Nome>, direto da redação".
Uso: .venv/bin/python scripts/rewrite_all_new_standard.py
"""
import logging
import re
import time
from datetime import datetime

from app.database import get_session
from app.schema import NewsArticle
from app.rewriter import load_reporters_config
from app.groq_client import GroqClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger("rewrite_all")

FORBIDDEN = re.compile(r"^(LEAD|APURAÇÃO|CONTEXTO|DESENVOLVIMENTO|DADOS E NÚMEROS)\s*[—–-]", re.I | re.M)
TAIL_OLD = re.compile(r"Por ([A-ZÀ-ÚÂÊÎÔÛÃÕÇÉÍÓÚÜÑ ]+?), do Portal Cerrado\s*$", re.I)

# id -> categoria correta (tempo sai de esporte; general redistribuído)
CATFIX = {
    1: "culture", 2: "economy", 3: "culture", 4: "culture", 5: "economy",
    12: "security", 13: "security", 14: "politics", 17: "economy",
    20: "security", 21: "security", 23: "culture", 24: "security",
    28: "politics", 30: "clima", 32: "security", 33: "security",
    34: "security", 37: "clima", 39: "clima", 40: "security",
    41: "economy", 43: "security", 44: "politics", 45: "security",
    46: "security",
}


def valid(text: str, attribution: str):
    words = len((text or "").split())
    if not (700 <= words <= 1300):
        return False, f"fora da faixa ({words})"
    if FORBIDDEN.search(text or ""):
        return False, "rótulo de seção"
    if not (text or "").strip().endswith(attribution.strip()):
        return False, "sem assinatura"
    return True, f"ok {words}"


def main():
    db = get_session()
    reporters = load_reporters_config()
    groq = GroqClient()
    if not groq.api_key:
        print("SEM GROQ_API_KEY — abortando")
        return

    # 1) categorias + tags
    fixed = 0
    for aid, cat in CATFIX.items():
        art = db.query(NewsArticle).filter(NewsArticle.id == aid).first()
        if art and art.category != cat:
            art.category = cat
            art.tags = [cat]
            fixed += 1
    db.commit()
    print(f"categorias corrigidas: {fixed}")

    # 2) reescrita
    arts = db.query(NewsArticle).filter(NewsArticle.status == "published").order_by(NewsArticle.id).all()
    by_slug = {}
    for r in db.query(NewsArticle.reporter_id).distinct():
        pass
    from app.schema import Reporter
    rep_by_id = {r.id: r for r in db.query(Reporter).all()}

    ok, kept, failed = 0, 0, []
    for art in arts:
        rep = rep_by_id.get(art.reporter_id)
        slug = rep.slug if rep else "enzo.bianchi"
        profile = reporters.get(slug) or list(reporters.values())[0]
        attribution = profile.attribution
        # pula quem já está no padrão novo (economiza Groq)
        cur = (art.content or "").strip()
        if cur.endswith(attribution.strip()) and 700 <= len(cur.split()) <= 1300 and not FORBIDDEN.search(cur):
            ok += 1
            logger.info(f"[{art.id}] já no padrão, pulada: {art.title[:50]}")
            continue
        srcs = art.sources if isinstance(art.sources, list) else []
        url = srcs[0].get("url", "") if srcs and isinstance(srcs[0], dict) else ""
        name = srcs[0].get("name", "") if srcs and isinstance(srcs[0], dict) else ""
        try:
            body_in = (art.content or "")[:3000]
            res = groq.rewrite_article(
                {"title": art.title, "summary": (art.summary or "")[:600], "source": name or "Portal de Notícias",
                 "url": url, "body": body_in},
                profile.get_system_prompt(), attribution, related_sources=None,
            )
            text = (res.get("rewritten_content") or "").strip()
            # garante assinatura exata no fecho (modelo às vezes varia ou omite)
            if text and not text.endswith(attribution.strip()):
                if re.search(r"direto da reda[cç][aã]o\s*$", text, re.I):
                    text = re.sub(r"Por .{0,60}direto da reda[cç][aã]o\s*$", attribution.strip(), text, flags=re.I)
                else:
                    text = text + "\n\n" + attribution.strip()
            good, why = valid(text, attribution)
            if not good:
                kept += 1
                logger.info(f"[{art.id}] mantida ({why}): {art.title[:50]}")
            else:
                art.content = text
                paras = [p.strip() for p in text.split("\n\n") if p.strip()]
                art.summary = (paras[0][:300].rsplit(" ", 1)[0] + "...") if paras and len(paras[0]) > 300 else (paras[0] if paras else art.summary)
                art.updated_at = datetime.utcnow()
                ok += 1
                logger.info(f"[{art.id}] reescrita ({why}): {art.title[:50]}")
            db.commit()
        except Exception as e:
            db.rollback()
            kept += 1
            failed.append(art.id)
            logger.error(f"[{art.id}] erro, mantida: {e}")
        time.sleep(25)

    # 3) normaliza assinatura de quem ficou no texto antigo
    norm = 0
    for art in db.query(NewsArticle).filter(NewsArticle.status == "published").all():
        rep = rep_by_id.get(art.reporter_id)
        disp = (rep.display_name.title() if rep else "")
        new_tail = f"Por {disp}, direto da redação" if disp else ""
        if art.content and TAIL_OLD.search(art.content) and new_tail:
            art.content = TAIL_OLD.sub(new_tail, art.content)
            norm += 1
    db.commit()
    print(f"reescritas: {ok} | mantidas: {kept} | falhas: {failed} | assinaturas normalizadas: {norm}")
    db.close()


if __name__ == "__main__":
    main()
