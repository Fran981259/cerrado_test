export type EditorialStatus = "draft" | "classified" | "review" | "rewritten" | "failed" | "published";

export type EditorialArticle = {
  slug: string;
  title: string;
  summary?: string | null;
  content?: string | null;
  original_text?: string | null;
  category: string;
  importance_score?: number | null;
  engagement_score?: number | null;
  status: EditorialStatus;
  writing_review?: Array<{ message?: string }>;
};

export type EditorialChanges = Pick<
  EditorialArticle,
  "category" | "importance_score" | "engagement_score" | "status"
>;

type QueueResponse = { total?: number; limit?: number; offset?: number; articles?: EditorialArticle[] };

export type EditorialQueue = { total: number; limit: number; offset: number; articles: EditorialArticle[] };

/** Loads the protected editorial queue with the operator-provided key. */
export async function fetchEditorialQueue(apiKey: string, offset = 0, limit = 50): Promise<EditorialQueue> {
  const response = await fetch(`/api/editorial/review?offset=${offset}&limit=${limit}`, {
    headers: { "X-API-Key": apiKey },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(response.status === 401 ? "Chave editorial inválida." : "Não foi possível carregar a fila.");
  const payload = (await response.json()) as QueueResponse;
  return {
    total: Number(payload.total ?? 0),
    limit: Number(payload.limit ?? limit),
    offset: Number(payload.offset ?? offset),
    articles: Array.isArray(payload.articles) ? payload.articles : [],
  };
}

/** Persists editorial decisions for one article. */
export async function updateEditorialArticle(apiKey: string, slug: string, changes: EditorialChanges): Promise<void> {
  const response = await fetch(`/api/editorial/review/${encodeURIComponent(slug)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", "X-API-Key": apiKey },
    body: JSON.stringify(changes),
  });
  if (!response.ok) throw new Error(response.status === 401 ? "Chave editorial inválida." : "A revisão não foi salva.");
}
