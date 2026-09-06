"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { CATEGORY_LIST } from "@/lib/categories";

// Hierarquia do menu: 6 principais + restante no dropdown "Editorias".
// Slugs seguem o frontend (tech/science) com aliases resolvidos no getCategory.
const PRIMARY_SLUGS = ["politics", "economy", "security", "sports", "clima", "tech"];

const PRIMARY = [
  { href: "/", label: "Início", cat: null as string | null },
  ...CATEGORY_LIST.filter((c) => PRIMARY_SLUGS.includes(c.slug)).map((c) => ({
    href: `/?cat=${c.slug}`,
    label: c.label,
    cat: c.slug as string | null,
  })),
];

const MORE = CATEGORY_LIST.filter(
  (c) => c.slug !== "general" && !PRIMARY_SLUGS.includes(c.slug)
).map((c) => ({ href: `/?cat=${c.slug}`, label: c.label, cat: c.slug as string | null }));

const ALL = [
  { href: "/", label: "Início", cat: null as string | null },
  ...CATEGORY_LIST.filter((c) => c.slug !== "general").map((c) => ({
    href: `/?cat=${c.slug}`,
    label: c.label,
    cat: c.slug as string | null,
  })),
];

const linkCls = (on: boolean) =>
  `relative px-2.5 py-2 text-[12px] font-bold uppercase tracking-wider transition-colors whitespace-nowrap after:absolute after:left-2.5 after:right-2.5 after:-bottom-0.5 after:h-0.5 after:origin-left after:scale-x-0 after:bg-[#e63946] after:transition-transform hover:after:scale-x-100 ${
    on ? "text-[#e63946] after:scale-x-100" : "text-zinc-600 hover:text-zinc-900"
  }`;

function DesktopLinks() {
  const active = useSearchParams().get("cat");
  const moreOn = MORE.some((n) => n.cat === active);
  return (
    <>
      {PRIMARY.map((n) => {
        const on = n.cat === null ? active === null : active === n.cat;
        return (
          <Link key={n.href + n.label} href={n.href} aria-current={on ? "page" : undefined} className={linkCls(on)}>
            {n.label}
          </Link>
        );
      })}
      <div className="group relative">
        <button
          aria-haspopup="true"
          className={`${linkCls(moreOn)} inline-flex cursor-pointer items-center gap-1 bg-transparent`}
        >
          Editorias
          <svg width="10" height="6" viewBox="0 0 10 6" className="transition-transform group-hover:rotate-180" aria-hidden="true">
            <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
          </svg>
        </button>
        <div className="invisible absolute right-0 top-full z-50 w-52 translate-y-1 rounded-xl border border-zinc-200 bg-white p-2 opacity-0 shadow-lg transition-all group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:visible group-focus-within:translate-y-0 group-focus-within:opacity-100">
          {MORE.map((n) => {
            const on = active === n.cat;
            return (
              <Link
                key={n.href}
                href={n.href}
                className={`block rounded-lg px-3 py-2 text-[12px] font-bold uppercase tracking-wider transition-colors ${
                  on ? "bg-red-50 text-[#e63946]" : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                }`}
              >
                {n.label}
              </Link>
            );
          })}
        </div>
      </div>
    </>
  );
}

function MobileLinks() {
  const active = useSearchParams().get("cat");
  return (
    <>
      {ALL.map((n) => {
        const on = n.cat === null ? active === null : active === n.cat;
        return (
          <Link
            key={"m-" + n.href + n.label}
            href={n.href}
            aria-current={on ? "page" : undefined}
            className={`shrink-0 border-b-2 px-1 py-2 text-[12px] font-bold uppercase tracking-wider transition-colors ${
              on ? "border-[#e63946] text-[#e63946]" : "border-transparent text-zinc-600"
            }`}
          >
            {n.label}
          </Link>
        );
      })}
    </>
  );
}

export function DesktopNav() {
  return (
    <nav className="hidden items-center gap-0.5 lg:flex" aria-label="Editorias">
      <Suspense>
        <DesktopLinks />
      </Suspense>
    </nav>
  );
}

export function MobileNav() {
  return (
    <div className="border-t border-zinc-200 overflow-x-auto lg:hidden" aria-label="Editorias">
      <div className="flex gap-4 px-4">
        <Suspense>
          <MobileLinks />
        </Suspense>
      </div>
    </div>
  );
}
