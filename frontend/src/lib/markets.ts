/**
 * Cotações reais do mercado agro — consumidas via rota server-side (/api/markets)
 * e direto nos Server Components da home (cache por processo).
 *
 * Fontes editoriais:
 * - CEPEA: boi gordo, bezerro, milho, soja, etanol e frango.
 * - Google Finance: dólar e Ibovespa.
 *
 * Regras: sempre validar, nunca inventar número; valor ausente vira estado
 * "indisponível" claro para o leitor, com a fonte identificada.
 */

export type MarketDirection = "up" | "down" | "flat" | null;

export type MarketItem = {
  id: string;
  label: string;
  sublabel: string;
  value: string | null;
  changePct: number | null;
  direction: MarketDirection;
  source: string;
  sourceHref: string;
  updatedAt: string | null;
  status: "ok" | "unavailable";
  note?: string;
};

export type MarketFeed = {
  items: MarketItem[];
  fetchedAt: string;
  degraded: boolean;
};

const MARKET_TTL_MS = 90_000;

type CepeaAsset = {
  id: string;
  label: string;
  sublabel: string;
  page: string;
  min: number;
  max: number;
};

const CEPEA_BASE = "https://www.cepea.org.br/br/indicador";
const SOY: CepeaAsset = {
  id: "soja",
  label: "Soja",
  sublabel: "R$/saca",
  page: `${CEPEA_BASE}/soja.aspx`,
  min: 1,
  max: 1_000,
};
const CORN: CepeaAsset = {
  id: "milho",
  label: "Milho",
  sublabel: "R$/saca",
  page: `${CEPEA_BASE}/milho.aspx`,
  min: 1,
  max: 1_000,
};
const BOI: CepeaAsset = {
  id: "boi-gordo",
  label: "Boi gordo",
  sublabel: "R$/@ · SP",
  page: `${CEPEA_BASE}/boi-gordo.aspx`,
  min: 1,
  max: 1_000,
};
const CALF: CepeaAsset = { id: "bezerro", label: "Bezerro", sublabel: "R$/cabeça", page: `${CEPEA_BASE}/bezerro.aspx`, min: 1, max: 20_000 };
const ETHANOL: CepeaAsset = { id: "etanol", label: "Etanol", sublabel: "R$/litro", page: `${CEPEA_BASE}/etanol.aspx`, min: 0.1, max: 30 };
const CHICKEN: CepeaAsset = { id: "frango", label: "Frango", sublabel: "R$/kg", page: `${CEPEA_BASE}/frango.aspx`, min: 0.1, max: 100 };
const GOOGLE_USD = {
  id: "dolar",
  label: "Dólar",
  sublabel: "USD/BRL",
  source: "Google Finance (USD/BRL)",
  href: "https://www.google.com/finance/beta/quote/USD-BRL",
  min: 1,
  max: 20,
};
const GOOGLE_IBOV = {
  id: "ibovespa",
  label: "Ibovespa",
  sublabel: "B3",
  source: "Google Finance (Ibovespa)",
  href: "https://www.google.com/finance/beta/quote/IBOV:INDEXBVMF",
  min: 50_000,
  max: 400_000,
};

function clampPct(value: number): number {
  if (!Number.isFinite(value)) return 0;
  return Math.min(99.99, Math.max(-99.99, value));
}

function directionOf(pct: number | null): MarketDirection {
  if (pct === null) return null;
  if (pct > 0.05) return "up";
  if (pct < -0.05) return "down";
  return "flat";
}

function formatDecimal(value: number, digits = 2): string {
  return value.toLocaleString("pt-BR", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}

function formatBRL(value: number): string {
  return value.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

type Quote = { value: number; changePct: number | null; updatedAt: string | null };

function parseNumberPtBR(raw: string): number {
  const normalized = raw
    .replace(/[R$\s%]/g, "")
    .replace(/[–−]/g, "-")
    .replace(/\./g, "")
    .replace(/,/g, ".");
  return Number(normalized);
}

async function fetchText(url: string, timeoutMs = 10_000): Promise<string> {
  const res = await fetch(url, {
    // Cotações não podem herdar o cache persistente do fetch do Next. O TTL
    // abaixo controla a cadência por processo sem apresentar um fechamento
    // antigo como se fosse atualização atual.
    cache: "no-store",
    headers: {
      accept: "text/html,application/xhtml+xml",
      "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
      "accept-language": "pt-BR,pt;q=0.9,en;q=0.8",
    },
    signal: AbortSignal.timeout(timeoutMs),
  });
  if (!res.ok) throw new Error(`http ${res.status} ${url}`);
  return res.text();
}

function extractFirst(html: string, pattern: RegExp): string | null {
  const match = html.match(pattern);
  return match && match[1] ? match[1] : null;
}

async function fetchCepea(asset: CepeaAsset): Promise<Quote> {
  const html = await fetchText(asset.page);
  const table = extractFirst(html, /<table[^>]+imagenet-indicador1[^>]*>([\s\S]*?)<\/table>/i);
  const priceRaw = table && extractFirst(table, /<td[^>]*>\s*([\d.]+,\d{2})\s*<\/td>/i);
  if (!priceRaw) throw new Error("cepea price missing");
  const value = parseNumberPtBR(priceRaw);
  if (!Number.isFinite(value) || value < asset.min || value > asset.max) throw new Error(`cepea price out of range: ${priceRaw}`);

  const pctRaw = table && extractFirst(table, /<td[^>]*>\s*([+\-–−]?[\d.,]+)%\s*<\/td>/i);
  let changePct = null;
  if (pctRaw) {
    const parsed = parseNumberPtBR(pctRaw);
    if (Number.isFinite(parsed)) changePct = clampPct(parsed);
  }
  return { value, changePct, updatedAt: null };
}

async function fetchGoogleFinance(asset: typeof GOOGLE_USD | typeof GOOGLE_IBOV): Promise<Quote> {
  const html = await fetchText(asset.href);
  const valueRaw = extractFirst(html, /data-last-price="([\d.,]+)"/i);
  if (!valueRaw) throw new Error("google finance price missing");
  const value = Number(valueRaw.replace(/,/g, ""));
  if (!Number.isFinite(value) || value < asset.min || value > asset.max) throw new Error(`google finance price out of range: ${valueRaw}`);
  return { value, changePct: null, updatedAt: null };
}

async function buildFeed(): Promise<MarketFeed> {
  const results = await Promise.allSettled([
    fetchCepea(BOI),
    fetchCepea(CALF),
    fetchCepea(CORN),
    fetchCepea(SOY),
    fetchCepea(ETHANOL),
    fetchGoogleFinance(GOOGLE_USD),
    fetchCepea(CHICKEN),
    fetchGoogleFinance(GOOGLE_IBOV),
  ]);

  const mk = (
    base: { id: string; label: string; sublabel: string; source: string; href: string },
    resolved: PromiseSettledResult<Quote>,
    formatter: (value: number) => string,
    note?: string,
  ): MarketItem => {
    if (resolved.status === "rejected" || !resolved.value) {
      return { id: base.id, label: base.label, sublabel: base.sublabel, value: null, changePct: null, direction: null, source: base.source, sourceHref: base.href, updatedAt: null, status: "unavailable", note: note ?? "Fonte temporariamente fora do ar." };
    }
    const { value, changePct, updatedAt } = resolved.value;
    return { id: base.id, label: base.label, sublabel: base.sublabel, value: formatter(value), changePct, direction: directionOf(changePct), source: base.source, sourceHref: base.href, updatedAt, status: "ok" };
  };

  const items: MarketItem[] = [
    mk({ ...BOI, source: "CEPEA", href: BOI.page }, results[0], formatBRL),
    mk({ ...CALF, source: "CEPEA", href: CALF.page }, results[1], formatBRL),
    mk({ ...CORN, source: "CEPEA", href: CORN.page }, results[2], formatBRL),
    mk({ ...SOY, source: "CEPEA", href: SOY.page }, results[3], formatBRL),
    mk({ ...ETHANOL, source: "CEPEA", href: ETHANOL.page }, results[4], formatBRL),
    mk(GOOGLE_USD, results[5], formatBRL),
    mk({ ...CHICKEN, source: "CEPEA", href: CHICKEN.page }, results[6], formatBRL),
    mk(GOOGLE_IBOV, results[7], (v) => formatDecimal(v)),
  ];

  const degraded = items.some((item) => item.status === "unavailable");
  return { items, fetchedAt: new Date().toISOString(), degraded };
}

let cached: { at: number; feed: MarketFeed } | null = null;
let inflight: Promise<MarketFeed> | null = null;

export function getMarketFeed(): Promise<MarketFeed> {
  if (cached && Date.now() - cached.at < MARKET_TTL_MS) return Promise.resolve(cached.feed);
  if (inflight) return inflight;
  inflight = buildFeed()
    .then((feed) => {
      cached = { at: Date.now(), feed };
      inflight = null;
      return feed;
    })
    .catch((error) => {
      inflight = null;
      throw error;
    });
  return inflight;
}

export type { MarketFeed as MarketFeedResponse };
