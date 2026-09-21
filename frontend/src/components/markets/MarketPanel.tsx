import Link from "next/link";
import { getMarketFeed } from "@/lib/markets";
import { formatMarketTime } from "@/lib/time";

function ChangePct({ direction, pct }: { direction: string | null; pct: number | null }) {
  if (pct === null || !direction) return <span className="text-[11px] text-text-muted">sem variação</span>;
  const arrow = direction === "up" ? "▲" : direction === "down" ? "▼" : "·";
  const color = direction === "up" ? "text-emerald-700" : direction === "down" ? "text-red-700" : "text-text-muted";
  return (
    <span className={`text-xs font-bold tabular-nums ${color}`} aria-label={`Variação de ${pct}%`}>
      {arrow} {Math.abs(pct).toLocaleString("pt-BR")}%
    </span>
  );
}

export async function MarketPanel() {
  const feed = await getMarketFeed();
  const availableItems = feed.items.filter((item) => item.status === "ok");
  const sources = Array.from(new Set(availableItems.map((item) => item.source)));
  const updated = availableItems
    .map((item) => item.updatedAt)
    .filter(Boolean)
    .sort()
    .at(-1);

  if (!availableItems.length) return null;

  return (
    <aside className="flex flex-col rounded-lg border border-black/10 bg-surface p-5 shadow-sm" aria-labelledby="mercado-cotacoes-heading">
      <div className="flex items-baseline justify-between gap-3 border-b-2 border-accent-soil pb-2">
        <div>
          <p className="eyebrow">Mercado & Cotações</p>
          <h3 id="mercado-cotacoes-heading" className="mt-1 font-display text-2xl font-bold text-text-primary">Agro e mercados</h3>
        </div>
      </div>

      <ul className="mt-4 divide-y divide-black/8">
        {availableItems.map((item) => (
          <li key={item.id} className="py-3">
            {item.status === "ok" ? (
              <div className="flex items-center justify-between gap-3">
                <div className="min-w-0">
                  <span className="block text-sm font-bold text-text-primary">{item.label}</span>
                  <span className="block truncate text-[11px] text-text-muted">{item.sublabel}</span>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-0.5">
                  <span className="text-base font-bold tabular-nums text-text-primary">{item.value}</span>
                  <ChangePct direction={item.direction} pct={item.changePct} />
                </div>
              </div>
            ) : null}
          </li>
        ))}
      </ul>

      <div className="mt-auto border-t border-black/8 pt-3 text-[10px] leading-relaxed text-text-muted">
        {feed.degraded && (
          <p className="mb-1 font-semibold text-amber-700">Exibimos somente cotações verificadas disponíveis no momento.</p>
        )}
        <p>
          Fonte: {sources.join(" · ")}
          {updated ? ` · atualizado ${formatMarketTime(updated)}` : ""}.{" "}
          <Link href="/api/markets" className="font-semibold text-accent-soil underline decoration-gold decoration-2 underline-offset-2 hover:text-gold-deep">
            dados brutos
          </Link>
        </p>
      </div>
    </aside>
  );
}
