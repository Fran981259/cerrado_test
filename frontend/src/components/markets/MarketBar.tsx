import Link from "next/link";
import { getMarketFeed } from "@/lib/markets";
import { formatMarketTime } from "@/lib/time";

function pctClass(direction: string): string {
  if (direction === "up") return "text-emerald-200";
  if (direction === "down") return "text-orange-200";
  return "text-white/70";
}

function DirectionArrow({ direction, pct, label }: { direction: string; pct: number; label: string }) {
  if (direction === "up") {
    return <span aria-label={`${label}, alta de ${pct}%`} title={`${pct}%`} className={`inline-flex items-center gap-0.5 text-[11px] font-bold tabular-nums ${pctClass("up")}`}><span aria-hidden="true">▲</span>{pct}%</span>;
  }
  if (direction === "down") {
    return <span aria-label={`${label}, queda de ${pct}%`} title={`${pct}%`} className={`inline-flex items-center gap-0.5 text-[11px] font-bold tabular-nums ${pctClass("down")}`}><span aria-hidden="true">▼</span>{pct}%</span>;
  }
  return <span className="text-[11px] font-semibold text-white/65">estável</span>;
}

export async function MarketBar() {
  const feed = await getMarketFeed();
  const availableItems = feed.items.filter((item) => item.status === "ok");

  // A permanent strip of failures harms the masthead more than it informs.
  // The market module returns only when there is at least one verified quote.
  if (!availableItems.length) return null;

  return (
    <div className="sticky top-0 z-40 bg-accent-soil text-white shadow-[0_2px_12px_rgba(22,26,22,0.25)]" role="region" aria-label="Commodities e cotações agro">
      <div className="container-editorial flex items-center">
        <div className="hidden items-center gap-2 border-r border-white/20 py-3 pr-5 sm:flex" aria-hidden="true">
          <span className="h-2 w-2 rounded-full bg-gold" />
          <span className="text-[10px] font-black uppercase tracking-[0.2em]">Commodities &amp; Cotações Agro</span>
        </div>
        <div className="no-scrollbar flex flex-1 items-stretch overflow-x-auto snap-x">
          {availableItems.map((item) => (
            <Link
              key={item.id}
              href={item.sourceHref}
              target="_blank"
              rel="noopener noreferrer"
              title={`${item.label} — ${item.source}. Atualizado: ${formatMarketTime(item.updatedAt) || "não informado"}`}
              className="flex shrink-0 snap-start flex-col justify-center border-l border-white/15 px-4 py-2.5 min-w-[128px] outline-offset-[-3px] transition-colors hover:bg-white/10"
            >
              <span className="text-[10px] font-bold uppercase tracking-wider text-white/70">
                {item.label}
                <span className="ml-1 hidden font-medium normal-case tracking-normal text-white/55 lg:inline">{item.sublabel}</span>
              </span>
              {item.status === "ok" ? (
                <span className="mt-0.5 flex items-center gap-2">
                  <span className="text-[13px] font-bold tabular-nums leading-none">{item.value}</span>
                  {item.changePct !== null && item.direction ? <DirectionArrow direction={item.direction} pct={item.changePct} label={item.label} /> : <span className="text-[11px] text-white/60">sem variação</span>}
                </span>
              ) : (
                <span className="mt-0.5 flex items-center gap-1.5 text-[11px] font-semibold text-amber-200">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-300" aria-hidden="true" />
                  indisponível
                </span>
              )}
            </Link>
          ))}
        </div>
        <div className="hidden shrink-0 items-center pl-4 lg:flex" aria-hidden="true">
          <span className="text-[10px] leading-tight text-white/55">
            Fonte: {Array.from(new Set(availableItems.map((item) => item.source))).join(" · ")}
            {feed.degraded ? <span className="block text-amber-200">· parcialmente indisponível</span> : null}
          </span>
        </div>
      </div>
    </div>
  );
}
