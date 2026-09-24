import Link from "next/link";
import { getReporter } from "@/lib/reporters";
import { getCategory } from "@/lib/categories";
import { formatRelativeTime } from "@/lib/time";
import type { Article } from "@/lib/api";
import { SectionHeading } from "./SectionHeading";

function hrefOf(article: Article): string {
  return article.slug ? `/noticia/${article.slug}` : article.url || "#";
}

function PoderColumn({ article }: { article: Article }) {
  const category = getCategory(article.category);
  return (
    <div>
      <h3 className="flex items-center gap-2 border-b border-white/15 pb-2 text-[11px] font-black uppercase tracking-[0.2em] text-gold">
        <span className="h-1.5 w-1.5 rounded-full bg-gold" aria-hidden="true" />
        {category.label}
      </h3>
      <Link href={hrefOf(article)} className="group mt-3 block" aria-label={`${category.label}: ${article.title}`}>
        <span className="text-[11px] text-white/50">{formatRelativeTime(article.published_at)}</span>
        <h4 className="mt-1 font-display text-[17px] font-bold leading-snug text-white transition-colors group-hover:text-gold">{article.title}</h4>
        <span className="mt-1.5 block text-[11px] font-semibold text-white/60">{getReporter(article.reporter_slug).name}</span>
      </Link>
    </div>
  );
}

export function PoderModule({ articles }: { articles: Article[] }) {
  if (!articles.length) return null;

  return (
    <section aria-labelledby="poder-heading" className="bg-charcoal text-white">
      <div className="container-editorial py-7 sm:py-8">
        <SectionHeading eyebrow="Poder e eleições" title="Política que influencia Mato Grosso do Sul" id="poder-heading" dark />
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-white/60">Acompanhamento de política nacional, eleições e decisões com impacto no estado.</p>
        <div className="mt-6 grid gap-x-8 gap-y-7 border-t border-white/10 pt-6 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((article) => <PoderColumn key={article.slug || article.title} article={article} />)}
        </div>
      </div>
    </section>
  );
}
