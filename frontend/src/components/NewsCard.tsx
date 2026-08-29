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
      <article className="group relative overflow-hidden rounded-2xl bg-white shadow-sm hover:shadow-lg transition-all">
        <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
          <div className="relative h-[380px] sm:h-[420px] overflow-hidden">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={img} alt={article.title} className="h-full w-full object-cover group-hover:scale-[1.03] transition-transform duration-500" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/10 to-transparent" />
            <span className="absolute left-4 top-4 rounded-md px-3 py-1 text-xs font-bold text-white" style={{ background: cat.color }}>
              {cat.icon} {cat.label}
            </span>
            <div className="absolute bottom-0 p-6 text-white">
              <h2 className="text-2xl sm:text-3xl font-extrabold leading-tight line-clamp-3">{article.title}</h2>
              {article.summary && <p className="mt-3 text-sm opacity-90 line-clamp-2 max-w-3xl">{article.summary}</p>}
              <div className="mt-4 flex items-center gap-3 text-xs opacity-80">
                <span>✍️ {reporter.name}</span>
                <span>•</span>
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
      <article className="group flex gap-3 rounded-xl bg-white p-3 shadow-sm hover:shadow-md transition-shadow">
        <div className="h-20 w-28 shrink-0 overflow-hidden rounded-lg bg-zinc-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={img} alt={article.title} className="h-full w-full object-cover group-hover:scale-105 transition-transform" />
        </div>
        <div className="min-w-0 flex-1">
          <span className="inline-block rounded px-2 py-0.5 text-[10px] font-bold text-white" style={{ background: cat.color }}>{cat.label}</span>
          <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
            <h3 className="mt-1 line-clamp-2 text-sm font-bold leading-snug text-zinc-900 group-hover:text-[#e63946]">{article.title}</h3>
          </Link>
          <span className="text-[11px] text-zinc-500">{formatDate(article.published_at)}</span>
        </div>
      </article>
    );
  }

  return (
    <article className="group overflow-hidden rounded-2xl bg-white shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all flex flex-col">
      <Link href={href} target={isExternal ? "_blank" : undefined} className="block">
        <div className="relative h-48 overflow-hidden bg-zinc-100">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={img} alt={article.title} className="h-full w-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <span className="absolute left-3 top-3 rounded-md px-2.5 py-1 text-xs font-bold text-white shadow" style={{ background: cat.color }}>
            {cat.icon} {cat.label}
          </span>
        </div>
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <Link href={href} target={isExternal ? "_blank" : undefined}>
          <h3 className="line-clamp-2 text-[15px] font-extrabold leading-snug text-zinc-900 group-hover:text-[#e63946]">{article.title}</h3>
        </Link>
        {article.summary && <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-zinc-600">{article.summary}</p>}
        <div className="mt-4 flex items-center justify-between text-xs text-zinc-500 border-t border-zinc-100 pt-3">
          <span className="font-medium">✍️ {reporter.name}</span>
          <span>{formatDate(article.published_at)}</span>
        </div>
      </div>
    </article>
  );
}
