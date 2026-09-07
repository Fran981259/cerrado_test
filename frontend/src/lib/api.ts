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
  sources?: string[];
  tags?: string[];
  is_curiosity?: boolean;
  source?: string;
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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://portal_cerrado:8000";

export async function fetchNews(params?: { category?: string; limit?: number; offset?: number }): Promise<Article[]> {
  try {
    const search = new URLSearchParams();
    if (params?.category) search.set("category", params.category);
    if (params?.limit) search.set("limit", String(params.limit));
    if (params?.offset) search.set("offset", String(params.offset));

    const url = `${API_URL}/api/news${search.toString() ? `?${search}` : ""}`;
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) {
      return [];
    }
    const data = await res.json();
    const list = (data.news ?? data.articles ?? data ?? []) as Article[];
    const offset = params?.offset ?? 0;
    const limit = params?.limit ?? 24;
    const filtered = params?.category ? list.filter((a) => a.category === params.category) : list;
    return filtered.slice(offset, offset + limit);
  } catch {
    return [];
  }
}

export async function fetchArticleBySlug(slug: string): Promise<Article | null> {
  try {
    const res = await fetch(`${API_URL}/api/news/${slug}`, { next: { revalidate: 60 } });
    if (!res.ok) {
      return null;
    }
    const data = await res.json();
    return data && data.title ? (data as Article) : null;
  } catch {
    return null;
  }
}

export async function fetchTrends(limit?: number): Promise<TrendSignal[]> {
  try {
    const search = new URLSearchParams();
    if (limit) search.set("limit", String(limit));
    const url = `${API_URL}/api/trends${search.toString() ? `?${search}` : ""}`;
    const res = await fetch(url, { next: { revalidate: 300 } });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.trends ?? []) as TrendSignal[];
  } catch {
    return [];
  }
}

// Helper para sitemap/build, mantido para consumir a API real.
export function getAllRealArticles(): Promise<Article[]> {
  return fetchNews({ limit: 100 });
}
