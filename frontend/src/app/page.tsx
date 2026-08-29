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
          <div className="grid lg:grid-cols-[2fr_1fr] gap-6">
            <NewsCard article={hero} variant="hero" />
            <div className="grid gap-4 content-start">
              {secondary.map((a) => (
                <NewsCard key={a.slug || a.title} article={a} variant="compact" />
              ))}
            </div>
          </div>
        )}

        {rest.length > 0 && (
          <>
            <h2 className="mt-10 mb-4 text-lg font-extrabold tracking-tight text-zinc-900 flex items-center gap-2">
              <span className="h-6 w-1 bg-[#e63946] rounded-full" /> Últimas notícias
              {cat && <span className="text-sm font-semibold text-zinc-500">— {cat}</span>}
            </h2>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {rest.map((a) => (
                <NewsCard key={a.slug || a.title} article={a} />
              ))}
            </div>
          </>
        )}

        {list.length === 0 && (
          <div className="py-20 text-center">
            <p className="text-zinc-500 font-medium">Nenhuma notícia encontrada para esta categoria.</p>
            <Link href="/" className="inline-block mt-4 text-[#e63946] font-bold">← Ver todas</Link>
          </div>
        )}
      </div>

      <div className="container-custom">
        <div className="rounded-2xl bg-white border border-zinc-100 p-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <h3 className="font-extrabold text-zinc-900">Receba as principais notícias de MS</h3>
            <p className="text-sm text-zinc-500">Atualizações diárias direto no seu e-mail. Sem spam.</p>
          </div>
          <form className="flex gap-2 w-full md:w-auto">
            <input placeholder="Seu e-mail" className="flex-1 md:w-72 rounded-full border border-zinc-200 px-5 py-3 text-sm outline-none focus:border-[#e63946] focus:ring-2 focus:ring-[#e63946]/20" />
            <button type="button" className="shrink-0 rounded-full bg-[#1a1a2e] text-white px-6 py-3 text-sm font-bold hover:bg-black">Assinar</button>
          </form>
        </div>
      </div>
    </div>
  );
}
