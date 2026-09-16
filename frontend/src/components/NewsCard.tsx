import Link from "next/link";
import { getCategory, PATTERN_IMAGES } from "@/lib/categories";
import { getReporter } from "@/lib/reporters";
import type { Article } from "@/lib/api";
import { Icon } from "@/components/Icon";

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
      <article className="group relative overflow-hidden rounded-[2rem] border border-black/5 bg-white shadow-[0_28px_90px_rgba(45,41,38,0.14)] news-card-hover">
        <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
          <div className="relative h-[440px] overflow-hidden sm:h-[520px]">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={img} alt={article.title} className="img-zoom h-full w-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/88 via-black/35 to-black/5" />
            <span className="absolute left-5 top-5 rounded-full px-3 py-1.5 text-xs font-black uppercase tracking-wider text-white bg-accent-leaf shadow-lg">
              <Icon name={cat.iconClass} /> {cat.label}
            </span>
            <div className="absolute bottom-0 max-w-4xl p-6 text-white sm:p-8">
              <h2 className="line-clamp-3 text-4xl font-display font-black leading-[0.98] tracking-tight sm:text-6xl">{article.title}</h2>
              {article.summary && <p className="mt-4 line-clamp-2 max-w-3xl text-base font-medium leading-relaxed text-white/88">{article.summary.replace(/\*\*/g, "")}</p>}
              <div className="mt-5 flex flex-wrap items-center gap-3 text-xs font-bold uppercase tracking-wider text-white/80">
                <span>{reporter.name}</span>
                <span className="h-1 w-1 rounded-full bg-white/50" />
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
      <article className="group flex gap-4 rounded-2xl p-2 transition hover:bg-white hover:shadow-sm">
        <div className="h-24 w-32 shrink-0 overflow-hidden rounded-xl bg-zinc-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={img} alt={article.title} className="h-full w-full object-cover group-hover:scale-105 transition-transform" />
        </div>
        <div className="min-w-0 flex-1">
          <span className="text-[10px] font-black text-accent-leaf uppercase tracking-[0.18em]">{cat.label}</span>
          <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
            <h3 className="mt-1 line-clamp-2 text-base font-display font-black leading-snug text-text-primary group-hover:text-accent-soil">{article.title}</h3>
          </Link>
        </div>
      </article>
    );
  }

  return (
    <article className="group flex flex-col overflow-hidden rounded-[1.65rem] border border-black/5 bg-white shadow-sm news-card-hover">
      <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
        <div className="relative h-52 overflow-hidden bg-zinc-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={img} alt={article.title} className="img-zoom h-full w-full object-cover" />
          <span className="absolute left-3 top-3 rounded-full px-3 py-1 text-[11px] font-black uppercase tracking-wider text-white bg-accent-leaf shadow-lg">
            <Icon name={cat.iconClass} /> {cat.label}
          </span>
        </div>
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <Link href={href} target={isExternal ? "_blank" : undefined}>
          <h3 className="line-clamp-3 text-xl font-display font-black leading-tight text-text-primary group-hover:text-accent-soil">{article.title}</h3>
        </Link>
        {article.summary && <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-text-muted">{article.summary.replace(/\*\*/g, "")}</p>}
        <div className="mt-auto flex items-center justify-between border-t border-zinc-100 pt-4 text-xs font-semibold text-text-muted">
          <span className="font-bold">{reporter.name}</span>
          <span>{formatDate(article.published_at)}</span>
        </div>
      </div>
    </article>
  );
}
