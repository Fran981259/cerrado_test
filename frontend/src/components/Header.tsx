import Link from "next/link";
import TopBar from "./TopBar";
import { DesktopNav, MobileNav } from "./NavMenu";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 glass-panel">
      <TopBar />
      <div className="container-custom flex items-center gap-4 py-3">
        <Link href="/" className="group flex shrink-0 items-center gap-3 transition-transform duration-300 hover:scale-[1.02]">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-text-primary font-display text-xl font-black text-white shadow-lg transition-colors duration-500 group-hover:bg-accent-soil">PC</span>
          <span className="hidden flex-col leading-none sm:flex">
            <span className="text-xl font-display font-black tracking-tight text-text-primary">Portal</span>
            <span className="text-sm font-display font-black tracking-[0.18em] text-accent-soil transition-colors duration-500 group-hover:text-text-primary">Cerrado</span>
          </span>
        </Link>

        <div className="min-w-0 flex-1">
          <DesktopNav />
        </div>

        <div className="hidden shrink-0 items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted md:flex">
          <Link href="/sobre" className="rounded-full px-3 py-2 hover:bg-white/10 hover:text-text-primary transition-colors">Sobre</Link>
          <Link href="/contato" className="rounded-full bg-accent-soil px-4 py-2 text-white shadow-sm hover:bg-white hover:text-text-primary transition-all">Contato</Link>
        </div>
      </div>

      {/* mobile nav */}
      <MobileNav />
    </header>
  );
}
