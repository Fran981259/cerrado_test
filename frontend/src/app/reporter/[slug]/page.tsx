import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { REPORTERS, reporterInitials } from "@/lib/reporters";
import { fetchNews, fetchTrends } from "@/lib/api";
import { getCategory } from "@/lib/categories";
import { TrendPanel } from "@/components/TrendPanel";

export const revalidate = 300;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";
  const r = REPORTERS[slug];
  if (!r) return { title: "Repórter não encontrado" };
  return {
    title: `${r.name} — ${r.beat}`,
    description: r.bio,
    alternates: { canonical: `${base}/reporter/${slug}` },
    openGraph: {
      title: `${r.name} — ${r.beat}`,
      description: r.bio,
      url: `${base}/reporter/${slug}`,
      type: "profile",
    },
  };
}

export default async function ReporterPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const r = REPORTERS[slug];
  if (!r) notFound();

  const [all, trends] = await Promise.all([
    fetchNews({ limit: 100 }),
    fetchTrends(5),
  ]);
  const mine = all.filter((a) => a.reporter_slug === slug).slice(0, 9);

  return (
    <div className="container-custom py-8 max-w-6xl">
      <Link href="/" className="inline-flex items-center gap-2 text-sm font-bold text-zinc-600 hover:text-[#e63946]">← Voltar</Link>

      <div className="mt-6 flex flex-col sm:flex-row gap-6 rounded-2xl border border-zinc-100 bg-white p-6 shadow-sm">
        <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-full bg-[#e63946] text-3xl font-black text-white">
          {reporterInitials(r.name)}
        </div>
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-[#e63946]">{r.role}</p>
          <h1 className="mt-1 text-3xl font-black text-zinc-900">{r.name}</h1>
          <p className="mt-1 text-sm font-semibold text-zinc-600">{r.beat} — Portal Cerrado</p>
          <p className="mt-3 leading-relaxed text-zinc-700">{r.bio}</p>
          <p className="mt-3 text-sm text-zinc-500">🎓 Formação: {r.university} — {r.state}</p>
        </div>
      </div>

      <div className="mt-8">
        <TrendPanel trends={trends} title="Temas quentes agora" compact />
      </div>

      <h2 className="mt-10 text-xl font-extrabold text-zinc-900">Últimas de {r.name.split(" ")[0]}</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {mine.map((a) => (
          <Link key={a.slug || a.title} href={a.slug ? `/noticia/${a.slug}` : "#"} className="rounded-xl border border-zinc-100 bg-white p-4 shadow-sm hover:shadow-md">
            <span className="text-xs font-bold text-[#e63946]">{getCategory(a.category).label}</span>
            <p className="mt-2 line-clamp-3 text-sm font-bold leading-snug text-zinc-900">{a.title}</p>
          </Link>
        ))}
        {mine.length === 0 && <p className="text-sm text-zinc-500">Nenhuma matéria publicada ainda.</p>}
      </div>
    </div>
  );
}
