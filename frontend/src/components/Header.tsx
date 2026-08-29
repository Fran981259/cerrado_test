import Link from "next/link";
import { CATEGORY_LIST } from "@/lib/categories";

const NAV = [
  { href: "/", label: "Início" },
  ...CATEGORY_LIST.slice(0, 6).map((c) => ({ href: `/?cat=${c.slug}`, label: c.label })),
];

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-white shadow-sm">
      {/* top bar */}
      <div className="bg-[#1a1a2e] text-white text-xs">
        <div className="container-custom flex items-center justify-between py-2">
          <span className="opacity-80 hidden sm:block">
            {new Date().toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
          </span>
          <span className="opacity-80">Mato Grosso do Sul • Atualizado 24h</span>
          <div className="hidden md:flex gap-4 opacity-80">
            <Link href="/sobre" className="hover:text-white hover:opacity-100">Sobre</Link>
            <Link href="/contato" className="hover:text-white hover:opacity-100">Contato</Link>
          </div>
        </div>
      </div>

      {/* main */}
      <div className="container-custom flex items-center justify-between py-4 gap-4">
        <Link href="/" className="flex items-center gap-2 shrink-0">
          <span className="text-2xl font-black tracking-tight text-[#e63946]">ATUALIZA<span className="text-[#1a1a2e]">BRASIL</span></span>
          <span className="hidden sm:inline bg-[#e63946] text-white text-[10px] font-bold px-2 py-1 rounded">MS</span>
        </Link>

        <nav className="hidden lg:flex items-center gap-1">
          {NAV.map((n) => (
            <Link
              key={n.href + n.label}
              href={n.href}
              className="px-3 py-2 rounded-md text-[13px] font-semibold text-zinc-700 hover:bg-[#e63946] hover:text-white transition-colors"
            >
              {n.label}
            </Link>
          ))}
        </nav>

        <Link href="/contato" className="hidden md:inline-flex bg-[#e63946] hover:bg-[#c1121f] text-white text-sm font-bold px-5 py-2.5 rounded-full transition-colors">
          Anuncie aqui
        </Link>
      </div>

      {/* mobile nav */}
      <div className="lg:hidden border-t border-zinc-100 overflow-x-auto">
        <div className="flex gap-1 px-4 py-2">
          {NAV.map((n) => (
            <Link
              key={"m-" + n.label}
              href={n.href}
              className="shrink-0 px-3 py-1.5 rounded-full bg-zinc-100 text-xs font-semibold text-zinc-700 hover:bg-[#e63946] hover:text-white"
            >
              {n.label}
            </Link>
          ))}
        </div>
      </div>
    </header>
  );
}
