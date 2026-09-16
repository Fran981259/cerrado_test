import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { REPORTERS, reporterInitials } from "@/lib/reporters";
import { fetchNewsResponse, fetchTrends } from "@/lib/api";
import { TrendPanel } from "@/components/TrendPanel";
import { Pagination } from "@/components/Pagination";
import { parsePage } from "@/lib/pagination";
import { NewsCard } from "@/components/NewsCard";

export const revalidate = 300;

export async function generateMetadata({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { page } = await searchParams;
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";
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
    },
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
    fetchNewsResponse({ reporterSlug: slug, limit: perPage, offset, sortBy: "trend" }),
    fetchTrends(5),
  ]);
  const mine = newsResult.news;
  const totalPages = Math.max(1, Math.ceil((newsResult.total || 0) / perPage));
  if (currentPage > totalPages) notFound();

  return (
    <div className="bg-[radial-gradient(circle_at_top_left,rgba(166,94,78,0.16),transparent_30rem),linear-gradient(180deg,#fdfbf7_0%,#f7f1e8_100%)] py-10">
      <div className="container-custom max-w-6xl">
        <Link href="/" className="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm font-black text-text-muted shadow-sm hover:text-accent-soil">← Voltar</Link>

        <div className="mt-6 overflow-hidden rounded-[2rem] border border-black/5 bg-white shadow-[0_28px_90px_rgba(45,41,38,0.12)]">
          <div className="bg-text-primary p-8 text-white sm:p-10">
            <div className="flex flex-col gap-6 sm:flex-row sm:items-end">
              <div className="flex h-28 w-28 shrink-0 items-center justify-center rounded-[2rem] bg-white font-display text-4xl font-black text-text-primary shadow-xl">
                {reporterInitials(r.name)}
              </div>
              <div>
                <p className="text-xs font-black uppercase tracking-[0.28em] text-white/55">{r.role}</p>
                <h1 className="mt-2 font-display text-5xl font-black leading-none tracking-tight sm:text-7xl">{r.name}</h1>
                <p className="mt-3 text-lg font-semibold text-white/78">{r.beat} • Portal Cerrado</p>
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
