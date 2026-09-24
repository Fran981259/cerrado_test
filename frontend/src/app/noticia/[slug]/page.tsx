import type { Metadata } from 'next';
import Image from 'next/image';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { fetchArticleBySlug, fetchNewsResponse } from '@/lib/api';
import type { Article } from '@/lib/api';
import {
  cleanArticleText,
  formatArticleContent,
  formatArticleDate,
  readingTimeMinutes,
  serializeJsonLd,
} from '@/lib/formatArticle';
import { categorySlug, getCategory, PATTERN_IMAGES } from '@/lib/categories';
import { ArticleQuickGuide } from '@/components/article/ArticleQuickGuide';
import { ArticleShareActions } from '@/components/article/ArticleShareActions';
import { ArticleSidebar } from '@/components/article/ArticleSidebar';
import { getReporter, reporterInitials } from '@/lib/reporters';
import { REPORTERS } from '@/lib/reporters';
import { buildArticleJsonLd } from '@/lib/articleSeo';
import { Icon } from '@/components/Icon';
import { ScrollProgress } from '@/components/ScrollProgress';
import { getPublicSiteUrl } from '@/lib/siteUrl';

export const revalidate = 300;

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>;
}): Promise<Metadata> {
  const { slug } = await params;
  const base = getPublicSiteUrl();
  try {
    const article = await fetchArticleBySlug(slug);
    if (!article) return { title: 'Notícia não encontrada' };
    const image = article.image_url || PATTERN_IMAGES[article.category] || PATTERN_IMAGES.general;
    return {
      title: article.title,
      description: article.summary || article.title,
      alternates: { canonical: `${base}/noticia/${slug}` },
      openGraph: {
        title: article.title,
        description: article.summary,
        type: 'article',
        url: `${base}/noticia/${slug}`,
        images: [{ url: image, alt: article.title }],
      },
      twitter: {
        card: 'summary_large_image',
        title: article.title,
        description: article.summary || article.title,
        images: [{ url: image, alt: article.title }],
      },
    };
  } catch {
    return { title: 'Portal Cerrado' };
  }
}

export default async function NoticiaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let article: Article | null = null;
  try {
    article = await fetchArticleBySlug(slug);
  } catch {
    return (
      <div className="container-custom py-16 text-center text-red-600 font-semibold">
        A API de noticias nao respondeu. O frontend depende do backend real para carregar a materia.
      </div>
    );
  }
  if (!article) notFound();

  const cat = getCategory(article.category);
  const reporter = getReporter(article.reporter_slug);
  const img =
    (article as unknown as { image_url?: string }).image_url ||
    PATTERN_IMAGES[article.category] ||
    PATTERN_IMAGES.general;

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
  const bodyHtml = formatArticleContent(
    article.content || '',
    article.summary || '',
    article.title || ''
  );
  const minutes = readingTimeMinutes(article.content || article.summary || '');
  const reporterSlug = article.reporter_slug || '';
  const base = getPublicSiteUrl();
  const canonicalUrl = `${base}/noticia/${article.slug || slug}`;
  const lead = cleanArticleText(article.summary || article.content).slice(0, 360);
  const primarySource = article.sources?.[0];
  const authorUrl = Object.hasOwn(REPORTERS, reporterSlug)
    ? `${base}/reporter/${reporterSlug}`
    : undefined;
  const jsonLd = buildArticleJsonLd({
    article,
    canonicalUrl,
    categoryLabel: cat.label,
    imageUrl: img,
    reporterName: reporter.name,
    reporterUrl: authorUrl,
  });

  return (
    <div className="bg-[radial-gradient(circle_at_top_left,rgba(200,138,44,0.1),transparent_40rem),linear-gradient(180deg,var(--color-canvas)_0%,#ffffff_100%)] pb-16">
      <ScrollProgress />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: serializeJsonLd(jsonLd) }}
      />
      <section className="relative isolate min-h-[560px] overflow-hidden bg-canvas text-text-primary">
        <Image
          src={img}
          alt=""
          fill
          priority
          sizes="100vw"
          className="object-cover opacity-15 mix-blend-multiply"
        />
        <div className="absolute inset-0 bg-[linear-gradient(90deg,var(--color-canvas)_0%,transparent_100%)]" />
        <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-surface to-transparent" />
        <div className="container-custom relative z-10 flex min-h-[560px] flex-col justify-end pb-16 pt-8">
          <Link
            href="/"
            className="mb-auto inline-flex w-fit items-center gap-2 rounded-full border border-black/10 bg-black/5 px-4 py-2 text-sm font-bold text-text-primary backdrop-blur transition hover:bg-black/10"
          >
            ← Voltar para capa
          </Link>
          <div className="max-w-4xl">
            <span
              className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-xs font-black uppercase tracking-[0.22em] text-white shadow-sm"
              style={{ background: cat.color }}
            >
              <Icon name={cat.iconClass} /> {cat.label}
            </span>
            <h1 className="mt-6 text-balance font-display text-4xl font-black leading-[0.98] tracking-tight sm:text-5xl lg:text-7xl">
              {article.title}
            </h1>
            {lead && (
              <p className="mt-6 max-w-3xl border-l-4 border-accent-soil pl-5 text-lg font-medium leading-relaxed text-text-muted sm:text-xl">
                {lead}
              </p>
            )}
          </div>
        </div>
      </section>

      <div className="container-custom -mt-10 grid gap-8 lg:grid-cols-[minmax(0,1fr)_360px]">
        <article className="relative z-10 min-w-0 overflow-hidden rounded-[2rem] border border-black/5 bg-white shadow-[0_28px_90px_rgba(45,41,38,0.12)]">
          <div className="grid gap-4 border-b border-zinc-100 bg-white/95 p-5 sm:grid-cols-[1fr_auto] sm:items-center sm:p-7">
            <div className="flex items-center gap-4">
              <Link
                href={reporterSlug ? `/reporter/${reporterSlug}` : '#'}
                className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-text-primary text-lg font-black text-white shadow-inner"
              >
                {reporterInitials(reporter.name)}
              </Link>
              <div>
                <p className="text-xs font-black uppercase tracking-[0.18em] text-accent-soil">
                  Reportagem
                </p>
                <Link
                  href={reporterSlug ? `/reporter/${reporterSlug}` : '#'}
                  className="font-display text-xl font-bold text-text-primary hover:text-accent-soil"
                >
                  {reporter.name}
                </Link>
                <p className="text-sm text-text-muted">{reporter.role || reporter.specialty}</p>
              </div>
            </div>
            <dl className="grid grid-cols-2 gap-3 text-sm sm:flex sm:flex-wrap sm:justify-end">
              <div className="rounded-2xl bg-canvas px-4 py-3">
                <dt className="text-[10px] font-black uppercase tracking-widest text-text-muted">
                  Publicado
                </dt>
                <dd className="mt-1 font-bold text-text-primary">
                  {formatArticleDate(article.published_at)}
                </dd>
              </div>
              <div className="rounded-2xl bg-canvas px-4 py-3">
                <dt className="text-[10px] font-black uppercase tracking-widest text-text-muted">
                  Leitura
                </dt>
                <dd className="mt-1 font-bold text-text-primary">{minutes} min</dd>
              </div>
            </dl>
          </div>

          <div className="mx-5 mt-6 lg:hidden sm:mx-7">
            <ArticleQuickGuide
              categoryLabel={cat.label}
              heading="Em resumo"
              minutes={minutes}
              reporterName={reporter.name}
              source={primarySource}
            />
          </div>

          <figure className="mx-5 mt-6 overflow-hidden rounded-[1.5rem] bg-zinc-100 sm:mx-7">
            <div className="relative h-[260px] sm:h-[380px]">
              <Image
                src={img}
                alt={article.title}
                fill
                sizes="(min-width: 1024px) 760px, 100vw"
                className="object-cover"
              />
            </div>
            <figcaption className="bg-canvas px-4 py-3 text-xs font-medium text-text-muted">
              {primarySource
                ? `Imagem: ${primarySource.name || article.source || 'Fonte original'}`
                : 'Imagem ilustrativa selecionada pela redação do Portal Cerrado.'}
            </figcaption>
          </figure>

          <div className="article-body article-body-premium mx-auto px-5 py-8 sm:px-7 sm:py-10">
            {bodyHtml ? (
              <div dangerouslySetInnerHTML={{ __html: bodyHtml }} />
            ) : (
              <>
                <p>{article.summary}</p>
                <p>
                  Esta matéria foi produzida por nossa equipe de redação, com base em apuração
                  rigorosa de fontes e fatos. Citamos a fonte original e mantemos compromisso com a
                  correção e transparência.
                </p>
                <p>
                  Conteúdo completo disponível na fonte original. Voltaremos com atualizações assim
                  que houver novos desdobramentos.
                </p>
              </>
            )}
          </div>

          {article.tags && article.tags.length > 0 && (
            <div className="mx-auto flex max-w-[72ch] flex-wrap gap-2 px-5 pb-8 sm:px-7">
              {article.tags.map((t) => (
                <span
                  key={t}
                  className="rounded-full border border-zinc-200 bg-canvas px-3 py-1 text-xs font-bold uppercase tracking-wide text-text-muted"
                >
                  #{categorySlug(t) ? getCategory(t).label : t}
                </span>
              ))}
            </div>
          )}

          <div className="mx-5 mb-8 sm:mx-7">
            <ArticleShareActions title={article.title} url={canonicalUrl} />
          </div>

          {reporterSlug && (
            <Link
              href={`/reporter/${reporterSlug}`}
              className="mx-5 mb-8 flex items-center gap-4 rounded-2xl border border-zinc-100 bg-text-primary p-5 text-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-xl sm:mx-7"
            >
              <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-white text-lg font-black text-text-primary">
                {reporterInitials(reporter.name)}
              </span>
              <span>
                <span className="block text-xs font-bold uppercase tracking-widest text-white/60">
                  {reporter.role || reporter.specialty}
                </span>
                <span className="block font-display text-xl font-extrabold">
                  {reporter.name}, direto da redação
                </span>
                <span className="block text-sm text-white/70">Conheça o perfil do repórter →</span>
              </span>
            </Link>
          )}
        </article>

        <ArticleSidebar
          categoryLabel={cat.label}
          latestArticles={latest}
          minutes={minutes}
          relatedArticles={related}
          reporterName={reporter.name}
          source={primarySource}
        />
      </div>
    </div>
  );
}
