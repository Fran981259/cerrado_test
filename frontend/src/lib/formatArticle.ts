/**
 * Formatação de matéria para cara de notícia real.
 * O conteúdo do banco é texto puro com \n\n — sem <p>, sem títulos.
 * Aqui convertemos para HTML semântico com classes do .article-body.
 */

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function inline(md: string): string {
  let h = escapeHtml(md);
  // **negrito**
  h = h.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  // *itálico* (evita conflito com listas)
  h = h.replace(/(^|[\s(])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  return h;
}

export function formatArticleContent(raw: string, summary?: string, title?: string): string {
  if (!raw || !raw.trim()) return "";
  // Se já vier com <p> do banco, devolve como está
  if (/<p[\s>]|<h2[\s>]|<ul[\s>]/i.test(raw)) return raw;

  const lines = raw.replace(/\r\n/g, "\n").split("\n");
  const out: string[] = [];
  let para: string[] = [];
  let list: string[] = [];
  let skipBullets = false;
  let firstChecks = 0;

  const norm = (s: string) => s.toLowerCase().replace(/\s+/g, " ").trim();
  const cleanLead = norm(summary || "");
  const cleanTitle = norm(title || "");
  const overlap = (a: string, b: string) => {
    const wa = a.split(" ").filter((w) => w.length > 3);
    const wb = new Set(b.split(" ").filter((w) => w.length > 3));
    if (!wa.length || wb.size < 5) return 0;
    const hit = wa.filter((w) => wb.has(w)).length;
    return hit / Math.min(wa.length, wb.size);
  };
  const isLeadRepeat = (text: string) => {
    const t = norm(text);
    if (t.length < 40) return false;
    // Texto muito maior que lead/título nunca é repetição (protege o artigo todo)
    if (t.split(" ").length > 150) return false;
    // título embutido no corpo? descarta
    if (cleanTitle && (t === cleanTitle || overlap(t, cleanTitle) > 0.85)) return true;
    if (!cleanLead || cleanLead.length < 40) return false;
    if (t.startsWith(cleanLead.slice(0, 60)) || cleanLead.startsWith(t.slice(0, 60))) return true;
    return overlap(t, cleanLead) > 0.65;
  };

  const pushPara = (text: string) => {
    // Repetições do lead/título no início do corpo? descarta (evita repetição)
    if (firstChecks < 3) {
      firstChecks++;
      if (isLeadRepeat(text)) return;
    }
    // Muro de texto (>60 palavras)? quebra por orçamento de ~55 palavras
    const words = text.split(/\s+/).length;
    if (words > 60) {
      const sentences = text.match(/[^.!?…]+[.!?…]+["“”)]?/g) || [text];
      let buf = "";
      let bufWords = 0;
      const flush = () => {
        if (buf.trim()) out.push(`<p>${inline(buf.trim())}</p>`);
        buf = "";
        bufWords = 0;
      };
      for (const s of sentences) {
        const w = s.trim().split(/\s+/).length;
        if (bufWords + w > 60 && bufWords >= 20) flush();
        buf += (buf ? " " : "") + s.trim();
        bufWords += w;
      }
      flush();
      return;
    }
    out.push(`<p>${inline(text)}</p>`);
  };

  const flushPara = () => {
    let text = para.join(" ").trim();
    para = [];
    if (!text) return;
    // Limpa rótulos legados de template antigo (soavam IA) — vale para o acervo existente
    text = text.replace(/^(LEAD|APURAÇÃO|CONTEXTO|DESENVOLVIMENTO|DADOS E NÚMEROS)\s*[—–-]\s*/i, "");
    // Rede de segurança: prefixos de template antigo viram texto corrido
    text = text.replace(/^(O QUE DIZEM AS FONTES CRUZADAS|ANÁLISE E IMPACTO PARA MS|SERVIÇO E PRÓXIMOS PASSOS|DADOS E NÚMEROS|DESENVOLVIMENTO|CONTEXTO|APURAÇÃO)\s*[—–:\-]\s*/i, "");
    if (text.length < 30 && /fontes/i.test(text)) return;
    if (/https?:\/\//.test(text)) {
      text = text.replace(/\(https?:\/\/[^)]+\)/g, "").replace(/https?:\/\/\S+/g, "").trim();
      if (text.length < 30) return;
    }
    // Assinatura do repórter — destaque próprio (separa se vier colada ao parágrafo)
    const glued = text.match(/(.+[.?!…"”])\s+(Por .+, direto da reda[cç][aã]o)$/i);
    if (glued) {
      pushPara(glued[1]);
      out.push(`<p class="assinatura">${inline(glued[2])}</p>`);
      return;
    }
    if (/^Por .+, direto da reda[cç][aã]o$/i.test(text)) {
      out.push(`<p class="assinatura">${inline(text)}</p>`);
      return;
    }
    // Linha curta em MAIÚSCULAS ou terminada em : vira intertítulo
    if (/^[A-ZÀ-Ú0-9][A-ZÀ-Ú0-9\s\-–—,;:'"().]{12,80}:?$/.test(text) && text.length < 90 && !text.endsWith(".")) {
      out.push(`<h2>${inline(text.replace(/:$/, ""))}</h2>`);
      return;
    }
    pushPara(text);
  };

  const flushList = () => {
    if (!list.length) return;
    out.push(`<ul>${list.map((i) => `<li>${inline(i)}</li>`).join("")}</ul>`);
    list = [];
  };

  for (const line of lines) {
    const t = line.trim();
    // Assinatura sempre em bloco próprio com destaque, mesmo colada ao parágrafo
    if (/^Por .+, direto da reda[cç][aã]o$/i.test(t)) {
      flushPara();
      flushList();
      out.push(`<p class="assinatura">${escapeHtml(t)}</p>`);
      continue;
    }
    // Lixo de scraper: byline da fonte, datas soltas, CTAs (nunca da nossa assinatura)
    if (/^Por\s.{2,60}$/i.test(t)) {
      flushPara();
      continue;
    }
    if (/^(\d{1,2}\s+de\s+[a-zç]+\s+de\s+\d{4}|\d{2}\/\d{2}\/\d{4}|Atualizado|Em\s+\d{2}\/\d{2}\/\d{4}).{0,80}$/i.test(t)) {
      flushPara();
      continue;
    }
    if (/clique aqui|canal do .* whatsapp|siga .* no (whatsapp|instagram|facebook)/i.test(t) && t.length < 120) {
      flushPara();
      continue;
    }
    // Bloco de fontes no corpo nunca renderiza (botão Fonte original cobre)
    if (/^\*?\*?Fontes (consultadas|cruzadas)/i.test(t)) {
      flushPara();
      flushList();
      skipBullets = true;
      continue;
    }
    if (skipBullets) {
      if (/^[\*\-•]\s/.test(t) || t === "") continue;
      skipBullets = false;
    }
    if (!t) {
      flushPara();
      flushList();
      continue;
    }
    if (/^#{1,3}\s+/.test(t)) {
      flushPara();
      flushList();
      out.push(`<h2>${inline(t.replace(/^#{1,3}\s+/, ""))}</h2>`);
      continue;
    }
    if (/^(\*|-|•)\s+/.test(t)) {
      flushPara();
      list.push(t.replace(/^(\*|-|•)\s+/, ""));
      continue;
    }
    if (/^>\s+/.test(t)) {
      flushPara();
      flushList();
      out.push(`<blockquote>${inline(t.replace(/^>\s+/, ""))}</blockquote>`);
      continue;
    }
    // **Fontes Consultadas:** vira intertítulo + lista na sequência
    if (/^\*\*.+\*\*:?$/.test(t)) {
      flushPara();
      flushList();
      out.push(`<h2>${inline(t.replace(/:/g, ""))}</h2>`);
      continue;
    }
    para.push(t);
  }
  flushPara();
  flushList();
  return out.join("\n");
}

export function readingTimeMinutes(raw: string): number {
  const words = (raw || "").split(/\s+/).filter(Boolean).length;
  return Math.max(1, Math.round(words / 200));
}
