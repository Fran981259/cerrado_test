import { notFound, permanentRedirect } from "next/navigation";
import type { Metadata } from "next";
import { fetchNewsResponse, fetchTrends, type Article, type TrendSignal } from "@/lib/api";
import { NewsCard } from "@/components/NewsCard";
import Ticker from "@/components/Ticker";
import { TrendPanel } from "@/components/TrendPanel";
import { Pagination } from "@/components/Pagination";
import { parsePage } from "@/lib/pagination";
import { categorySlug } from "@/lib/categories";

export const revalidate = 60;

export async function generateMetadata({ searchParams }: { searchParams: Promise<{ cat?: string; page?: string }> }): Promise<Metadata> {
  const { cat, page } = await searchParams;
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";
  const currentPage = parsePage(page);
  if (currentPage === null) notFound();
  const canonical = cat ? `${base}/?cat=${cat}${currentPage > 1 ? `&page=${currentPage}` : ""}` : `${base}/${currentPage > 1 ? `?page=${currentPage}` : ""}`;
  const pageLabel = currentPage > 1 ? ` - Página ${currentPage}` : "";
  return {
    title: cat ? `Portal Cerrado | ${cat}${pageLabel}` : `Portal Cerrado${pageLabel}`,
    description: cat ? `Notícias de ${cat} no Portal Cerrado${pageLabel}` : `Notícias do Portal Cerrado${pageLabel}`,
    alternates: { canonical },
    robots: currentPage > 1 ? { index: false, follow: true } : { index: true, follow: true },
  };
}

export default async function Home({ searchParams }: { searchParams: Promise<{ cat?: string; page?: string }> }) {
  const { cat, page } = await searchParams;
  const perPage = 24;
  const currentPage = parsePage(page);
  if (currentPage === null) notFound();
  if (cat) {
    const slug = categorySlug(cat);
    if (!slug) notFound();
    permanentRedirect(`/categoria/${slug}${currentPage > 1 ? `?page=${currentPage}` : ""}`);
  }
  const offset = (currentPage - 1) * perPage;
  let list: Article[] = [];
  let trends: TrendSignal[] = [];
  let total = 0;
  let loadError = "";
  try {
    const [articlesResult, trendSignals] = await Promise.all([
      fetchNewsResponse({ category: cat, limit: perPage, offset, sortBy: "trend" }),
      fetchTrends(6),
    ]);
    list = articlesResult.news;
    total = articlesResult.total;
    trends = trendSignals;
  } catch {
    loadError = "A API de noticias nao respondeu. O frontend depende do backend real para carregar o conteudo.";
  }

  // Destaques determinísticos: hero = mais recente, secondary = próximos 4 (estável, sem Math.random)
  const pool = [...list.slice(0, 12)];
  const picked = pool.slice(0, 5).map((a) => a.slug || a.title);
  const hero = pool[0];
  const secondary = pool.slice(1, 5);
  const rest = [...list.filter((a) => !picked.includes(a.slug || a.title))];
  const totalPages = Math.max(1, Math.ceil((total || 0) / perPage));
  if (!loadError && currentPage > totalPages) notFound();

  return (
    <div className="relative overflow-hidden bg-canvas">
      {/* Fundo vivo animado */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.12),transparent_40rem),linear-gradient(180deg,#09090b_0%,#18181b_100%)] animate-breathe" />
      
      <div className="relative z-10">
        <Ticker />

      <section className="container-custom py-6 sm:py-7">
        <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-accent-soil">Jornalismo com credibilidade</p>
        <h1 className="mt-2 max-w-3xl font-display text-4xl font-black leading-[0.95] tracking-tight text-text-primary sm:text-5xl">O pulso de Mato Grosso do Sul.</h1>
        <p className="mt-3 max-w-2xl text-[15px] leading-relaxed text-text-muted">Política, economia, segurança, agronegócio e clima — do dia a dia de Campo Grande e do interior, direto e sem rodeio.</p>
      </section>

      <div className="container-custom pb-6">
        <TrendPanel trends={trends} />
      </div>

      <div className="container-custom pb-12">
        {hero && (
          <div className="grid lg:grid-cols-[2fr_1fr] gap-8">
            <NewsCard article={hero} variant="hero" />
            <div className="hidden rounded-[2rem] border border-white/5 bg-black/40 p-6 shadow-sm backdrop-blur lg:block">
              <p className="text-xs font-black uppercase tracking-[0.24em] text-accent-soil">Seleção editorial</p>
              <h2 className="mb-4 mt-2 font-display text-3xl font-black text-text-primary">Destaques</h2>
              <div className="grid gap-3">
                {secondary.map((a) => (
                  <NewsCard key={a.slug || a.title} article={a} variant="compact" />
                ))}
              </div>
            </div>
            {/* Mobile secondary */}
            <div className="grid gap-4 lg:hidden">
              {secondary.map((a) => (
                <NewsCard key={a.slug || a.title} article={a} variant="compact" />
              ))}
            </div>
          </div>
        )}

        {rest.length > 0 && (
          <>
            <h2 className="mt-16 mb-8 flex items-center gap-4 font-display text-3xl font-black text-text-primary">
              Últimas notícias
              {cat && <span className="text-base font-medium text-text-muted">— {cat}</span>}
              <span className="h-px flex-1 bg-black/10" />
            </h2>
            <div className="grid gap-7 sm:grid-cols-2 lg:grid-cols-4">
              {rest.map((a) => (
                <NewsCard key={a.slug || a.title} article={a} />
              ))}
            </div>
          </>
        )}

        {!loadError && list.length === 0 && (
          <div className="rounded-[2rem] glass-panel border-white/10 p-12 text-center text-text-muted shadow-lg">Nenhuma notícia encontrada. A Inteligência Artificial está escrevendo novas matérias neste instante...</div>
        )}

        {!loadError && <Pagination page={currentPage} totalPages={totalPages} base="/" />}

        {loadError && (
          <div className="rounded-[2rem] glass-panel border-red-500/20 p-12 text-center font-semibold text-red-600 shadow-lg">{loadError}</div>
        )}
      </div>
      </div>
    </div>
  );
}
