import Link from "next/link";
import { Suspense } from "react";
import { fetchNews, MOCK_ARTICLES } from "@/lib/api";
import { NewsCard } from "@/components/NewsCard";
import CategoryFilter from "@/components/CategoryFilter";
import Ticker from "@/components/Ticker";

export const revalidate = 60;

export default async function Home({ searchParams }: { searchParams: Promise<{ cat?: string }> }) {
  const { cat } = await searchParams;
  let articles = await fetchNews({ category: cat, limit: 24 });
  if (articles.length === 0) articles = MOCK_ARTICLES;

  // filtro client já aplicado via API, mas garante
  const filtered = cat ? articles.filter((a) => a.category === cat) : articles;
  const list = filtered.length ? filtered : articles;

  const hero = list[0];
  const secondary = list.slice(1, 5);
  const rest = list.slice(5);

  return (
    <div>
      <Ticker articles={list} />

      <div className="container-custom py-6">
        <Suspense fallback={<div className="h-10 bg-zinc-100 rounded-full animate-pulse" />}>
          <CategoryFilter />
        </Suspense>
      </div>

      <div className="container-custom pb-10">
        {hero && (
          <div className="grid lg:grid-cols-[2fr_1fr] gap-8">
            <NewsCard article={hero} variant="hero" />
            <div className="border-l border-zinc-200 pl-8 hidden lg:block">
              <h2 className="text-xl font-display font-bold text-text-primary mb-4">Destaques</h2>
              <div className="grid gap-2">
                {secondary.map((a) => (
                  <NewsCard key={a.slug || a.title} article={a} variant="compact" />
                ))}
              </div>
            </div>
            {/* Mobile secondary */}
            <div className="lg:hidden grid gap-4">
              {secondary.map((a) => (
                <NewsCard key={a.slug || a.title} article={a} variant="compact" />
              ))}
            </div>
          </div>
        )}

        {rest.length > 0 && (
          <>
            <h2 className="mt-16 mb-8 text-2xl font-display font-bold text-text-primary flex items-center gap-4">
              Últimas notícias
              {cat && <span className="text-base font-medium text-text-muted">— {cat}</span>}
              <span className="flex-1 h-px bg-zinc-200" />
            </h2>
            <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {rest.map((a) => (
                <NewsCard key={a.slug || a.title} article={a} />
              ))}
            </div>
          </>
        )}
        
        {list.length === 0 && (
          <div className="py-20 text-center text-text-muted">Nenhuma notícia encontrada.</div>
        )}
      </div>
      <div className="container-custom pb-20">
        <div className="rounded-lg bg-white border border-zinc-200 p-8 flex flex-col md:flex-row items-center justify-between gap-6">
          <div>
            <h3 className="font-display font-bold text-xl text-text-primary">Receba as principais notícias de MS</h3>
            <p className="text-sm text-text-muted mt-1">Atualizações diárias direto no seu e-mail. Sem spam.</p>
          </div>
          <form className="flex gap-2 w-full md:w-auto">
            <input placeholder="Seu e-mail" className="flex-1 md:w-72 rounded border border-zinc-300 px-4 py-2.5 text-sm outline-none focus:border-accent-soil focus:ring-1 focus:ring-accent-soil" />
            <button type="button" className="shrink-0 rounded bg-text-primary text-white px-6 py-2.5 text-sm font-bold hover:bg-accent-soil transition-colors">Assinar</button>
          </form>
        </div>
      </div>
    </div>
  );
}
