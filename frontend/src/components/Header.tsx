import Link from "next/link";
import { Suspense } from "react";
import { MarketBar } from "@/components/markets/MarketBar";
import { DesktopNav } from "@/components/NavMenu";
import { MobileMenu } from "@/components/home/MobileMenu";

function SearchControl() {
  return (
    <form action="/busca" role="search" className="relative hidden md:block">
      <label htmlFor="busca-masthead" className="sr-only">
        Buscar no Portal Cerrado
      </label>
      <input
        id="busca-masthead"
        name="q"
        type="search"
        autoComplete="off"
        placeholder="Buscar no portal…"
        className="h-10 w-44 rounded border border-black/15 bg-canvas px-3 pr-9 text-sm text-text-primary placeholder:text-text-muted focus:bg-surface sm:w-56"
      />
      <button type="submit" aria-label="Buscar" className="absolute right-1 top-1/2 grid h-8 w-8 -translate-y-1/2 place-items-center text-accent-soil hover:text-gold-deep">
        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
          <circle cx="11" cy="11" r="7" />
          <line x1="16.5" y1="16.5" x2="21" y2="21" />
        </svg>
      </button>
    </form>
  );
}

export default function Header() {
  return (
    <>
      <Suspense
        fallback={
          <div className="sticky top-0 z-40 bg-accent-soil text-white" role="status" aria-label="Carregando cotações">
            <div className="container-editorial flex items-center gap-3 py-3.5">
              <span className="h-2 w-2 rounded-full bg-gold" aria-hidden="true" />
              <span className="text-[11px] font-bold uppercase tracking-[0.18em] text-white/80">Cotações em atualização…</span>
            </div>
          </div>
        }
      >
        <MarketBar />
      </Suspense>
      <header className="relative z-30 border-b border-black/10 bg-surface">
        <div className="container-editorial flex items-center gap-4 py-4">
          <div className="lg:hidden">
            <MobileMenu />
          </div>
          <Link href="/" className="mx-auto flex items-center gap-3 lg:mx-0" aria-label="Portal Cerrado — página inicial">
            <span aria-hidden="true" className="grid h-11 w-11 shrink-0 place-items-center rounded bg-accent-soil font-display text-lg font-bold text-white">
              PC
            </span>
            <span className="flex flex-col leading-none">
              <span className="font-display text-2xl font-bold tracking-tight text-text-primary">
                Portal <span className="text-accent-soil">Cerrado</span>
              </span>
              <span className="mt-1 text-[10px] font-bold uppercase tracking-[0.2em] text-gold-deep">Agro · Mercados · Mato Grosso do Sul</span>
            </span>
          </Link>
          <div className="ml-auto flex items-center gap-3">
            <SearchControl />
            <Link href="/busca" aria-label="Buscar no Portal Cerrado" className="grid h-10 w-10 place-items-center rounded border border-black/15 text-accent-soil transition-colors hover:bg-black/5 md:hidden">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                <circle cx="11" cy="11" r="7" />
                <line x1="16.5" y1="16.5" x2="21" y2="21" />
              </svg>
            </Link>
            <Link href="/contato" className="hidden rounded bg-accent-soil px-4 py-2.5 text-xs font-bold uppercase tracking-wider text-white transition-colors hover:bg-charcoal lg:inline-block">
              Contato
            </Link>
          </div>
        </div>

        <div className="hidden border-t border-black/10 lg:block">
          <div className="container-editorial py-1.5">
            <DesktopNav />
          </div>
        </div>
        <div className="masthead-rule" aria-hidden="true" />
      </header>
    </>
  );
}