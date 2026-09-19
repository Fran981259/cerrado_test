import Link from 'next/link';
import { getCategory } from '@/lib/categories';
import { getReporter } from '@/lib/reporters';
import { formatRelativeTime } from '@/lib/time';
import type { Article } from '@/lib/api';
import { ArticleImage } from './ArticleImage';

function hrefOf(article: Article): string {
  return article.slug ? `/noticia/${article.slug}` : article.url || '#';
}

function Byline({ article, className = '' }: { article: Article; className?: string }) {
  const reporter = getReporter(article.reporter_slug);
  return (
    <p className={`text-xs text-text-muted ${className}`}>
      <span className="font-bold text-text-primary">{reporter.name}</span>
      <span className="mx-1.5" aria-hidden="true">
        ·
      </span>
      {formatRelativeTime(article.published_at)}
    </p>
  );
}

function MainCard({ article }: { article: Article }) {
  const cat = getCategory(article.category);
  return (
    <Link
      href={hrefOf(article)}
      className="group relative block h-[480px] overflow-hidden rounded-lg bg-black"
      aria-label={`Manchete: ${article.title}`}
    >
      <ArticleImage
        article={article}
        sizes="(max-width: 768px) 100vw, 50vw"
        priority
        className="absolute inset-0 h-full w-full opacity-90 transition-transform duration-700 group-hover:scale-105"
        showBadge={false}
      />
      <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 flex flex-col p-6 sm:p-8">
        <span className="mb-3 w-fit rounded bg-accent-soil px-2.5 py-1 text-[10px] font-black uppercase tracking-wider text-white shadow-sm">
          {cat.label}
        </span>
        <h1 className="font-display text-3xl font-bold leading-[1.08] tracking-tight text-white transition-colors sm:text-4xl lg:text-[2.5rem]">
          {article.title}
        </h1>
        {article.summary && (
          <p className="mt-3 line-clamp-2 text-[15px] leading-relaxed text-white/80">
            {article.summary.replace(/\*\*/g, '')}
          </p>
        )}
        <div className="mt-4 text-xs text-white/70">
          <span className="font-bold text-white">{getReporter(article.reporter_slug).name}</span>
          <span className="mx-1.5" aria-hidden="true">
            ·
          </span>
          {formatRelativeTime(article.published_at)}
        </div>
      </div>
    </Link>
  );
}

function FeatureCard({ article }: { article: Article }) {
  return (
    <Link href={hrefOf(article)} className="group block" aria-label={`Em alta: ${article.title}`}>
      <ArticleImage
        article={article}
        sizes="(max-width: 768px) 100vw, 33vw"
        className="aspect-[4/3]"
      />
      <h2 className="mt-3 font-display text-xl font-bold leading-snug text-text-primary transition-colors group-hover:text-accent-soil">
        {article.title}
      </h2>
      <Byline article={article} className="mt-2.5" />
    </Link>
  );
}

function CompactCard({ article }: { article: Article }) {
  const cat = getCategory(article.category);
  return (
    <Link
      href={hrefOf(article)}
      className="group flex items-center gap-4"
      aria-label={`Teaser: ${article.title}`}
    >
      <ArticleImage
        article={article}
        showBadge={false}
        className="w-24 shrink-0 aspect-[4/3] sm:w-28"
        sizes="112px"
      />
      <div className="min-w-0">
        <p className="text-[10px] font-bold uppercase tracking-wider text-accent-soil">
          {cat.label}
        </p>
        <h3 className="mt-1 line-clamp-2 text-sm font-bold leading-snug text-text-primary transition-colors group-hover:text-accent-soil">
          {article.title}
        </h3>
        <p className="mt-1 text-[11px] text-text-muted">
          {formatRelativeTime(article.published_at)}
        </p>
      </div>
    </Link>
  );
}

export function HeroGrid({
  main,
  feature,
  rail,
}: {
  main?: Article;
  feature?: Article;
  rail: Article[];
}) {
  return (
    <section
      aria-label="Manchetes em destaque"
      className="container-editorial grid gap-x-8 gap-y-10 py-6 lg:grid-cols-12"
    >
      <div className="lg:col-span-6">
        {main ? (
          <MainCard article={main} />
        ) : (
          <EmptySlot label="Sem manchetes publicadas no momento." />
        )}
      </div>
      <div className="lg:col-span-3">
        {feature ? (
          <FeatureCard article={feature} />
        ) : (
          <EmptySlot label="Sem destaques secundários no momento." />
        )}
      </div>
      <div className="flex flex-col gap-5 border-t border-black/10 pt-5 lg:col-span-3 lg:border-l lg:border-t-0 lg:pl-8 lg:pt-0">
        {rail.length === 0 ? (
          <EmptySlot label="Sem destaques compactos no momento." />
        ) : (
          <>
            {rail.slice(0, 2).map((article) => (
              <CompactCard key={article.slug || article.title} article={article} />
            ))}
          </>
        )}
      </div>
    </section>
  );
}

function EmptySlot({ label }: { label: string }) {
  return (
    <p className="rounded border border-dashed border-black/15 bg-black/[0.02] p-6 text-sm text-text-muted">
      {label}
    </p>
  );
}
