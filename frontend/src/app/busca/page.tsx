import type { Metadata } from "next";
import { fetchNewsResponse, type Article } from "@/lib/api";
import { NewsCard } from "@/components/NewsCard";

export const revalidate = 60;

const BASE = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";

export async function generateMetadata({ searchParams }: { searchParams: Promise<{ q?: string }> }): Promise<Metadata> {
  const { q } = await searchParams;
  const query = (q ?? "").trim();
  return {
    title: query ? `Busca: ${query} — Portal Cerrado` : "Busca — Portal Cerrado",
    description: query ? `Resultados da busca por "${query}" no Portal Cerrado.` : "Encontre notícias no Portal Cerrado.",
    robots: { index: false, follow: true },
    alternates: { canonical: `${BASE}/busca` },
  };
}

function matches(query: string, article: Article): boolean {
  const haystack = [article.title, article.summary, article.tags?.join(" "), article.category].filter(Boolean).join(" ").toLowerCase();
  return haystack.includes(query);
}

export default async function BuscaPage({ searchParams }: { searchParams: Promise<{ q?: string }> }) {
  const { q } = await searchParams;
  const query = (q ?? "").trim().toLowerCase();

  let results: Article[] = [];
  let scanned = 0;
  let loadError = "";
  if (query) {
    try {
      const seen = new Map<string, Article>();
      for (const offset of [0, 100]) {
        const response = await fetchNewsResponse({ limit: 100, offset, sortBy: "recent" });
        response.news.forEach((article) => seen.set(article.slug || article.title, article));
        if (response.news.length < 100) break;
      }
      const articles = Array.from(seen.values());
      scanned = articles.length;
      results = articles.filter((article) => matches(query, article));
    } catch {
      loadError = "A API de notícias não respondeu. Tente novamente em instantes.";
    }
  }

  return (
    <div className="container-editorial py-8">
      <h1 className="font-display text-3xl font-bold text-text-primary">Busca</h1>

      <form action="/busca" role="search" className="mt-5 flex max-w-xl gap-2">
        <label htmlFor="busca-q" className="sr-only">
          Termo de busca
        </label>
        <input
          id="busca-q"
          name="q"
          type="search"
          defaultValue={q}
          placeholder="Digite um termo para buscar…"
          autoFocus={!q}
          className="h-12 flex-1 rounded border border-black/15 bg-surface px-4 text-sm text-text-primary placeholder:text-text-muted"
        />
        <button type="submit" className="h-12 shrink-0 rounded bg-accent-soil px-6 text-sm font-bold uppercase tracking-wider text-white transition-colors hover:bg-charcoal">
          Buscar
        </button>
      </form>

      {loadError ? (
        <p className="mt-8 rounded border border-red-700/25 bg-red-50 px-5 py-4 text-sm font-semibold text-red-800" role="alert">
          {loadError}
        </p>
      ) : query && results.length === 0 ? (
        <p className="mt-8 rounded border border-dashed border-black/15 bg-black/[0.02] p-8 text-sm text-text-muted" role="status">
          Nenhuma notícia encontrada para &ldquo;{q}&rdquo;. Tente outro termo ou navegue pelas editorias.
        </p>
      ) : query ? (
        <>
          <p className="mt-6 text-sm text-text-muted" role="status">
            {results.length} {results.length === 1 ? "resultado" : "resultados"} para <strong>{q}</strong> · varredura nas {scanned} publicações mais recentes do portal.
          </p>
          <div className="mt-6 grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
            {results.map((article) => (
              <NewsCard key={article.slug || article.title} article={article} />
            ))}
          </div>
        </>
      ) : (
        <p className="mt-8 rounded border border-dashed border-black/15 bg-black/[0.02] p-8 text-sm text-text-muted">
          Digite um termo acima para buscar nas publicações recentes do Portal Cerrado.
        </p>
      )}
    </div>
  );
}