import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { REPORTERS, reporterInitials } from "@/lib/reporters";
import { fetchNewsResponse, fetchTrends } from "@/lib/api";
import { TrendPanel } from "@/components/TrendPanel";
import { Pagination } from "@/components/Pagination";
import { parsePage } from "@/lib/pagination";
import { NewsCard } from "@/components/NewsCard";
import { DEFAULT_SOCIAL_IMAGE } from "@/lib/siteMetadata";
import { getPublicSiteUrl } from "@/lib/siteUrl";

export const revalidate = 300;

export async function generateMetadata({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { page } = await searchParams;
  const base = getPublicSiteUrl();
  const r = Object.hasOwn(REPORTERS, slug) ? REPORTERS[slug] : undefined;
  if (!r) return { title: "Repórter não encontrado" };
  const currentPage = parsePage(page);
  if (currentPage === null) notFound();
  const canonical = `${base}/reporter/${slug}${currentPage > 1 ? `?page=${currentPage}` : ""}`;
  return {
    title: `${r.name} — ${r.beat}`,
    description: r.bio,
    alternates: { canonical },
    robots: currentPage > 1 ? { index: false, follow: true } : { index: true, follow: true },
    openGraph: {
      title: `${r.name} — ${r.beat}`,
      description: r.bio,
      url: canonical,
      type: "profile",
      images: [DEFAULT_SOCIAL_IMAGE],
    },
    twitter: { card: "summary_large_image", images: [DEFAULT_SOCIAL_IMAGE] },
  };
}

export default async function ReporterPage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> }) {
  const { slug } = await params;
  const { page } = await searchParams;
  const r = Object.hasOwn(REPORTERS, slug) ? REPORTERS[slug] : undefined;
  if (!r) notFound();

  const perPage = 9;
  const currentPage = parsePage(page);
  if (currentPage === null) notFound();
  const offset = (currentPage - 1) * perPage;

  const [newsResult, trends] = await Promise.all([
    fetchNewsResponse({ reporterSlug: slug, region: "ms", limit: perPage, offset, sortBy: "trend" }),
    fetchTrends(5),
  ]);
  const mine = newsResult.news;
  const totalPages = Math.max(1, Math.ceil((newsResult.total || 0) / perPage));
  if (currentPage > totalPages) notFound();

  return (
    <div className="bg-canvas py-10 sm:py-14">
      <div className="container-editorial max-w-6xl">
        <Link href="/" className="inline-flex items-center gap-2 border-b border-accent-soil pb-1 text-sm font-bold text-accent-soil hover:text-gold-deep">← Voltar para a capa</Link>

        <div className="mt-6 border-y-2 border-charcoal bg-surface">
          <div className="p-8 sm:p-10">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-end">
              <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-full bg-accent-soil font-display text-3xl font-bold text-white">
                {reporterInitials(r.name)}
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-[0.22em] text-gold-deep">{r.role}</p>
                <h1 className="mt-2 font-display text-5xl font-bold leading-none tracking-tight text-text-primary sm:text-7xl">{r.name}</h1>
                <p className="mt-3 text-lg text-text-muted">{r.beat} • Portal Cerrado</p>
              </div>
            </div>
          </div>
          <div className="grid gap-6 p-8 md:grid-cols-[1fr_280px]">
            <p className="text-lg leading-relaxed text-text-primary">{r.bio}</p>
            <div className="rounded-2xl bg-canvas p-5 text-sm text-text-muted">
              <p className="font-black uppercase tracking-widest text-accent-soil">Credenciais</p>
              <p className="mt-3 font-semibold">Formação: {r.university}</p>
              <p className="mt-1 font-semibold">Base editorial: {r.state}</p>
              <p className="mt-1 font-semibold">Matérias: {newsResult.total}</p>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <TrendPanel trends={trends} title="Temas quentes agora" compact />
        </div>

        <h2 className="mt-12 flex items-center gap-4 font-display text-3xl font-black text-text-primary">
          Últimas de {r.name.split(" ")[0]}
          <span className="h-px flex-1 bg-black/10" />
        </h2>
        <div className="mt-6 grid gap-7 sm:grid-cols-2 lg:grid-cols-3">
          {mine.map((a) => (
            <NewsCard key={a.slug || a.title} article={a} />
          ))}
          {mine.length === 0 && <p className="rounded-2xl bg-white p-8 text-sm text-text-muted shadow-sm">Nenhuma matéria publicada ainda.</p>}
        </div>

        <Pagination page={currentPage} totalPages={totalPages} base={`/reporter/${slug}`} />
      </div>
    </div>
  );
}
