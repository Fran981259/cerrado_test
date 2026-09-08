import Link from "next/link";
import TopBar from "./TopBar";
import { DesktopNav, MobileNav } from "./NavMenu";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-black/5 bg-canvas/82 shadow-[0_14px_50px_rgba(45,41,38,0.08)] backdrop-blur-xl">
      <TopBar />
      <div className="container-custom flex items-center justify-between gap-4 py-4">
        <Link href="/" className="group flex shrink-0 items-center gap-3">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-text-primary font-display text-2xl font-black text-white shadow-lg transition group-hover:bg-accent-soil">PC</span>
          <span className="flex flex-col leading-none">
            <span className="text-2xl font-display font-black tracking-tight text-text-primary">Portal</span>
            <span className="text-xl font-display font-black tracking-[0.18em] text-accent-soil">Cerrado</span>
          </span>
        </Link>

        <DesktopNav />

        <div className="hidden items-center gap-2 text-xs font-bold uppercase tracking-wider text-text-muted md:flex">
          <Link href="/sobre" className="rounded-full px-3 py-2 hover:bg-white hover:text-text-primary">Sobre</Link>
          <Link href="/contato" className="rounded-full bg-text-primary px-4 py-2 text-white shadow-sm hover:bg-accent-soil">Contato</Link>
        </div>
      </div>

      {/* mobile nav */}
      <MobileNav />
    </header>
  );
}
