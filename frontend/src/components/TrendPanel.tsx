import Link from "next/link";
import { getCategory } from "@/lib/categories";
import type { TrendSignal } from "@/lib/api";
import { Icon } from "@/components/Icon";

type Props = {
  trends: TrendSignal[];
  title?: string;
  compact?: boolean;
};

export function TrendPanel({ trends, title = "Em alta agora", compact = false }: Props) {
  if (!trends.length) return null;

  const visible = trends.slice(0, compact ? 4 : 5);

  return (
    <section className="rounded-[1.75rem] border border-black/5 bg-white/90 p-5 shadow-[0_18px_50px_rgba(45,41,38,0.08)] backdrop-blur">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-sm font-black uppercase tracking-[0.22em] text-accent-soil">{title}</h2>
        <span className="hidden text-xs font-semibold text-text-muted sm:inline">Tendências em tempo real</span>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {visible.map((trend) => {
          const cat = getCategory(trend.category || trend.topic);
          const href = trend.category ? `/categoria/${trend.category}` : "/";

          return (
            <Link
              key={`${trend.topic}-${trend.category}`}
              href={href}
              className="inline-flex items-center gap-2 rounded-full border border-black/5 bg-canvas px-3 py-1.5 text-sm font-bold text-text-primary transition hover:-translate-y-0.5 hover:bg-text-primary hover:text-white"
            >
              <Icon name={cat.iconClass} />
              <span>{cat.label}</span>
              <span className="rounded-full bg-white/70 px-2 text-xs text-text-muted">{trend.article_count}</span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
