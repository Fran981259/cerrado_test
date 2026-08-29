"""
Scanner REAL de Notícias — Atualiza Brasil
Coleta headlines de portais brasileiros via HTTP.
"""

import re
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealPortalScanner:
    """Scanner que faz scraping REAL de portais."""
    
    PORTALS = [
        {
            "name": "MS News",
            "url": "https://www.msnews.com.br",
            "default_category": "general",
            "selectors": {
                "article": "article, .post, .noticia, .news-item",
                "title": "h1, h2, h3, .title, .titulo",
                "link": "a",
            }
        },
        {
            "name": "MS Todo Dia",
            "url": "https://www.mstododia.com.br",
            "default_category": "general",
            "selectors": {
                "article": "article, .post, .noticia",
                "title": "h1, h2, h3, .title",
                "link": "a",
            }
        },
        {
            "name": "Agência de Notícias MS",
            "url": "https://www.agenciadenoticias.ms.gov.br",
            "default_category": "politics",
            "selectors": {
                "article": "article, .post, .noticia",
                "title": "h1, h2, h3, .title",
                "link": "a",
            }
        },
        {
            "name": "O Estado Online",
            "url": "https://www.oestadoonline.com.br",
            "default_category": "general",
            "selectors": {
                "article": "article, .post, .noticia",
                "title": "h1, h2, h3, .title",
                "link": "a",
            }
        },
    ]
    
    CATEGORY_KEYWORDS = {
        "tech": [
            "tecnologia", "inovação", "software", "startup", "digital", "ti",
            "inteligência artificial", "robot", "cibernet", "google", "microsoft",
            "apple", "meta", "facebook", "instagram", "whatsapp", "telegram", "netflix",
            "celular", "smartphone", "iphone", "android", "programação", "código",
            "hacker", "ciberataque", "bitcoin", "criptomoeda", "nuvem", "cloud",
            "5g", "wi-fi", "internet", "site", "plataforma", "sistema",
            "cyber", "app", "apps", "automação", "robotica", "robotização"
        ],
        "sports": [
            "futebol", "esporte", "campeonato", "time", "jogador", "partida", "torneio",
            "gol", "bola", "estádio", "torcida", "atleta", "corrida", "natação",
            "basquete", "vôlei", "tênis", "ufc", "mma", "luta", "boxe", "ginástica",
            "sul-mato-grossense", "operário", "comercial", "novo", "athletico",
            "seleção", "brasileirão", "libertadores", "copa", "olimpíada", "paralimpíada",
            "treino", "modalidade", "esportivo", "competição", "medalha", "título"
        ],
        "security": [
            "segurança", "polícia", "crime", "investigação", "suspeito", "flagrante",
            "prisão", "preso", "delegacia", "assalto", "roubo", "furto", "estupro",
            "homicídio", "morte", "operação", "abordagem", "ocorrência", "registro",
            "boletim", "cárcere", "cadeia", "foragido", "mandado", "prender", "policiais",
            "quadrilha", "banda", "tráfico", "droga", "entorpecente", "entorpecente",
            "PF", "Polícia Federal", "PM", "Polícia Militar", "Civil", "crime", "criminal"
        ],
        "politics": [
            "governo", "política", "lei", "decreto", "parlamento", "eleição", "prefeito",
            "vereador", "deputado", "senador", "governador", "presidente", "campanha",
            "votação", "urna", "mandato", "gestão", "administração", "secretário",
            "assembleia", "câmara", "senado", "congresso", "estadual", "municipal",
            "reforma", "projeto", "indicação", "legislativo", "executivo", "judiciário",
            "tribunal", "STJ", "STF", "TRE", "TSE", "portaria", "resolução", "norma"
        ],
        "health": [
            "saúde", "hospitalar", "doença", "tratamento", "prevenção", "vacina", "médico",
            "enfermagem", "enfermeiro", "UBS", "SUS", "ambulatório", "clínica",
            "atendimento", "paciente", "diagnóstico", "receita", "medicamento", "remédio",
            "cirurgia", "exame", "laboratório", "hemocentro", "hemosul", "vacinação",
            "dengue", "covid", "gripe", "sarampo", "tuberculose", "HIV", "AIDS",
            "leito", "enfermaria", "UTI", "emergência", "pronto-socorro", "atender"
        ],
        "education": [
            "educação", "universidade", "estudante", "curso", "concurso", "escola",
            "UFMS", "IFMS", "faculdade", "aula", "professor", "aluno", "vestibular",
            "ENEM", "prova", "ensino", "graduação", "pós", "mestrado", "doutorado",
            "aprendizado", "conhecimento", "bolsa", "estágio", "formatura", "diploma",
            "ensino fundamental", "ensino médio", "ensino superior", "matricul", "inscrição"
        ],
        "agriculture": [
            "agronegócio", "safra", "produtor rural", "exportação", "agro", "plantio",
            "soja", "milho", "algodão", "cana-de-açúcar", "pecuária", "gado", "boi",
            "suíno", "frango", "pesca", "aquicultura", "fronteira", "pantanal",
            "colheita", "plantação", "fertilizante", "insumo", "máquina agrícola",
            "agricultor", "lavoura", "rebanho", "bovino", "suinocultura", "avicultura"
        ],
        "entertainment": [
            "cultura", "evento", "show", "arte", "festival", "música", "teatro",
            "cinema", "filme", "série", "ator", "atriz", "celebridade", "famoso",
            "carnaval", "festa junina", "réveillon", "feriado", "turismo",
            "viagem", "praia", "hotel", "restaurante", "gastronomia", "parque",
            "exposição", "pintura", "espetáculo", "concerto", "banda", "cant", "artista"
        ],
        "economy": [
            "economia", "mercado", "emprego", "bolsa", "investimento", "crédito",
            "trabalho", "salário", "piso salarial", "INSS", "imposto", "taxa", "juro",
            "banco", "finança", "receita", "arrecadação", "balança comercial",
            "comércio", "indústria", "fábrica", "varejo", "atacado", "negócio",
            "empresa", "funcionário", "contratação", "demissão", "vaga", "BNDES"
        ],
    }
    
    REPORTER_BY_CATEGORY = {
        "tech": "enzo.bianchi",
        "sports": "marcus.teixeira",
        "security": "rafael.dumas",
        "politics": "luciana.freitas",
        "health": "maya.santos",
        "education": "fernanda.lima",
        "agriculture": "bia.fernandes",
        "entertainment": "pedro.mendes",
        "economy": "carlos.nunes",
        "general": "enzo.bianchi",
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
    
    def scan_all(self) -> Dict:
        """Escaneia TODOS os portais configurados."""
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "portals": {},
            "articles": [],
            "summary": {"total": 0, "success": 0, "failed": 0},
        }
        
        for portal in self.PORTALS:
            try:
                portal_result = self._scan_portal(portal)
                results["portals"][portal["name"]] = portal_result
                results["summary"]["total"] += 1
                
                if portal_result["status"] == "success":
                    results["summary"]["success"] += 1
                    results["articles"].extend(portal_result["articles"])
                else:
                    results["summary"]["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Erro ao escanear {portal['name']}: {e}")
                results["summary"]["failed"] += 1
        
        return results
    
    def _scan_portal(self, portal: Dict) -> Dict:
        """Escaneia um portal específico."""
        name = portal["name"]
        url = portal["url"]
        
        logger.info(f"Escaneando: {name} ({url})")
        
        try:
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            articles = self._extract_articles(soup, portal, url)
            
            return {
                "name": name,
                "url": url,
                "status": "success",
                "articles_count": len(articles),
                "articles": articles,
            }
            
        except requests.exceptions.RequestException as e:
            logger.warning(f"Falha em {name}: {e}")
            return {
                "name": name,
                "url": url,
                "status": "failed",
                "error": str(e),
                "articles": [],
            }
    
    def _extract_articles(self, soup: BeautifulSoup, portal: Dict, 
                          base_url: str) -> List[Dict]:
        """Extrai artigos do HTML."""
        articles = []
        seen_urls = set()
        
        candidates = []
        candidates.extend(soup.find_all("article"))
        candidates.extend(soup.find_all(["h2", "h3"]))
        candidates.extend(soup.find_all("div", class_=re.compile(r"noticia|post|news|article|item", re.I)))
        
        for element in candidates:
            article = self._parse_element(element, portal, base_url)
            if article and article["url"] not in seen_urls:
                if self._is_valid_article(article):
                    articles.append(article)
                    seen_urls.add(article["url"])
                    
                    if len(articles) >= 25:
                        break
        
        return articles
    
    def _parse_element(self, element, portal: Dict, base_url: str) -> Optional[Dict]:
        """Parseia um elemento HTML em artigo."""
        try:
            if element.name in ["h2", "h3"]:
                link = element.find("a")
                if not link:
                    parent = element.parent
                    if parent:
                        link = parent.find("a")
                title = element.get_text(strip=True)
            else:
                link = element.find("a")
                title_elem = element.find(["h1", "h2", "h3", "h4"])
                if not title_elem:
                    title_elem = element.find("a")
                title = title_elem.get_text(strip=True) if title_elem else ""
            
            if not link or not link.get("href"):
                return None
            
            if not title or len(title) < 10:
                return None
            
            href = link["href"]
            if href.startswith("/"):
                href = urljoin(base_url, href)
            elif not href.startswith("http"):
                return None
            
            if any(skip in href.lower() for skip in ["/login", "/cadastro", "/contato", "/sobre", "/privacy", "/termos", "/search", "/feed", "/rss"]):
                return None
            
            category = self._classify(title)
            reporter = self.REPORTER_BY_CATEGORY.get(category, "enzo.bianchi")
            
            summary = self._extract_summary(element)
            
            return {
                "title": title[:300],
                "summary": summary,
                "url": href,
                "source": portal["name"],
                "source_url": portal["url"],
                "category": category,
                "reporter_slug": reporter,
                "scraped_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return None
    
    def _extract_summary(self, element) -> str:
        """Extrai o summary/resumo do artigo."""
        text_parts = []
        for p in element.find_all(["p", "span", "div"]):
            text = p.get_text(strip=True)
            if 50 < len(text) < 300:
                text_parts.append(text)
        return " ".join(text_parts[:2])[:500] if text_parts else ""
    
    def _classify(self, title: str) -> str:
        """Classifica um artigo por categoria usando word boundaries."""
        import re
        title_lower = title.lower()
        
        scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = 0
            for kw in keywords:
                # Usa word boundary para evitar "ia" em "entre", "campo" em "comportamento", etc.
                pattern = r'\b' + re.escape(kw.lower()) + r'\b'
                if re.search(pattern, title_lower):
                    score += 1
            if score > 0:
                scores[category] = score
        
        if scores:
            best_category = max(scores, key=scores.get)
            return best_category
        
        return "general"
    
    def _is_valid_article(self, article: Dict) -> bool:
        """Valida se é um artigo válido."""
        title = article.get("title", "")
        url = article.get("url", "")
        
        if len(title) < 20:
            return False
        
        if not url.startswith("http"):
            return False
        
        # Filtra títulos que não são notícias
        invalid_titles = [
            "últimas notícias", "última hora", "breaking news", "notícias ao vivo",
            "para o servidor", "contato", "sobre nós", "política de privacidade",
            "termos de uso", "cadastro", "login", "registro", "newsletter",
            "edição anterior", "arquivo", "search", "pesquisa", "search result",
            "click here", "saiba mais", "leia mais", "veja também", "veja mais",
            "voltar", "anterior", "próximo", "next", "previous",
        ]
        title_lower = title.lower().strip()
        if any(inv in title_lower for inv in invalid_titles):
            return False
        
        if len(title.split()) < 3:
            return False
        
        skip_patterns = [
            "javascript:", "mailto:", "#", "/search",
            "/login", "/signup", "/register", "/feed", "/rss",
            "/podcast", "/video", "/author", "/sobre", "/contato",
            "/privacy", "/termos", "/login", "/cadastro"
        ]
        if any(p in url.lower() for p in skip_patterns):
            return False
        
        return True


def scan_all_portals() -> Dict:
    """Função principal para escanear todos os portais."""
    scanner = RealPortalScanner()
    return scanner.scan_all()
