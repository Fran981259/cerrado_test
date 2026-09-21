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
      className="group relative block h-[430px] overflow-hidden rounded-lg bg-black"
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
        <h1 className="font-display text-3xl font-bold leading-[1.08] tracking-tight text-white transition-colors sm:text-4xl lg:text-4xl">
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
    <Link href={hrefOf(article)} className="group block border-b border-black/10 pb-5 last:border-b-0 last:pb-0" aria-label={`Em alta: ${article.title}`}>
      <ArticleImage
        article={article}
        sizes="(max-width: 768px) 100vw, 25vw"
        className="aspect-[16/10] rounded-md"
      />
      <h2 className="mt-2.5 line-clamp-3 font-display text-xl font-bold leading-snug text-text-primary transition-colors group-hover:text-accent-soil">
        {article.title}
      </h2>
      <Byline article={article} className="mt-2" />
    </Link>
  );
}

function CompactCard({ article }: { article: Article }) {
  const cat = getCategory(article.category);
  return (
    <Link
      href={hrefOf(article)}
      className="group grid grid-cols-[7.25rem_minmax(0,1fr)] items-start gap-3 border-b border-black/10 pb-4 last:border-b-0 last:pb-0"
      aria-label={`Teaser: ${article.title}`}
    >
      <ArticleImage
        article={article}
        showBadge={false}
        className="aspect-[16/10] w-full rounded-sm"
        sizes="116px"
      />
      <div className="min-w-0">
        <p className="text-[10px] font-bold uppercase tracking-wider text-accent-soil">
          {cat.label}
        </p>
        <h3 className="mt-1 line-clamp-3 text-[15px] font-bold leading-snug text-text-primary transition-colors group-hover:text-accent-soil">
          {article.title}
        </h3>
        <p className="mt-1 text-[11px] text-text-muted">
          {formatRelativeTime(article.published_at)}
        </p>
      </div>
    </Link>
  );
}

function LatestCard({ article }: { article: Article }) {
  const cat = getCategory(article.category);
  return (
    <Link href={hrefOf(article)} className="group block" aria-label={`Notícia: ${article.title}`}>
      <ArticleImage article={article} showBadge={false} sizes="(max-width: 640px) 100vw, 25vw" className="aspect-[16/10] rounded-md" />
      <p className="mt-3 text-[10px] font-black uppercase tracking-[0.16em] text-accent-soil">{cat.label}</p>
      <h3 className="mt-1.5 line-clamp-3 font-display text-lg font-bold leading-tight text-text-primary transition-colors group-hover:text-accent-soil">
        {article.title}
      </h3>
      <Byline article={article} className="mt-2" />
    </Link>
  );
}

export function HeroGrid({
  main,
  side,
  rail,
  latest,
}: {
  main?: Article;
  side: Article[];
  rail: Article[];
  latest: Article[];
}) {
  const hasSide = side.length > 0;
  const hasRail = rail.length > 0;
  if (!main && !hasSide && !hasRail && latest.length === 0) return null;

  return (
    <section
      aria-label="Manchetes em destaque"
      className="container-editorial py-7 sm:py-9"
    >
      <div className="grid gap-x-6 gap-y-7 lg:grid-cols-12">
        {main && (
          <div className="lg:col-span-6">
            <MainCard article={main} />
          </div>
        )}
        {hasSide && (
          <div className="grid gap-5 sm:grid-cols-2 lg:col-span-3 lg:grid-cols-1">
            {side.slice(0, 2).map((article) => (
              <FeatureCard key={article.slug || article.title} article={article} />
            ))}
          </div>
        )}
        {hasRail && (
          <div className="flex flex-col gap-4 border-t border-black/10 pt-5 lg:col-span-3 lg:border-l lg:border-t-0 lg:pl-6 lg:pt-0">
            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-gold-deep">Mais recentes</p>
            {rail.slice(0, 3).map((article) => (
              <CompactCard key={article.slug || article.title} article={article} />
            ))}
          </div>
        )}
      </div>
      {latest.length > 0 && (
        <div className="mt-8 border-t border-black/10 pt-6">
          <div className="mb-5 flex items-end justify-between gap-4">
            <h2 className="font-display text-2xl font-bold text-text-primary">Mais notícias de Mato Grosso do Sul</h2>
            <span className="hidden text-xs font-semibold text-text-muted sm:block">Atualizações locais em todas as editorias</span>
          </div>
          <div className="grid gap-x-6 gap-y-7 sm:grid-cols-2 lg:grid-cols-4">
            {latest.slice(0, 4).map((article) => (
              <LatestCard key={article.slug || article.title} article={article} />
            ))}
          </div>
        </div>
      )}
    </section>
  );
}
