import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchArticleBySlug, fetchNewsResponse } from "@/lib/api";
import type { Article } from "@/lib/api";
import { formatArticleContent, readingTimeMinutes, serializeJsonLd } from "@/lib/formatArticle";
import { getCategory, PATTERN_IMAGES } from "@/lib/categories";
import { getReporter, reporterInitials } from "@/lib/reporters";
import Comments from "@/components/Comments";
import { Icon } from "@/components/Icon";
import { ScrollProgress } from "@/components/ScrollProgress";

export const revalidate = 300;

function formatDate(value?: string) {
  if (!value) return "";
  return new Date(value).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function cleanText(value?: string) {
  return (value || "").replace(/[#*_>`]/g, "").replace(/\s+/g, " ").trim();
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";
  try {
    const article = await fetchArticleBySlug(slug);
    if (!article) return { title: "Notícia não encontrada" };
    return {
      title: article.title,
      description: article.summary || article.title,
      alternates: { canonical: `${base}/noticia/${slug}` },
      openGraph: {
        title: article.title,
        description: article.summary,
        type: "article",
        url: `${base}/noticia/${slug}`,
      },
      twitter: { card: "summary_large_image", title: article.title, description: article.summary || article.title },
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
    const [relatedResult, latestResult] = await Promise.all([
      fetchNewsResponse({ category: article.category, limit: 6 }),
      fetchNewsResponse({ limit: 6 }),
    ]);
    related = relatedResult.news.filter((a) => a.slug !== slug).slice(0, 5);
    latest = latestResult.news.filter((a) => a.slug !== slug).slice(0, 5);
  } catch {
    related = [];
    latest = [];
  }
  const bodyHtml = formatArticleContent(article.content || "", article.summary || "", article.title || "");
  const minutes = readingTimeMinutes(article.content || article.summary || "");
  const reporterSlug = article.reporter_slug || "";
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";
  const canonicalUrl = `${base}/noticia/${article.slug || slug}`;
  const updatedAt = (article as { updated_at?: string }).updated_at;
  const lead = cleanText(article.summary || article.content).slice(0, 360);
  const primarySource = article.sources?.[0];
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: article.title,
    description: article.summary || article.title,
    datePublished: article.published_at || article.created_at || undefined,
    dateModified: updatedAt || article.published_at || article.created_at || undefined,
    author: reporter ? { "@type": "Person", name: reporter.name } : undefined,
    publisher: { "@type": "Organization", name: "Portal Cerrado" },
    mainEntityOfPage: canonicalUrl,
    image: img,
    url: canonicalUrl,
  };

  return (
    <main className="bg-[radial-gradient(circle_at_top_left,rgba(59,130,246,0.12),transparent_40rem),linear-gradient(180deg,#09090b_0%,#18181b_100%)] pb-16">
      <ScrollProgress />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: serializeJsonLd(jsonLd) }} />
      <section className="relative isolate min-h-[560px] overflow-hidden bg-zinc-950 text-white">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={img} alt="" referrerPolicy="no-referrer" className="absolute inset-0 h-full w-full object-cover opacity-55" />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(20,16,12,0.92)_0%,rgba(20,16,12,0.66)_48%,rgba(20,16,12,0.22)_100%)]" />
        <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-[#09090b] to-transparent" />
        <div className="container-custom relative z-10 flex min-h-[560px] flex-col justify-end pb-16 pt-8">
          <Link href="/" className="mb-auto inline-flex w-fit items-center gap-2 rounded-full border border-white/20 bg-white/10 px-4 py-2 text-sm font-bold text-white/90 backdrop-blur transition hover:bg-white/20">← Voltar para capa</Link>
          <div className="max-w-4xl">
            <span className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-xs font-black uppercase tracking-[0.22em] text-white shadow-lg" style={{ background: cat.color }}><Icon name={cat.iconClass} /> {cat.label}</span>
            <h1 className="mt-6 text-balance font-display text-4xl font-black leading-[0.98] tracking-tight sm:text-5xl lg:text-7xl">{article.title}</h1>
            {lead && <p className="mt-6 max-w-3xl border-l-4 border-white/70 pl-5 text-lg font-medium leading-relaxed text-white/88 sm:text-xl">{lead}</p>}
          </div>
        </div>
      </section>

      <div className="container-custom -mt-10 grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
        <article className="relative z-10 min-w-0 overflow-hidden rounded-[2rem] border border-black/5 bg-white shadow-[0_28px_90px_rgba(45,41,38,0.12)]">
          <div className="grid gap-4 border-b border-zinc-100 bg-white/95 p-5 sm:grid-cols-[1fr_auto] sm:items-center sm:p-7">
            <div className="flex items-center gap-4">
              <Link href={reporterSlug ? `/reporter/${reporterSlug}` : "#"} className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-text-primary text-lg font-black text-white shadow-inner">
                {reporterInitials(reporter.name)}
              </Link>
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-accent-soil">Reportagem</p>
                <Link href={reporterSlug ? `/reporter/${reporterSlug}` : "#"} className="font-display text-xl font-bold text-text-primary hover:text-accent-soil">{reporter.name}</Link>
                <p className="text-sm text-text-muted">{reporter.role || reporter.specialty}</p>
              </div>
            </div>
            <dl className="grid grid-cols-2 gap-3 text-sm sm:flex sm:flex-wrap sm:justify-end">
              <div className="rounded-2xl bg-canvas px-4 py-3">
                <dt className="text-[10px] font-black uppercase tracking-widest text-text-muted">Publicado</dt>
                <dd className="mt-1 font-bold text-text-primary">{formatDate(article.published_at)}</dd>
              </div>
              <div className="rounded-2xl bg-canvas px-4 py-3">
                <dt className="text-[10px] font-black uppercase tracking-widest text-text-muted">Leitura</dt>
                <dd className="mt-1 font-bold text-text-primary">{minutes} min</dd>
              </div>
            </dl>
          </div>

          <figure className="mx-5 mt-6 overflow-hidden rounded-[1.5rem] bg-zinc-100 sm:mx-7">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={img} alt={article.title} referrerPolicy="no-referrer" className="h-[260px] w-full object-cover sm:h-[380px]" />
            <figcaption className="bg-canvas px-4 py-3 text-xs font-medium text-text-muted">
              {primarySource ? `Imagem: ${primarySource.name || article.source || "Fonte original"}` : "Imagem ilustrativa selecionada pela redação do Portal Cerrado."}
            </figcaption>
          </figure>

          <div className="article-body article-body-premium mx-auto px-5 py-8 sm:px-7 sm:py-10">
            {bodyHtml ? (
              <div dangerouslySetInnerHTML={{ __html: bodyHtml }} />
            ) : (
              <>
                <p>{article.summary}</p>
                <p>Esta matéria foi produzida por nossa equipe de redação, com base em apuração rigorosa de fontes e fatos. Citamos a fonte original e mantemos compromisso com a correção e transparência.</p>
                <p>Conteúdo completo disponível na fonte original. Voltaremos com atualizações assim que houver novos desdobramentos.</p>
              </>
            )}
          </div>

          {article.tags && article.tags.length > 0 && (
            <div className="mx-auto flex max-w-[72ch] flex-wrap gap-2 px-5 pb-8 sm:px-7">
              {article.tags.map((t) => (
                <span key={t} className="rounded-full border border-zinc-200 bg-canvas px-3 py-1 text-xs font-bold uppercase tracking-wide text-text-muted">#{t}</span>
              ))}
            </div>
          )}

          {reporterSlug && (
            <Link href={`/reporter/${reporterSlug}`} className="mx-5 mb-8 flex items-center gap-4 rounded-2xl border border-zinc-100 bg-text-primary p-5 text-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-xl sm:mx-7">
              <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-white text-lg font-black text-text-primary">
                {reporterInitials(reporter.name)}
              </span>
              <span>
                <span className="block text-xs font-bold uppercase tracking-widest text-white/60">{reporter.role || reporter.specialty}</span>
                <span className="block font-display text-xl font-extrabold">{reporter.name}, direto da redação</span>
                <span className="block text-sm text-white/70">Conheça o perfil do repórter →</span>
              </span>
            </Link>
          )}

          <div className="border-t border-zinc-100 bg-canvas/70 px-5 py-8 sm:px-7">
            <Comments slug={article.slug || slug} title={article.title} />
          </div>
        </article>

        <aside className="relative z-10 space-y-6 lg:sticky lg:top-6 lg:self-start">
          <section className="rounded-[1.75rem] border border-black/5 bg-white p-6 shadow-[0_22px_70px_rgba(45,41,38,0.10)]">
            <p className="text-xs font-black uppercase tracking-[0.24em] text-accent-soil">Guia rápido</p>
            <h2 className="mt-2 font-display text-2xl font-black text-text-primary">Antes de ler</h2>
            <div className="mt-5 grid gap-3 text-sm">
              <div className="flex items-center justify-between rounded-2xl bg-canvas px-4 py-3"><span className="text-text-muted">Categoria</span><strong>{cat.label}</strong></div>
              <div className="flex items-center justify-between rounded-2xl bg-canvas px-4 py-3"><span className="text-text-muted">Tempo</span><strong>{minutes} min</strong></div>
              <div className="flex items-center justify-between rounded-2xl bg-canvas px-4 py-3"><span className="text-text-muted">Repórter</span><strong>{reporter.name}</strong></div>
            </div>
            {primarySource && (
              <a href={primarySource.url} target="_blank" rel="noopener noreferrer" className="mt-5 flex items-center justify-between rounded-2xl bg-accent-soil px-4 py-3 text-sm font-black text-white transition hover:bg-text-primary">
                <span>Fonte original</span>
                <span aria-hidden="true">↗</span>
              </a>
            )}
          </section>

          <section className="rounded-[1.75rem] border border-black/5 bg-white p-6 shadow-sm">
            <h3 className="font-display text-xl font-black text-text-primary">Mais lidas</h3>
            <div className="mt-4 space-y-4">
              {latest.map((r, i) => (
                <Link key={r.slug || r.title} href={r.slug ? `/noticia/${r.slug}` : "#"} className="group flex gap-4 rounded-2xl p-2 transition hover:bg-canvas">
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-canvas font-display text-lg font-black text-accent-soil">{i + 1}</span>
                  <span>
                    <span className="block text-[11px] font-black uppercase tracking-wide text-accent-soil">{getCategory(r.category).label}</span>
                    <span className="line-clamp-3 text-sm font-bold leading-snug text-text-primary group-hover:text-accent-soil">{r.title}</span>
                  </span>
                </Link>
              ))}
            </div>
          </section>

          {related.length > 0 && (
            <section className="rounded-[1.75rem] border border-black/5 bg-white p-6 shadow-sm">
              <h3 className="font-display text-xl font-black text-text-primary">Do mesmo tema</h3>
              <div className="mt-4 space-y-4">
                {related.map((r) => (
                  <Link key={r.slug || r.title} href={r.slug ? `/noticia/${r.slug}` : "#"} className="group block rounded-2xl border border-zinc-100 p-4 transition hover:border-accent-soil/30 hover:bg-canvas">
                    <span className="block text-[11px] font-black uppercase tracking-wide text-accent-soil">{getCategory(r.category).label}</span>
                    <span className="line-clamp-3 text-sm font-bold leading-snug text-text-primary group-hover:text-accent-soil">{r.title}</span>
                  </Link>
                ))}
              </div>
            </section>
          )}
        </aside>
      </div>
    </main>
  );
}
