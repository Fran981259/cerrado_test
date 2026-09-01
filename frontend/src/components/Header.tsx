import Link from "next/link";
import { CATEGORY_LIST } from "@/lib/categories";

const NAV = [
  { href: "/", label: "Início" },
  ...CATEGORY_LIST.slice(0, 6).map((c) => ({ href: `/?cat=${c.slug}`, label: c.label })),
];

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-canvas border-b border-zinc-200">
      <div className="container-custom flex items-center justify-between py-4 gap-4">
        <Link href="/" className="flex flex-col shrink-0">
          <span className="text-3xl font-display font-bold tracking-tight text-text-primary">PORTAL</span>
          <span className="text-xl font-display font-bold tracking-wider text-accent-soil -mt-1">CERRADO</span>
        </Link>

        <nav className="hidden lg:flex items-center gap-1">
          {NAV.map((n) => (
            <Link
              key={n.href + n.label}
              href={n.href}
              className="px-3 py-1 text-sm font-sans font-medium text-text-primary hover:text-accent-soil transition-colors"
            >
              {n.label}
            </Link>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-4 text-xs font-sans text-text-muted">
          <Link href="/sobre" className="hover:text-text-primary">Sobre</Link>
          <Link href="/contato" className="hover:text-text-primary">Contato</Link>
        </div>
      </div>

      {/* mobile nav */}
      <div className="lg:hidden border-t border-zinc-200 overflow-x-auto">
        <div className="flex gap-4 px-4 py-2">
          {NAV.map((n) => (
            <Link
              key={"m-" + n.label}
              href={n.href}
              className="shrink-0 text-sm font-sans font-medium text-text-primary hover:text-accent-soil"
            >
              {n.label}
            </Link>
          ))}
        </div>
      </div>
    </header>
  );
}
