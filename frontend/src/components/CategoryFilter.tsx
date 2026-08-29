"use client";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { CATEGORY_LIST } from "@/lib/categories";

export default function CategoryFilter() {
  const params = useSearchParams();
  const active = params.get("cat");

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin">
      <Link
        href="/"
        className={`shrink-0 rounded-full px-4 py-2 text-sm font-bold border transition-colors ${!active ? "bg-[#1a1a2e] text-white border-[#1a1a2e]" : "bg-white text-zinc-700 border-zinc-200 hover:border-zinc-300"}`}
      >
        Todas
      </Link>
      {CATEGORY_LIST.map((c) => {
        const isActive = active === c.slug;
        return (
          <Link
            key={c.slug}
            href={`/?cat=${c.slug}`}
            className={`shrink-0 rounded-full px-4 py-2 text-sm font-bold border transition-colors ${isActive ? "text-white border-transparent" : "bg-white text-zinc-700 border-zinc-200 hover:border-zinc-300"}`}
            style={isActive ? { background: c.color } : undefined}
          >
            {c.icon} {c.label}
          </Link>
        );
      })}
    </div>
  );
}
