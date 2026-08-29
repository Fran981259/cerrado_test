import realArticles from "@/data/articles.json";

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

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Artigos reais coletados via scanner (26 artigos de O Estado Online + Agência MS)
const REAL_ARTICLES = realArticles as Article[];

function filterAndSlice(articles: Article[], params?: { category?: string; limit?: number; offset?: number }) {
  let out = articles;
  if (params?.category) out = out.filter((a) => a.category === params.category);
  const offset = params?.offset ?? 0;
  const limit = params?.limit ?? 24;
  return out.slice(offset, offset + limit);
}

export async function fetchNews(params?: { category?: string; limit?: number; offset?: number }): Promise<Article[]> {
  const search = new URLSearchParams();
  if (params?.category) search.set("category", params.category);
  if (params?.limit) search.set("limit", String(params.limit));
  if (params?.offset) search.set("offset", String(params.offset));

  const url = `${API_URL}/api/news${search.toString() ? `?${search}` : ""}`;
  try {
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error(`API ${res.status}`);
    const data = await res.json();
    const list = (data.news ?? data.articles ?? data ?? []) as Article[];
    if (list.length > 0) return filterAndSlice(list, params);
    // API vazia -> usa reais
    return filterAndSlice(REAL_ARTICLES, params);
  } catch {
    // API offline -> usa reais
    return filterAndSlice(REAL_ARTICLES, params);
  }
}

export async function fetchArticleBySlug(slug: string): Promise<Article | null> {
  try {
    const res = await fetch(`${API_URL}/api/news/${slug}`, { next: { revalidate: 60 } });
    if (res.ok) {
      const data = await res.json();
      if (data && data.title) return data as Article;
    }
  } catch {}
  // fallback local
  return REAL_ARTICLES.find((a) => a.slug === slug) ?? null;
}

// Para compatibilidade: MOCK agora são os reais
export const MOCK_ARTICLES: Article[] = REAL_ARTICLES;

// Helper para sitemap/build
export function getAllRealArticles(): Article[] {
  return REAL_ARTICLES;
}
