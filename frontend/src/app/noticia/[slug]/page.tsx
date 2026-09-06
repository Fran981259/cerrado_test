import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchArticleBySlug, fetchNews } from "@/lib/api";
import type { Article } from "@/lib/api";
import { formatArticleContent, readingTimeMinutes } from "@/lib/formatArticle";
import { getCategory, PATTERN_IMAGES } from "@/lib/categories";
import { getReporter, reporterInitials } from "@/lib/reporters";
import Comments from "@/components/Comments";

export const dynamic = "force-dynamic";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  try {
    const article = await fetchArticleBySlug(slug);
    if (!article) return { title: "Notícia não encontrada" };
    return {
      title: article.title,
      description: article.summary || article.title,
      openGraph: { title: article.title, description: article.summary, type: "article" },
    };
  } catch {
    return { title: "Portal Cerrado" };
  }
}

export default async function NoticiaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let article: Article | null = null;
  try {
    article = await fetchArticleBySlug(slug);
  } catch {
    return <div className="container-custom py-16 text-center text-red-600 font-semibold">A API de noticias nao respondeu. O frontend depende do backend real para carregar a materia.</div>;
  }
  if (!article) notFound();

  const cat = getCategory(article.category);
  const reporter = getReporter(article.reporter_slug);
  const img = (article as unknown as { image_url?: string }).image_url || PATTERN_IMAGES[article.category] || PATTERN_IMAGES.general;

  let related: Article[] = [];
  let latest: Article[] = [];
  try {
    related = (await fetchNews({ category: article.category, limit: 6 })).filter((a) => a.slug !== slug).slice(0, 5);
    latest = (await fetchNews({ limit: 6 })).filter((a) => a.slug !== slug).slice(0, 5);
  } catch {
    related = [];
    latest = [];
  }
  const bodyHtml = formatArticleContent(article.content || "", article.summary || "", article.title || "");
  const minutes = readingTimeMinutes(article.content || article.summary || "");
  const reporterSlug = article.reporter_slug || "";

  return (
    <div className="container-custom py-8 max-w-6xl">
      <Link href="/" className="inline-flex items-center gap-2 text-sm font-bold text-zinc-600 hover:text-[#e63946]">← Voltar</Link>

      <div className="mt-6 grid gap-10 lg:grid-cols-[minmax(0,1fr)_320px]">
        <article className="min-w-0">
          <div>
            <span className="inline-block rounded-full px-3 py-1 text-xs font-bold text-white" style={{ background: cat.color }}>{cat.icon} {cat.label}</span>
            <h1 className="mt-4 text-3xl md:text-4xl font-black leading-tight tracking-tight text-zinc-900">{article.title}</h1>
            {article.summary && <p className="mt-4 border-l-4 border-[#e63946] pl-4 text-lg font-semibold italic leading-relaxed text-zinc-800">{article.summary.replace(/\*\*/g, "")}</p>}

            <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-zinc-500 border-y border-zinc-100 py-4">
              {reporterSlug ? (
                <Link href={`/reporter/${reporterSlug}`} className="font-semibold text-zinc-700 hover:text-[#e63946] hover:underline">✍️ {reporter.name}</Link>
              ) : (
                <span className="font-semibold text-zinc-700">✍️ {reporter.name}</span>
              )}
              <span>•</span>
              <span>{article.published_at ? new Date(article.published_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" }) : ""}</span>
              <span>•</span>
              <span>⏱️ {minutes} min de leitura</span>
              {article.sources?.[0] && (
                <>
                  <span>•</span>
                  <a href={article.sources[0]} target="_blank" rel="noopener noreferrer" className="text-[#e63946] font-bold hover:underline">Fonte original</a>
                </>
              )}
            </div>
          </div>

          <figure className="mt-8 overflow-hidden rounded-2xl bg-zinc-100">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={img} alt={article.title} className="w-full h-[420px] object-cover" />
            <figcaption className="bg-white px-4 py-2 text-xs text-zinc-500">Foto ilustrativa — Portal Cerrado</figcaption>
          </figure>

          <div className="mt-8 article-body">
            {bodyHtml ? (
              <div dangerouslySetInnerHTML={{ __html: bodyHtml }} />
            ) : (
              <>
                <p>{article.summary}</p>
                <p>
                  Esta matéria foi apurada com base em fonte pública e reescrita pela nossa equipe de repórteres digitais. Citamos a fonte original
                  e mantemos compromisso com correção e transparência.
                </p>
                <p>Conteúdo completo disponível na fonte original. Voltaremos com atualizações assim que houver novos desdobramentos.</p>
              </>
            )}
          </div>

          {article.tags && article.tags.length > 0 && (
            <div className="mt-8 flex flex-wrap gap-2">
              {article.tags.map((t) => (
                <span key={t} className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-semibold text-zinc-600">#{t}</span>
              ))}
            </div>
          )}

          {reporterSlug && (
            <Link href={`/reporter/${reporterSlug}`} className="mt-8 flex items-center gap-4 rounded-2xl border border-zinc-100 bg-white p-5 shadow-sm hover:shadow-md">              <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-[#e63946] text-lg font-black text-white">
                {reporterInitials(reporter.name)}
              </span>
              <span>
                <span className="block text-xs font-bold uppercase tracking-widest text-[#e63946]">{reporter.role || reporter.specialty}</span>
                <span className="block font-extrabold text-zinc-900">{reporter.name}, direto da redação</span>
                <span className="block text-sm text-zinc-500">Conheça o repórter →</span>
              </span>
            </Link>
          )}

          <Comments slug={article.slug || slug} title={article.title} />
        </article>

        <aside className="space-y-8">
          <section className="rounded-2xl border border-zinc-100 bg-white p-5 shadow-sm">
            <h3 className="font-extrabold text-zinc-900">🔥 Mais lidas</h3>
            <div className="mt-4 space-y-4">
              {latest.map((r, i) => (
                <Link key={r.slug || r.title} href={r.slug ? `/noticia/${r.slug}` : "#"} className="flex gap-3">
                  <span className="text-2xl font-black text-zinc-200">{i + 1}</span>
                  <span>
                    <span className="block text-[11px] font-bold uppercase tracking-wide text-[#e63946]">{getCategory(r.category).label}</span>
                    <span className="line-clamp-3 text-sm font-bold leading-snug text-zinc-900">{r.title}</span>
                  </span>
                </Link>
              ))}
            </div>
          </section>

          {related.length > 0 && (
            <section className="rounded-2xl border border-zinc-100 bg-white p-5 shadow-sm">
              <h3 className="font-extrabold text-zinc-900">📌 Do mesmo nicho</h3>
              <div className="mt-4 space-y-4">
                {related.map((r) => (
                  <Link key={r.slug || r.title} href={r.slug ? `/noticia/${r.slug}` : "#"} className="block">
                    <span className="block text-[11px] font-bold uppercase tracking-wide text-[#e63946]">{getCategory(r.category).label}</span>
                    <span className="line-clamp-3 text-sm font-bold leading-snug text-zinc-900">{r.title}</span>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </aside>
      </div>
    </div>
  );
}
