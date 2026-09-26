"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense } from "react";

type Sub = { label: string; slug: string };
type MenuItem = { label: string; href?: string; subs?: Sub[]; highlight?: boolean };

export const CAPITAL_MENU: MenuItem[] = [
  { label: "Política", href: "/categoria/politics" },
  { label: "Segurança e Justiça", href: "/categoria/security" },
  {
    label: "Economia & Agro",
    subs: [
      { label: "Economia", slug: "economy" },
      { label: "Agronegócio", slug: "agriculture" },
    ],
  },
  { label: "Saúde", href: "/categoria/health" },
  {
    label: "Ciência & Tech",
    subs: [
      { label: "Ciência", slug: "science" },
      { label: "Tecnologia", slug: "tech" },
    ],
  },
  {
    label: "Cotidiano",
    subs: [
      { label: "Educação", slug: "education" },
      { label: "Clima", slug: "clima" },
      { label: "Geral", slug: "general" },
    ],
  },
  {
    label: "Cultura",
    subs: [
      { label: "Cultura", slug: "culture" },
      { label: "Entretenimento", slug: "entertainment" },
    ],
  },
  { label: "Esportes", href: "/categoria/sports" },
];

const linkCls = (on: boolean, highlight: boolean = false) =>
  `relative px-2.5 py-1.5 text-[11px] font-black uppercase tracking-wider transition-colors whitespace-nowrap rounded ${
    on
      ? "bg-accent-soil text-white"
      : highlight
        ? "bg-charcoal text-white hover:bg-accent-soil"
        : "text-text-muted hover:bg-black/5 hover:text-text-primary"
  }`;

function DesktopLinks() {
  const path = usePathname();
  const active = path.startsWith("/categoria/") ? path.split("/")[2] : path === "/" ? null : "";
  return (
    <>
      <Link href="/" aria-current={active === null ? "page" : undefined} className={linkCls(active === null)}>
        Início
      </Link>
      {CAPITAL_MENU.map((item, idx) => {
        if (item.href) {
          const slug = item.href.split("/").pop() || "";
          const on = active === slug;
          return (
            <Link key={item.label} href={item.href} aria-current={on ? "page" : undefined} className={linkCls(on, item.highlight)}>
              {item.highlight && <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-gold" aria-hidden="true" />}
              {item.label}
            </Link>
          );
        }
        const subs = item.subs || [];
        const moreOn = subs.some((s) => s.slug === active);
        const alignRight = idx >= CAPITAL_MENU.length - 3;
        return (
          <div key={item.label} className="group relative">
            <button aria-haspopup="true" className={`${linkCls(moreOn)} inline-flex cursor-pointer items-center gap-1 bg-transparent`}>
              {item.label}
              <svg width="10" height="6" viewBox="0 0 10 6" className="transition-transform group-hover:rotate-180" aria-hidden="true">
                <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
              </svg>
            </button>
            <div className={`invisible absolute top-full z-50 w-64 translate-y-2 rounded-md border border-black/10 bg-surface p-2 opacity-0 shadow-[0_18px_50px_-16px_rgba(22,26,22,0.35)] transition-all group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:visible group-focus-within:translate-y-0 group-focus-within:opacity-100 ${alignRight ? "right-0" : "left-0"}`}>
              {subs.map((s) => {
                const on = active === s.slug;
                return (
                  <Link
                    key={s.label}
                    href={`/categoria/${s.slug}`}
                    aria-current={on ? "page" : undefined}
                    className={`block rounded px-3 py-2 text-[12px] font-bold uppercase tracking-wider transition-colors ${on ? "bg-accent-soil text-white" : "text-text-muted hover:bg-black/5 hover:text-text-primary"}`}
                  >
                    {s.label}
                  </Link>
                );
              })}
            </div>
          </div>
        );
      })}
    </>
  );
}

export function DesktopNav() {
  return (
    <nav className="hidden min-w-0 flex-1 items-center justify-between gap-0.5 lg:flex" aria-label="Editorias">
      <Suspense>
        <DesktopLinks />
      </Suspense>
    </nav>
  );
}
