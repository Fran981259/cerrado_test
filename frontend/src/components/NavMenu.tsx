"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense, useState } from "react";

// Taxonomia Capital News adaptada à paleta Cerrado — mantém slugs existentes, só rótulos mudam
// Paleta continua Cerrado (rounded-full, bg-white, accent-soil), funcionalidade vem do Capital
type Sub = { label: string; slug: string };
type MenuItem = { label: string; href?: string; subs?: Sub[]; highlight?: boolean };

const CAPITAL_MENU: MenuItem[] = [
  { label: "Política", href: "/categoria/politics" },
  { label: "Policial", href: "/categoria/security" },
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
  { label: "Internacional", href: "/categoria/world", highlight: true },
];

const linkCls = (on: boolean, highlight: boolean = false) =>
  `relative px-2.5 py-1.5 text-[11px] font-black uppercase tracking-wider transition-all whitespace-nowrap rounded-full ${
    on
      ? "bg-accent-leaf text-white shadow-sm ring-1 ring-white/5"
      : highlight
        ? "bg-white text-black shadow-sm hover:bg-accent-soil hover:text-white"
        : "text-text-muted hover:bg-white/10 hover:text-white"
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
              {item.highlight && <span className="mr-1.5 inline-block h-1.5 w-1.5 rounded-full bg-accent-soil animate-pulse" aria-hidden="true" />}
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
                    className={`block rounded-xl px-3 py-2 text-[12px] font-black uppercase tracking-wider transition-colors ${on ? "bg-slate-100 text-accent-leaf" : "text-text-muted hover:bg-slate-50 hover:text-text-primary"}`}
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

function MobileLinks({ onClose }: { onClose: () => void }) {
  const path = usePathname();
  const active = path.startsWith("/categoria/") ? path.split("/")[2] : path === "/" ? null : "";
  const [expanded, setExpanded] = useState<string | null>(null);

  const toggle = (label: string) => setExpanded(expanded === label ? null : label);

  return (
    <div className="flex flex-col p-6 gap-3">
      <Link
        href="/"
        onClick={onClose}
        className={`block py-3 text-2xl font-black tracking-wide transition-colors ${active === null ? "text-accent-leaf" : "text-white/80"}`}
      >
        Início
      </Link>
      {CAPITAL_MENU.map((item) => {
        const isSubActive = item.subs?.some((s) => s.slug === active) || false;
        const isDirectActive = item.href ? active === item.href.split("/").pop() : false;
        const on = isDirectActive || isSubActive;
        const isExpanded = expanded === item.label;

        if (item.subs) {
          return (
            <div key={"m-" + item.label} className="flex flex-col">
              <button
                onClick={() => toggle(item.label)}
                className={`flex w-full items-center justify-between py-3 text-2xl font-black tracking-wide transition-colors ${on ? "text-accent-leaf" : "text-white/80"}`}
              >
                {item.label}
                <svg width="18" height="10" viewBox="0 0 10 6" className={`transition-transform duration-300 ${isExpanded ? "rotate-180" : ""}`} fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                  <path d="M1 1l4 4 4-4" />
                </svg>
              </button>
              <div className={`overflow-hidden transition-all duration-300 ease-in-out ${isExpanded ? "max-h-64 opacity-100" : "max-h-0 opacity-0"}`}>
                <div className="flex flex-col pl-6 py-2 gap-4 border-l-2 border-white/10 ml-2 mt-2 mb-4">
                  {item.subs.map((s) => (
                    <Link
                      key={s.label}
                      href={`/categoria/${s.slug}`}
                      onClick={onClose}
                      className={`text-xl font-bold tracking-wide ${active === s.slug ? "text-accent-leaf" : "text-white/60 hover:text-white"}`}
                    >
                      {s.label}
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          );
        }

        return (
          <Link
            key={"m-" + item.label}
            href={item.href!}
            onClick={onClose}
            className={`block py-3 text-2xl font-black tracking-wide transition-colors ${on ? "text-accent-leaf" : item.highlight ? "text-white" : "text-white/80 hover:text-white"}`}
          >
            {item.highlight && <span className="mr-2 inline-block h-2 w-2 rounded-full bg-accent-soil animate-pulse" aria-hidden="true" />}
            {item.label}
          </Link>
        );
      })}
    </div>
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
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button 
        className="p-2 text-text-primary hover:bg-black/5 transition-colors focus:outline-none" 
        onClick={() => setIsOpen(true)}
        aria-label="Abrir menu"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      </button>

      {/* Drawer Fullscreen */}
      <div 
        className={`fixed inset-0 z-[100] bg-zinc-950 text-white flex flex-col transition-all duration-400 ease-in-out ${
          isOpen ? "opacity-100 translate-y-0" : "opacity-0 -translate-y-4 pointer-events-none"
        }`}
      >
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <span className="font-display text-3xl font-black tracking-tight text-white">Menu</span>
          <button 
            className="p-3 text-white/70 hover:bg-white/10 hover:text-white transition-colors focus:outline-none rounded-full bg-white/5" 
            onClick={() => setIsOpen(false)}
            aria-label="Fechar menu"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto pb-6">
          <Suspense>
            <MobileLinks onClose={() => setIsOpen(false)} />
          </Suspense>
        </div>

        <div className="mt-auto border-t border-white/10 p-6 flex flex-col gap-4 bg-zinc-900">
          <Link href="/sobre" onClick={() => setIsOpen(false)} className="block py-4 text-base font-bold uppercase tracking-widest text-center text-white/70 hover:bg-white/5 hover:text-white transition-colors rounded-xl border border-white/10">Sobre</Link>
          <Link href="/contato" onClick={() => setIsOpen(false)} className="block bg-accent-leaf py-4 text-base font-bold uppercase tracking-widest text-center text-white shadow-lg hover:bg-opacity-90 transition-all rounded-xl">Contato</Link>
        </div>
      </div>
    </>
  );
}
