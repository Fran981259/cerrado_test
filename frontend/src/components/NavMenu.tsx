"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense } from "react";
import { CATEGORY_LIST } from "@/lib/categories";

// Taxonomia Capital News adaptada à paleta Cerrado — mantém slugs existentes, só rótulos mudam
// Paleta continua Cerrado (rounded-full, bg-white, accent-soil), funcionalidade vem do Capital
type Sub = { label: string; slug: string };
type MenuItem = { label: string; href?: string; subs?: Sub[] };

const CAPITAL_MENU: MenuItem[] = [
  {
    label: "Política e Poder",
    subs: [
      { label: "Política", slug: "politics" },
      { label: "Executivo", slug: "politics" },
      { label: "Judiciário", slug: "politics" },
      { label: "Legislativo", slug: "politics" },
      { label: "Tribunal de Contas", slug: "politics" },
    ],
  },
  {
    label: "Polícia e Justiça",
    subs: [
      { label: "Polícia", slug: "security" },
      { label: "Justiça", slug: "security" },
    ],
  },
  {
    label: "Cotidiano",
    subs: [
      { label: "Geral", slug: "general" },
      { label: "Ciência e Tecnologia", slug: "tech" },
      { label: "Educação", slug: "education" },
      { label: "Meio Ambiente", slug: "clima" },
      { label: "Saúde e Bem Estar", slug: "health" },
      { label: "Trânsito", slug: "general" },
      { label: "Loteria", slug: "general" },
    ],
  },
  { label: "Esporte", href: "/categoria/sports" },
  {
    label: "Economia e Agronegócio",
    subs: [
      { label: "Economia", slug: "economy" },
      { label: "Agronegócio", slug: "agriculture" },
    ],
  },
  { label: "Rural", href: "/categoria/agriculture" },
  { label: "Reportagem Especial", href: "/categoria/culture" },
  {
    label: "Oportunidades",
    subs: [
      { label: "Capacitação", slug: "education" },
      { label: "Concurso", slug: "education" },
      { label: "Trabalho e Renda", slug: "economy" },
    ],
  },
  {
    label: "Cultura e Entretenimento",
    subs: [
      { label: "Cinema", slug: "culture" },
      { label: "Cultura", slug: "culture" },
      { label: "Entretenimento", slug: "culture" },
    ],
  },
  {
    label: "Mais",
    subs: [
      { label: "Nacional", slug: "general" },
      { label: "Internacional", slug: "general" },
      { label: "Opinião", slug: "general" },
      { label: "Colunistas", slug: "general" },
      { label: "Capital Play", slug: "general" },
      { label: "Informe Publicitário", slug: "general" },
    ],
  },
];

// Compat: mantém PRIMARY/MORE/ALL para fallback, mas derivado do Capital
const PRIMARY_SLUGS = ["politics", "economy", "security", "sports", "clima", "tech"];
const PRIMARY = [
  { href: "/", label: "Início", cat: null as string | null },
  ...CATEGORY_LIST.filter((c) => PRIMARY_SLUGS.includes(c.slug)).map((c) => ({
    href: `/categoria/${c.slug}`,
    label: c.label,
    cat: c.slug as string | null,
  })),
];
const MORE = CATEGORY_LIST.filter((c) => c.slug !== "general" && !PRIMARY_SLUGS.includes(c.slug)).map((c) => ({ href: `/categoria/${c.slug}`, label: c.label, cat: c.slug as string | null }));
const ALL = [
  { href: "/", label: "Início", cat: null as string | null },
  ...CATEGORY_LIST.filter((c) => c.slug !== "general").map((c) => ({
    href: `/categoria/${c.slug}`,
    label: c.label,
    cat: c.slug as string | null,
  })),
];

const linkCls = (on: boolean) =>
  `relative rounded-full px-3 py-2 text-[12px] font-black uppercase tracking-wider transition-all whitespace-nowrap ${
    on ? "bg-white text-accent-soil shadow-sm ring-1 ring-black/5" : "text-text-muted hover:bg-white/70 hover:text-text-primary"
  }`;

function DesktopLinks() {
  const path = usePathname();
  const active = path.startsWith("/categoria/") ? path.split("/")[2] : path === "/" ? null : "";
  return (
    <>
      <Link href="/" aria-current={active === null ? "page" : undefined} className={linkCls(active === null)}>
        Início
      </Link>
      {CAPITAL_MENU.map((item) => {
        if (item.href) {
          const slug = item.href.split("/").pop() || "";
          const on = active === slug;
          return (
            <Link key={item.label} href={item.href} aria-current={on ? "page" : undefined} className={linkCls(on)}>
              {item.label}
            </Link>
          );
        }
        const subs = item.subs || [];
        const moreOn = subs.some((s) => s.slug === active);
        return (
          <div key={item.label} className="group relative">
            <button aria-haspopup="true" className={`${linkCls(moreOn)} inline-flex cursor-pointer items-center gap-1 bg-transparent`}>
              {item.label}
              <svg width="10" height="6" viewBox="0 0 10 6" className="transition-transform group-hover:rotate-180" aria-hidden="true">
                <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
              </svg>
            </button>
            <div className="invisible absolute left-0 top-full z-50 w-64 translate-y-2 rounded-2xl border border-black/5 bg-white p-2 opacity-0 shadow-[0_22px_70px_rgba(45,41,38,0.16)] transition-all group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:visible group-focus-within:translate-y-0 group-focus-within:opacity-100">
              {subs.map((s) => {
                const on = active === s.slug;
                return (
                  <Link
                    key={s.label}
                    href={`/categoria/${s.slug}`}
                    className={`block rounded-xl px-3 py-2 text-[12px] font-black uppercase tracking-wider transition-colors ${on ? "bg-canvas text-accent-soil" : "text-text-muted hover:bg-canvas hover:text-text-primary"}`}
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

function MobileLinks() {
  const path = usePathname();
  const active = path.startsWith("/categoria/") ? path.split("/")[2] : path === "/" ? null : "";
  // Mobile: mostra taxonomia Capital (funcionalidade) em scroll horizontal — paleta Cerrado mantida
  return (
    <>
      <Link
        href="/"
        aria-current={active === null ? "page" : undefined}
        className={`shrink-0 border-b-2 px-1 py-2 text-[12px] font-bold uppercase tracking-wider transition-colors ${active === null ? "border-accent-soil text-accent-soil" : "border-transparent text-text-muted"}`}
      >
        Início
      </Link>
      {CAPITAL_MENU.map((item) => {
        const href = item.href || (item.subs?.[0] ? `/categoria/${item.subs[0].slug}` : "/");
        const isSubActive = item.subs?.some((s) => s.slug === active) || false;
        const isDirectActive = item.href ? active === item.href.split("/").pop() : false;
        const on = isDirectActive || isSubActive;
        return (
          <Link
            key={"m-" + item.label}
            href={href}
            aria-current={on ? "page" : undefined}
            className={`shrink-0 border-b-2 px-1 py-2 text-[12px] font-bold uppercase tracking-wider transition-colors ${on ? "border-accent-soil text-accent-soil" : "border-transparent text-text-muted"}`}
          >
            {item.label}
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
    <div className="overflow-x-auto border-t border-black/5 bg-white/45 lg:hidden" aria-label="Editorias">
      <div className="flex gap-4 px-4">
        <Suspense>
          <MobileLinks />
        </Suspense>
      </div>
    </div>
  );
}
