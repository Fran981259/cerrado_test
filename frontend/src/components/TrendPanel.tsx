import Link from "next/link";
import { getCategory } from "@/lib/categories";
import type { TrendSignal } from "@/lib/api";

type Props = {
  trends: TrendSignal[];
  title?: string;
  compact?: boolean;
};

export function TrendPanel({ trends, title = "Em alta agora", compact = false }: Props) {
  if (!trends.length) return null;

  const visible = trends.slice(0, compact ? 4 : 5);

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-sm font-black uppercase tracking-[0.2em] text-zinc-500">{title}</h2>
        <span className="text-xs font-semibold text-zinc-400">Atualizado pelo ML editorial</span>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {visible.map((trend) => {
          const cat = getCategory(trend.category || trend.topic);
          const href = trend.category ? `/categoria/${trend.category}` : "/";

          return (
            <Link
              key={`${trend.topic}-${trend.category}`}
              href={href}
              className="inline-flex items-center gap-2 rounded-full bg-zinc-100 px-3 py-1.5 text-sm font-semibold text-zinc-800 transition-colors hover:bg-zinc-200"
            >
              <span>{cat.icon}</span>
              <span>{cat.label}</span>
              <span className="text-xs text-zinc-500">{trend.article_count}</span>
            </Link>
          );
        })}
      </div>
    </section>
  );
}
