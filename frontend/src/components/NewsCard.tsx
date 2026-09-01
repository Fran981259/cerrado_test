import Link from "next/link";
import { getCategory, PATTERN_IMAGES } from "@/lib/categories";
import { getReporter } from "@/lib/reporters";
import type { Article } from "@/lib/api";

function formatDate(d?: string) {
  if (!d) return "";
  try {
    return new Date(d).toLocaleDateString("pt-BR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
  } catch {
    return d.slice(0, 10);
  }
}

export function NewsCard({ article, variant = "default" }: { article: Article; variant?: "hero" | "default" | "compact" }) {
  const cat = getCategory(article.category);
  const reporter = getReporter(article.reporter_slug);
  const img = (article as unknown as { image_url?: string }).image_url || PATTERN_IMAGES[article.category] || PATTERN_IMAGES.general;
  const href = article.slug ? `/noticia/${article.slug}` : article.url || "#";
  const isExternal = !article.slug && !!article.url;

  if (variant === "hero") {
    return (
      <article className="group relative overflow-hidden rounded-lg bg-white border border-zinc-200">
        <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
          <div className="relative h-[380px] sm:h-[420px] overflow-hidden">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={img} alt={article.title} className="h-full w-full object-cover group-hover:scale-[1.03] transition-transform duration-500" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
            <span className="absolute left-4 top-4 rounded px-2 py-0.5 text-xs font-bold text-white bg-accent-leaf">
              {cat.icon} {cat.label}
            </span>
            <div className="absolute bottom-0 p-6 text-white">
              <h2 className="text-3xl sm:text-4xl font-display font-bold leading-tight line-clamp-3">{article.title}</h2>
              {article.summary && <p className="mt-3 text-sm opacity-90 line-clamp-2 max-w-3xl">{article.summary}</p>}
              <div className="mt-4 flex items-center gap-2 text-xs opacity-90">
                <span className="font-bold border-r border-white/30 pr-2">{reporter.name}</span>
                <span>{formatDate(article.published_at)}</span>
              </div>
            </div>
          </div>
        </Link>
      </article>
    );
  }

  if (variant === "compact") {
    return (
      <article className="group flex gap-4 border-b border-zinc-200 py-4 last:border-0">
        <div className="h-20 w-28 shrink-0 overflow-hidden bg-zinc-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={img} alt={article.title} className="h-full w-full object-cover group-hover:scale-105 transition-transform" />
        </div>
        <div className="min-w-0 flex-1">
          <span className="text-[10px] font-bold text-accent-leaf uppercase tracking-wider">{cat.label}</span>
          <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
            <h3 className="mt-0.5 line-clamp-2 text-base font-display font-bold leading-snug text-text-primary group-hover:text-accent-soil">{article.title}</h3>
          </Link>
        </div>
      </article>
    );
  }

  return (
    <article className="group flex flex-col border border-zinc-200 bg-white">
      <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
        <div className="relative h-48 overflow-hidden bg-zinc-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={img} alt={article.title} className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <span className="absolute left-3 top-3 rounded px-2 py-0.5 text-xs font-bold text-white bg-accent-leaf">
            {cat.icon} {cat.label}
          </span>
        </div>
      </Link>
      <div className="flex flex-1 flex-col p-4">
        <Link href={href} target={isExternal ? "_blank" : undefined}>
          <h3 className="line-clamp-3 text-lg font-display font-bold leading-tight text-text-primary group-hover:text-accent-soil">{article.title}</h3>
        </Link>
        {article.summary && <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-text-muted">{article.summary}</p>}
        <div className="mt-auto pt-4 flex items-center justify-between text-xs text-text-muted">
          <span className="font-bold">{reporter.name}</span>
          <span>{formatDate(article.published_at)}</span>
        </div>
      </div>
    </article>
  );
}
