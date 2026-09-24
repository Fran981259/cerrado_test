import Link from "next/link";
import type { Article } from "@/lib/api";
import { getCategory } from "@/lib/categories";
import { ArticleQuickGuide } from "./ArticleQuickGuide";

type ArticleSidebarProps = {
  categoryLabel: string;
  latestArticles: Article[];
  minutes: number;
  relatedArticles: Article[];
  reporterName: string;
  source?: { name?: string; url: string };
};

/** Renders related reading material alongside an article on large screens. */
export function ArticleSidebar({
  categoryLabel,
  latestArticles,
  minutes,
  relatedArticles,
  reporterName,
  source,
}: ArticleSidebarProps) {
  return (
    <aside className="relative z-10 space-y-6 lg:sticky lg:top-6 lg:self-start">
      <div className="hidden lg:block">
        <ArticleQuickGuide
          categoryLabel={categoryLabel}
          heading="Antes de ler"
          minutes={minutes}
          reporterName={reporterName}
          source={source}
        />
      </div>

      <section className="rounded-3xl border border-black/5 bg-white p-6">
        <h3 className="font-display text-xl font-black text-text-primary">Mais lidas</h3>
        <div className="mt-4 space-y-4">
          {latestArticles.map((article, index) => (
            <Link
              key={article.slug || article.title}
              href={article.slug ? `/noticia/${article.slug}` : "#"}
              className="group flex gap-4 rounded-2xl p-2 transition hover:bg-canvas"
            >
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-canvas font-display text-lg font-black text-accent-soil">
                {index + 1}
              </span>
              <span>
                <span className="block text-[11px] font-black uppercase tracking-wide text-accent-soil">
                  {getCategory(article.category).label}
                </span>
                <span className="line-clamp-3 text-sm font-bold leading-snug text-text-primary group-hover:text-accent-soil">
                  {article.title}
                </span>
              </span>
            </Link>
          ))}
        </div>
      </section>

      {relatedArticles.length > 0 && (
        <section className="rounded-3xl border border-black/5 bg-white p-6">
          <h3 className="font-display text-xl font-black text-text-primary">Do mesmo tema</h3>
          <div className="mt-4 space-y-4">
            {relatedArticles.map((article) => (
              <Link
                key={article.slug || article.title}
                href={article.slug ? `/noticia/${article.slug}` : "#"}
                className="group block rounded-2xl border border-zinc-100 p-4 transition hover:border-accent-soil/30 hover:bg-canvas"
              >
                <span className="block text-[11px] font-black uppercase tracking-wide text-accent-soil">
                  {getCategory(article.category).label}
                </span>
                <span className="line-clamp-3 text-sm font-bold leading-snug text-text-primary group-hover:text-accent-soil">
                  {article.title}
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}
    </aside>
  );
}
