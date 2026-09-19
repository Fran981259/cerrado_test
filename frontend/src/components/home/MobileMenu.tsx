"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { CAPITAL_MENU } from "@/components/NavMenu";

function Control({ open, onToggle }: { open: boolean; onToggle: () => void }) {
  return (
    <button
      type="button"
      onClick={onToggle}
      aria-expanded={open}
      aria-controls="menu-mobile-painel"
      aria-label={open ? "Fechar menu" : "Abrir menu"}
      className="grid h-11 w-11 place-items-center rounded border border-black/15 text-text-primary transition-colors hover:bg-black/5"
    >
      {open ? (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      ) : (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
          <line x1="3" y1="7" x2="21" y2="7" />
          <line x1="3" y1="12" x2="21" y2="12" />
          <line x1="3" y1="17" x2="15" y2="17" />
        </svg>
      )}
    </button>
  );
}

export function MobileMenu() {
  const [open, setOpen] = useState(false);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKey);
    document.documentElement.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.documentElement.style.overflow = "";
    };
  }, [open]);

  return (
    <>
      <Control open={open} onToggle={() => setOpen((v) => !v)} />
      {open && <div className="fixed inset-0 -z-10 bg-black/40" onClick={() => setOpen(false)} aria-hidden="true" />}
      <div
        id="menu-mobile-painel"
        hidden={!open}
        role="dialog"
        aria-modal="true"
        aria-label="Menu de editorias do Portal Cerrado"
        className="fixed inset-x-0 top-0 z-50 max-h-[100dvh] overflow-y-auto border-b border-black/10 bg-surface shadow-2xl"
      >
        <div className="flex items-center justify-between gap-4 px-5 py-4">
          <span className="font-display text-2xl font-bold tracking-tight text-text-primary">Editorias</span>
          <button ref={closeRef} type="button" onClick={() => setOpen(false)} aria-label="Fechar menu" className="grid h-11 w-11 place-items-center rounded border border-black/15 text-text-primary hover:bg-black/5">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="square">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div className="border-t border-black/10 px-5 py-4">
          <Link href="/" onClick={() => setOpen(false)} className="block border-b border-black/8 py-3 font-display text-xl font-bold text-text-primary hover:text-accent-soil">
            Início
          </Link>
          {CAPITAL_MENU.map((item) =>
            item.href ? (
              <Link key={item.label} href={item.href} onClick={() => setOpen(false)} className="block border-b border-black/8 py-3 font-display text-xl font-bold text-text-primary hover:text-accent-soil">
                {item.label}
              </Link>
            ) : (
              <details key={item.label} className="border-b border-black/8">
                <summary className="cursor-pointer list-none py-3 font-display text-xl font-bold text-text-primary hover:text-accent-soil">
                  <span className="flex items-center justify-between">
                    {item.label}
                    <svg width="14" height="8" viewBox="0 0 10 6" aria-hidden="true" className="text-gold-deep">
                      <path d="M1 1l4 4 4-4" stroke="currentColor" strokeWidth="2" fill="none" strokeLinecap="round" />
                    </svg>
                  </span>
                </summary>
                <div className="flex flex-col gap-1 py-1 pl-4">
                  {item.subs?.map((sub) => (
                    <Link key={sub.slug} href={`/categoria/${sub.slug}`} onClick={() => setOpen(false)} className="rounded px-2 py-2 text-sm font-bold text-text-muted hover:bg-black/5 hover:text-text-primary">
                      {sub.label}
                    </Link>
                  ))}
                </div>
              </details>
            ),
          )}
        </div>

        <div className="flex gap-3 border-t border-black/10 px-5 py-4">
          <Link href="/sobre" onClick={() => setOpen(false)} className="flex-1 rounded border border-black/15 px-4 py-3 text-center text-xs font-bold uppercase tracking-wider text-text-primary hover:bg-black/5">
            Sobre
          </Link>
          <Link href="/contato" onClick={() => setOpen(false)} className="flex-1 rounded bg-accent-soil px-4 py-3 text-center text-xs font-bold uppercase tracking-wider text-white">
            Contato
          </Link>
        </div>
      </div>
    </>
  );
}