export type Article = {
  id?: number;
  title: string;
  slug?: string;
  summary?: string;
  content?: string;
  category: string;
  reporter_slug?: string;
  reporter?: string;
  url?: string;
  image_url?: string;
  published_at?: string;
  created_at?: string;
  updated_at?: string;
  sources?: Array<{ url: string; name?: string; title?: string }>;
  tags?: string[];
  is_curiosity?: boolean;
  region?: "ms";
  source?: string;
  importance_score?: number;
  engagement_score?: number;
  final_score?: number;
  priority_tier?: "TIER_1" | "TIER_2" | "TIER_3" | "REJECT";
};

export type NewsSitemapArticle = {
  slug: string;
  title: string;
  published_at: string;
  updated_at?: string;
};

export type TrendSignal = {
  topic: string;
  category?: string;
  score: number;
  article_count: number;
  window_hours?: number;
  generated_at?: string | null;
  evidence?: Array<{ title?: string; slug?: string; category?: string; weight?: number }>;
};

export type NewsResponse = {
  total: number;
  limit: number;
  offset: number;
  category?: string | null;
  reporter_slug?: string | null;
  region?: "ms" | null;
  sort_by?: "recent" | "trend";
  news: Article[];
};

function getApiBase(): string {
  // Client: usa rewrites /api -> evita CORS e hostname Docker interno
  if (typeof window !== "undefined") return "";
  return process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
}

export class UpstreamError extends Error {
  constructor() { super("Conteudo temporariamente indisponivel. Tente novamente."); }
}

function articleFromJson(value: unknown): Article {
  if (!value || typeof value !== "object" || !("title" in value) || typeof value.title !== "string") throw new UpstreamError();
  const article = value as Article;
  if (typeof article.category !== "string" || (article.content != null && typeof article.content !== "string")) throw new UpstreamError();
  article.sources = (Array.isArray(article.sources) ? article.sources : []).flatMap((source) => {
    if (!source || typeof source !== "object" || typeof source.url !== "string") return [];
    try {
      const url = new URL(source.url);
      return ["http:", "https:"].includes(url.protocol) && !url.username && !url.password ? [source] : [];
    } catch { return []; }
  });
  return article;
}

export async function fetchNews(params?: { category?: string; reporterSlug?: string; region?: "ms"; limit?: number; offset?: number; sortBy?: "recent" | "trend" }): Promise<Article[]> {
  const data = await fetchNewsResponse(params);
  return data.news;
}

function apiUrl(path: string, qs?: string): string {
  const base = typeof window !== "undefined" ? "" : getApiBase();
  return `${base}${path}${qs ? `?${qs}` : ""}`;
}
export async function fetchNewsResponse(params?: { category?: string; reporterSlug?: string; region?: "ms"; limit?: number; offset?: number; sortBy?: "recent" | "trend" }): Promise<NewsResponse> {
  try {
    const search = new URLSearchParams();
    if (params?.category) search.set("category", params.category);
    if (params?.reporterSlug) search.set("reporter_slug", params.reporterSlug);
    if (params?.region) search.set("region", params.region);
    if (params?.limit !== undefined) search.set("limit", String(params.limit));
    if (params?.offset !== undefined) search.set("offset", String(params.offset));
    if (params?.sortBy) search.set("sort_by", params.sortBy);

    const url = apiUrl("/api/news", search.toString());
    const res = await fetch(url, { next: { revalidate: 60 }, signal: AbortSignal.timeout(10000) });
    if (!res.ok) {
      throw new UpstreamError();
    }
    const data = await res.json();
    if (!Array.isArray(data.news) || !Number.isSafeInteger(data.total) || data.total < 0) throw new UpstreamError();
    return {
      total: Number(data.total ?? 0),
      limit: Number(data.limit ?? params?.limit ?? 20),
      offset: Number(data.offset ?? params?.offset ?? 0),
      category: (data.category ?? params?.category ?? null) as string | null,
      reporter_slug: (data.reporter_slug ?? params?.reporterSlug ?? null) as string | null,
      region: (data.region ?? params?.region ?? null) as "ms" | null,
      sort_by: (data.sort_by ?? params?.sortBy ?? "recent") as "recent" | "trend",
      news: data.news.map(articleFromJson),
    };
  } catch {
    throw new UpstreamError();
  }
}

export async function fetchArticleBySlug(slug: string): Promise<Article | null> {
  try {
    const res = await fetch(apiUrl(`/api/news/${encodeURIComponent(slug)}`), { next: { revalidate: 60 }, signal: AbortSignal.timeout(10000) });
    if (res.status === 404) return null;
    if (!res.ok) {
      throw new UpstreamError();
    }
    const data = await res.json();
    return articleFromJson(data);
  } catch {
    throw new UpstreamError();
  }
}

export async function fetchTrends(limit?: number): Promise<TrendSignal[]> {
  try {
    const search = new URLSearchParams();
    if (limit) search.set("limit", String(limit));
    const url = apiUrl("/api/trends", search.toString());
    const res = await fetch(url, { next: { revalidate: 300 }, signal: AbortSignal.timeout(10000) });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.trends ?? []) as TrendSignal[];
  } catch {
    return [];
  }
}

export function sortArticlesByTrendScore(articles: Article[], trends: TrendSignal[]): Article[] {
  const trendRank = new Map<string, number>();
  trends.forEach((trend, index) => {
    trendRank.set(trend.category || trend.topic, trends.length - index);
  });

  return [...articles].sort((a, b) => {
    const aRank = trendRank.get(a.category) || 0;
    const bRank = trendRank.get(b.category) || 0;
    if (aRank !== bRank) return bRank - aRank;

    const aPublished = a.published_at || a.created_at || "";
    const bPublished = b.published_at || b.created_at || "";
    return bPublished.localeCompare(aPublished);
  });
}

function localCalendarDay(value: Date): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "America/Campo_Grande",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(value);
  const field = (type: string) => parts.find((part) => part.type === type)?.value ?? "";
  return `${field("year")}-${field("month")}-${field("day")}`;
}

/** Prioritizes current-day local reporting, then editorial relevance and engagement. */
export function rankHomepageArticles(articles: Article[], now = new Date()): Article[] {
  const today = localCalendarDay(now);
  const rank = (article: Article) => {
    const date = new Date(article.published_at || article.created_at || 0);
    const validDate = !Number.isNaN(date.valueOf());
    return {
      isToday: validDate && localCalendarDay(date) === today ? 1 : 0,
      final: article.final_score ?? 0,
      importance: article.importance_score ?? 0,
      engagement: article.engagement_score ?? 0,
      timestamp: validDate ? date.valueOf() : 0,
    };
  };
  return [...articles].sort((a, b) => {
    const left = rank(a);
    const right = rank(b);
    return right.isToday - left.isToday || right.final - left.final || right.importance - left.importance || right.engagement - left.engagement || right.timestamp - left.timestamp;
  });
}

const DYNAMIC_POOL_MULTIPLIER = 4;
const ROTATION_INTERVAL_MS = 60_000;

/** Rotates a fresh, local-news selection without repeating articles already on the home. */
export function selectDynamicLocalNews(articles: Article[], excluded: Article[], limit: number, now = new Date()): Article[] {
  const excludedKeys = new Set(excluded.map((article) => article.slug || article.title));
  const candidates = rankHomepageArticles(articles, now).filter((article) => !excludedKeys.has(article.slug || article.title));
  const pool = candidates.slice(0, Math.max(limit * DYNAMIC_POOL_MULTIPLIER, limit));
  if (!pool.length) return [];
  const offset = Math.floor(now.getTime() / ROTATION_INTERVAL_MS) % pool.length;
  return Array.from({ length: Math.min(limit, pool.length) }, (_, index) => pool[(offset + index) % pool.length]);
}

// Helper para sitemap/build, mantido para consumir a API real.
export async function getAllRealArticles(): Promise<Array<Pick<Article, "slug" | "updated_at" | "published_at">>> {
  const articles = [];
  let after = 0;
  let through: number | undefined;
  while (true) {
    const search = new URLSearchParams({ after_id: String(after), limit: "1000" });
    if (through !== undefined) search.set("through_id", String(through));
    // sitemap sempre server-side -> usa base absoluta
    const response = await fetch(`${getApiBase()}/api/sitemap?${search}`, { cache: "no-store", signal: AbortSignal.timeout(10000) });
    if (!response.ok) throw new UpstreamError();
    const data = await response.json();
    if (!Array.isArray(data.articles) || !Number.isSafeInteger(data.through_id)) throw new UpstreamError();
    through = data.through_id;
    if (!data.articles.length) break;
    const next = data.articles.at(-1).id;
    if (!Number.isSafeInteger(next) || next <= after) throw new UpstreamError();
    after = next;
    articles.push(...data.articles);
    if (articles.length > 49990) throw new Error("Sitemap requires partitioning before exceeding 50000 URLs");
  }
  return articles;
}

/** Returns only the current news window for the dedicated Google News sitemap. */
export async function getRecentNewsSitemapArticles(): Promise<NewsSitemapArticle[]> {
  const response = await fetch(`${getApiBase()}/api/news-sitemap?limit=1000`, {
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });
  if (!response.ok) throw new UpstreamError();
  const data = await response.json();
  if (!Array.isArray(data.articles)) throw new UpstreamError();
  return data.articles.filter((article: unknown): article is NewsSitemapArticle => {
    if (!article || typeof article !== "object") return false;
    const record = article as Record<string, unknown>;
    return typeof record.slug === "string" && typeof record.title === "string" && typeof record.published_at === "string";
  });
}
