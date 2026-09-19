import Link from "next/link";
import TopBar from "./TopBar";
import { DesktopNav, MobileNav } from "./NavMenu";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-white/5">
      <TopBar />
      <div className="container-custom flex items-center gap-4 py-3">
        <Link href="/" className="group flex shrink-0 items-center gap-3 transition-transform duration-300 hover:scale-[1.02]">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-white font-display text-xl font-black text-[#040405] shadow-lg transition-colors duration-500 group-hover:bg-accent-soil group-hover:text-white">PC</span>
          <span className="hidden flex-col leading-none sm:flex">
            <span className="text-xl font-display font-black tracking-tight text-white">Portal</span>
            <span className="text-sm font-display font-black tracking-[0.18em] text-accent-soil transition-colors duration-500 group-hover:text-white">Cerrado</span>
          </span>
        </Link>

        <div className="min-w-0 flex-1">
          <DesktopNav />
        </div>

        <div className="hidden shrink-0 items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted md:flex">
          <Link href="/sobre" className="px-3 py-2 hover:bg-white/10 hover:text-white transition-colors rounded-full">Sobre</Link>
          <Link href="/contato" className="bg-accent-leaf px-4 py-2 text-white shadow-sm hover:bg-white hover:text-black transition-all rounded-full">Contato</Link>
        </div>

        {/* mobile hamburger wrapper */}
        <div className="flex shrink-0 items-center lg:hidden ml-auto">
          <MobileNav />
        </div>
      </div>
    </header>
  );
}
