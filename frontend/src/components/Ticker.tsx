"use client";

import { useEffect, useState } from "react";

type Quote = { label: string; value: string; pct: number | null };

// Cotações REAIS — AwesomeAPI (moedas/BTC) + Banco Central (Selic).
// Sem dado fake: se a API falhar, mostra aviso honesto em vez de número inventado.
async function loadQuotes(): Promise<Quote[]> {
  const out: Quote[] = [];
  try {
    const r = await fetch("https://economia.awesomeapi.com.br/json/last/USD-BRL,EUR-BRL,BTC-BRL");
    if (r.ok) {
      const d = await r.json();
      const fmt = (v: string) => Number(v).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
      if (d.USDBRL) out.push({ label: "DÓLAR", value: fmt(d.USDBRL.bid), pct: Number(d.USDBRL.pctChange) || null });
      if (d.EURBRL) out.push({ label: "EURO", value: fmt(d.EURBRL.bid), pct: Number(d.EURBRL.pctChange) || null });
      if (d.BTCBRL) out.push({ label: "BITCOIN", value: fmt(d.BTCBRL.bid), pct: Number(d.BTCBRL.pctChange) || null });
    }
  } catch {}
  try {
    const r = await fetch("https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json");
    if (r.ok) {
      const d = await r.json();
      const v = Number(String(d?.[0]?.valor).replace(",", "."));
      if (Number.isFinite(v)) out.push({ label: "SELIC", value: `${v.toLocaleString("pt-BR")}% a.a.`, pct: null });
    }
  } catch {}
  return out;
}

export default function Ticker() {
  const [quotes, setQuotes] = useState<Quote[] | null>(null);

  useEffect(() => {
    let alive = true;
    const run = async () => {
      const q = await loadQuotes();
      if (alive) setQuotes(q);
    };
    run();
    const id = setInterval(run, 5 * 60 * 1000);
    return () => {
      alive = false;
      clearInterval(id);
    };
  }, []);

  if (quotes === null) {
    return (
      <div className="bg-[#e63946] text-white overflow-hidden">
        <div className="px-6 py-2 text-sm font-semibold whitespace-nowrap">• Carregando cotações do mercado…</div>
      </div>
    );
  }
  if (!quotes.length) {
    return (
      <div className="bg-[#e63946] text-white overflow-hidden">
        <div className="px-6 py-2 text-sm font-semibold whitespace-nowrap">• Cotações indisponíveis no momento</div>
      </div>
    );
  }
  const items = [...quotes, ...quotes];
  return (
    <div className="bg-[#e63946] text-white overflow-hidden">
      <div className="flex animate-[ticker_30s_linear_infinite] whitespace-nowrap">
        {items.map((q, i) => (
          <span key={i} className="px-6 py-2 text-sm font-semibold">
            • {q.label} {q.value}
            {q.pct !== null && (
              <span className={q.pct >= 0 ? "text-emerald-200" : "text-amber-200"}>
                {" "}{q.pct >= 0 ? "▲" : "▼"} {Math.abs(q.pct).toLocaleString("pt-BR")}%
              </span>
            )}
          </span>
        ))}
      </div>
      <style>{`@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}`}</style>
    </div>
  );
}
