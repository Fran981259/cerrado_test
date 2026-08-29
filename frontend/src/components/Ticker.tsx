import type { Article } from "@/lib/api";

export default function Ticker({ articles }: { articles: Article[] }) {
  if (!articles.length) return null;
  const items = [...articles.slice(0, 8), ...articles.slice(0, 8)];
  return (
    <div className="bg-[#e63946] text-white overflow-hidden">
      <div className="flex animate-[ticker_30s_linear_infinite] whitespace-nowrap">
        {items.map((a, i) => (
          <span key={i} className="px-6 py-2 text-sm font-semibold">• {a.title}</span>
        ))}
      </div>
      <style>{`@keyframes ticker{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}`}</style>
    </div>
  );
}
