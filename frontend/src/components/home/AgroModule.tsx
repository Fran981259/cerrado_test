import Link from "next/link";
import { Suspense } from "react";
import { getReporter } from "@/lib/reporters";
import { formatRelativeTime } from "@/lib/time";
import type { Article } from "@/lib/api";
import { ArticleImage } from "./ArticleImage";
import { MarketPanel } from "@/components/markets/MarketPanel";
import { SectionHeading } from "./SectionHeading";

function hrefOf(article: Article): string {
  return article.slug ? `/noticia/${article.slug}` : article.url || "#";
}

function AgroFeature({ article }: { article: Article }) {
  const reporter = getReporter(article.reporter_slug);
  return (
    <Link href={hrefOf(article)} className="group block">
      <div className="grid gap-5 sm:grid-cols-[2fr_3fr] sm:items-stretch">
        <ArticleImage article={article} sizes="(max-width: 640px) 100vw, 40vw" className="aspect-[16/10] sm:aspect-auto sm:h-full" />
        <div className="flex flex-col justify-center py-1">
          <span className="text-[10px] font-bold uppercase tracking-wider text-gold-deep">{formatRelativeTime(article.published_at)}</span>
          <h3 className="mt-2 font-display text-2xl font-bold leading-tight text-text-primary transition-colors group-hover:text-accent-soil">{article.title}</h3>
          {article.summary && <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-text-muted">{article.summary.replace(/\*\*/g, "")}</p>}
          <p className="mt-3 text-xs font-bold text-text-muted">{reporter.name}</p>
        </div>
      </div>
    </Link>
  );
}

function AgroSupport({ article }: { article: Article }) {
  return (
    <Link href={hrefOf(article)} className="group block border-t border-black/10 pt-4">
      <span className="text-[10px] font-bold uppercase tracking-wider text-gold-deep">{formatRelativeTime(article.published_at)}</span>
      <h4 className="mt-1.5 line-clamp-2 font-display text-lg font-bold leading-tight text-text-primary transition-colors group-hover:text-accent-soil">{article.title}</h4>
      <p className="mt-1.5 text-[11px] font-semibold text-text-muted">{getReporter(article.reporter_slug).name}</p>
    </Link>
  );
}

export function AgroModule({ articles }: { articles: Article[] }) {
  const feature = articles[0];
  const support = articles.slice(1, 3);

  return (
    <section aria-labelledby="agro-heading" className="container-editorial py-8">
      <SectionHeading eyebrow="Cerrado Agro" title="Agro, campo e negócios rurais" id="agro-heading" href="/categoria/agriculture" linkLabel="ver agronegócio" />
      <div className="mt-6 grid gap-10 lg:grid-cols-12">
        <div className="lg:col-span-8">
          {feature ? (
            <AgroFeature article={feature} />
          ) : (
            <p className="rounded border border-dashed border-black/15 bg-black/[0.02] p-6 text-sm text-text-muted">Sem cobertura de agronegócio no momento.</p>
          )}
          {support.length > 0 && (
            <div className="mt-8 grid gap-x-8 gap-y-6 sm:grid-cols-2">
              {support.map((article) => (
                <AgroSupport key={article.slug || article.title} article={article} />
              ))}
            </div>
          )}
        </div>
        <div className="lg:col-span-4">
          <Suspense
            fallback={
              <div className="rounded-lg border border-black/10 bg-surface p-5 shadow-sm" role="status" aria-label="Carregando cotações">
                <div className="h-4 w-40 animate-pulse rounded bg-black/10" />
                <div className="mt-4 space-y-3">
                  {[0, 1, 2, 3, 4].map((i) => (
                    <div key={i} className="flex justify-between">
                      <div className="h-3 w-24 rounded bg-black/10" />
                      <div className="h-3 w-16 rounded bg-black/10" />
                    </div>
                  ))}
                </div>
              </div>
            }
          >
            <MarketPanel />
          </Suspense>
        </div>
      </div>
    </section>
  );
}