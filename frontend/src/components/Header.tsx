import Link from "next/link";
import { DesktopNav, MobileNav } from "./NavMenu";

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-canvas/90 backdrop-blur-md border-b border-zinc-200 shadow-[0_1px_12px_rgba(0,0,0,0.04)]">
      <div className="container-custom flex items-center justify-between py-4 gap-4">
        <Link href="/" className="flex flex-col shrink-0">
          <span className="text-3xl font-display font-bold tracking-tight text-text-primary">PORTAL</span>
          <span className="text-xl font-display font-bold tracking-wider text-accent-soil -mt-1">CERRADO</span>
        </Link>

        <DesktopNav />

        <div className="hidden md:flex items-center gap-4 text-xs font-sans text-text-muted">
          <Link href="/sobre" className="hover:text-text-primary">Sobre</Link>
          <Link href="/contato" className="hover:text-text-primary">Contato</Link>
        </div>
      </div>

      {/* mobile nav */}
      <MobileNav />
    </header>
  );
}
