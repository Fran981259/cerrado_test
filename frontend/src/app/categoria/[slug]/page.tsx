import type { Metadata } from "next";
import Link from "next/link";
import { notFound, permanentRedirect } from "next/navigation";
import { fetchNewsResponse, fetchTrends } from "@/lib/api";
import { NewsCard } from "@/components/NewsCard";
import { CATEGORY_LIST, getCategory, categorySlug } from "@/lib/categories";
import { TrendPanel } from "@/components/TrendPanel";
import { Pagination } from "@/components/Pagination";
import { parsePage } from "@/lib/pagination";
import { Icon } from "@/components/Icon";

export const revalidate = 60;

export function generateStaticParams() {
  return CATEGORY_LIST.map(({ slug }) => ({ slug }));
}

export async function generateMetadata({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { page } = await searchParams;
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";
  const cat = getCategory(slug);
  const currentPage = parsePage(page);
  if (currentPage === null || !categorySlug(slug)) notFound();
  const canonical = `${base}/categoria/${slug}${currentPage > 1 ? `?page=${currentPage}` : ""}`;
  return {
    title: `${cat.label} | Portal Cerrado`,
    description: `Notícias de ${cat.label} em Mato Grosso do Sul`,
    alternates: { canonical },
    robots: currentPage > 1 ? { index: false, follow: true } : { index: true, follow: true },
    openGraph: {
      title: `${cat.label} | Portal Cerrado`,
      description: `Notícias de ${cat.label} em Mato Grosso do Sul`,
      url: canonical,
      type: "website",
    },
  };
}

export default async function CategoriaPage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> }) {
  const { slug } = await params;
  const { page } = await searchParams;
  const cat = getCategory(slug);
  const perPage = 24;
  const currentPage = parsePage(page);
  const canonicalSlug = categorySlug(slug);
  if (currentPage === null || !canonicalSlug) notFound();
  if (canonicalSlug !== slug) permanentRedirect(`/categoria/${canonicalSlug}${currentPage > 1 ? `?page=${currentPage}` : ""}`);
  const offset = (currentPage - 1) * perPage;
  const [newsResult, trends] = await Promise.all([
    fetchNewsResponse({ category: slug, limit: perPage, offset, sortBy: "trend" }),
    fetchTrends(5),
  ]);
  const articles = newsResult.news;
  const totalPages = Math.max(1, Math.ceil((newsResult.total || 0) / perPage));
  if (currentPage > totalPages) notFound();

  return (
    <div className="bg-canvas py-10 sm:py-14">
      <div className="container-editorial">
        <header className="border-b-2 border-charcoal pb-7">
          <span className="inline-flex items-center gap-2 text-xs font-black uppercase tracking-[0.22em] text-gold-deep"><Icon name={cat.iconClass} /> Editoria</span>
          <h1 className="mt-3 font-display text-5xl font-bold leading-none tracking-tight text-text-primary sm:text-7xl">{cat.label}</h1>
          <p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted">Acompanhe as principais atualizações desta editoria, com contexto regional e leitura direta.</p>
          <p className="mt-5 text-xs font-bold uppercase tracking-widest text-accent-soil">{newsResult.total} matérias publicadas</p>
        </header>

        <div className="my-8">
          <TrendPanel trends={trends} title="Temas em alta no portal" compact />
        </div>

        {articles.length === 0 ? (
          <div className="border-y border-black/10 bg-surface p-12 text-center text-text-muted">
            Nenhuma matéria em {cat.label} ainda.
            <Link href="/" className="mt-4 block font-black text-accent-soil">← Voltar para capa</Link>
          </div>
        ) : (
          <div className="grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
            {articles.map((a) => (
              <NewsCard key={a.slug || a.title} article={a} />
            ))}
          </div>
        )}

        <Pagination page={currentPage} totalPages={totalPages} base={`/categoria/${slug}`} />
      </div>
    </div>
  );
}
