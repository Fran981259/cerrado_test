"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Suspense, useState } from "react";

// Taxonomia Capital News adaptada à paleta Cerrado — mantém slugs existentes, só rótulos mudam
// Paleta continua Cerrado (rounded-full, bg-white, accent-soil), funcionalidade vem do Capital
type Sub = { label: string; slug: string };
type MenuItem = { label: string; href?: string; subs?: Sub[] };

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
];

const linkCls = (on: boolean) =>
  `relative px-2.5 py-1.5 text-[11px] font-black uppercase tracking-wider transition-all whitespace-nowrap ${
    on ? "bg-accent-leaf text-white shadow-sm ring-1 ring-black/5" : "text-text-muted hover:bg-black/5 hover:text-text-primary"
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
  return (
    <div className="flex flex-col gap-1 p-4">
      <Link
        href="/"
        onClick={onClose}
        aria-current={active === null ? "page" : undefined}
        className={`block border-l-4 px-4 py-3 text-sm font-black uppercase tracking-wider transition-colors ${active === null ? "border-accent-soil bg-black/5 text-accent-soil" : "border-transparent text-text-muted"}`}
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
            onClick={onClose}
            aria-current={on ? "page" : undefined}
            className={`block border-l-4 px-4 py-3 text-sm font-black uppercase tracking-wider transition-colors ${on ? "border-accent-soil bg-black/5 text-accent-soil" : "border-transparent text-text-muted"}`}
          >
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

      {/* Overlay & Drawer */}
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex">
          {/* Fundo escuro (clica para fechar) */}
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm transition-opacity"
            onClick={() => setIsOpen(false)}
            aria-hidden="true"
          />
          
          {/* Menu Lateral */}
          <div className="relative flex w-full max-w-xs flex-col overflow-y-auto bg-white shadow-2xl animate-in slide-in-from-left-full duration-300">
            <div className="flex items-center justify-between border-b p-4">
              <span className="font-display text-xl font-black tracking-tight text-text-primary">Menu</span>
              <button 
                className="p-2 text-text-muted hover:bg-black/5 hover:text-text-primary transition-colors focus:outline-none" 
                onClick={() => setIsOpen(false)}
                aria-label="Fechar menu"
              >
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>
            
            <Suspense>
              <MobileLinks onClose={() => setIsOpen(false)} />
            </Suspense>

            <div className="mt-auto border-t p-4 flex flex-col gap-2">
              <Link href="/sobre" onClick={() => setIsOpen(false)} className="block px-4 py-3 text-sm font-bold uppercase tracking-wider text-center text-text-muted hover:bg-black/5 hover:text-text-primary transition-colors">Sobre</Link>
              <Link href="/contato" onClick={() => setIsOpen(false)} className="block bg-accent-leaf px-4 py-3 text-sm font-bold uppercase tracking-wider text-center text-white shadow-sm hover:bg-text-primary transition-all">Contato</Link>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
