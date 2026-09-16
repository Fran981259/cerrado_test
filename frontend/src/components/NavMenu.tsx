"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense } from "react";

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
      { label: "Investigação", slug: "security" },
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

const linkCls = (on: boolean) =>
  `relative rounded-full px-2.5 py-1.5 text-[11px] font-black uppercase tracking-wider transition-all whitespace-nowrap ${
    on ? "bg-white/10 text-accent-soil shadow-sm ring-1 ring-white/10" : "text-text-muted hover:bg-white/10 hover:text-text-primary"
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
            <Link key={item.label} href={item.href} aria-current={on ? "page" : undefined} className={linkCls(on)}>
              {item.label}
            </Link>
          );
        }
        const subs = item.subs || [];
        const moreOn = subs.some((s) => s.slug === active);
        const alignRight = idx >= CAPITAL_MENU.length - 3; // últimos 3 não estouram à direita
        return (
          <div key={item.label} className="group relative">
            <button aria-haspopup="true" className={`${linkCls(moreOn)} inline-flex cursor-pointer items-center gap-1 bg-transparent`}>
              {item.label}
              <svg width="10" height="6" viewBox="0 0 10 6" className="transition-transform group-hover:rotate-180" aria-hidden="true">
                <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="1.5" fill="none" strokeLinecap="round" />
              </svg>
            </button>
            <div className={`invisible absolute top-full z-50 w-64 translate-y-2 rounded-2xl glass-panel p-2 opacity-0 shadow-[0_22px_70px_rgba(0,0,0,0.5)] transition-all group-hover:visible group-hover:translate-y-0 group-hover:opacity-100 group-focus-within:visible group-focus-within:translate-y-0 group-focus-within:opacity-100 ${alignRight ? "right-0" : "left-0"}`}>
              {subs.map((s) => {
                const on = active === s.slug;
                return (
                  <Link
                    key={s.label}
                    href={`/categoria/${s.slug}`}
                    className={`block rounded-xl px-3 py-2 text-[12px] font-black uppercase tracking-wider transition-colors ${on ? "bg-white/10 text-accent-soil" : "text-text-muted hover:bg-white/5 hover:text-text-primary"}`}
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
    <nav className="hidden min-w-0 flex-1 items-center gap-0.5 overflow-x-auto scrollbar-none lg:flex [&::-webkit-scrollbar]:hidden" aria-label="Editorias" style={{ scrollbarWidth: "none" }}>
      <Suspense>
        <DesktopLinks />
      </Suspense>
    </nav>
  );
}

export function MobileNav() {
  return (
    <div className="overflow-x-auto border-t border-white/10 bg-black/20 lg:hidden" aria-label="Editorias">
      <div className="flex gap-4 px-4">
        <Suspense>
          <MobileLinks />
        </Suspense>
      </div>
    </div>
  );
}
