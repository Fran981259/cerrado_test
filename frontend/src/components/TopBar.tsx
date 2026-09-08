import Link from "next/link";

function formatTopDate() {
  try {
    return new Date().toLocaleDateString("pt-BR", {
      weekday: "long",
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

export default function TopBar() {
  const date = formatTopDate();
  return (
    <div className="hidden border-b border-black/5 bg-[#f7f1e8] text-xs md:block">
      <div className="container-custom flex items-center justify-between gap-4 py-2">
        <div className="flex items-center gap-3 text-text-muted">
          <span className="hidden font-semibold uppercase tracking-wider text-accent-soil sm:inline">Campo Grande — MS</span>
          <span className="hidden h-3 w-px bg-black/10 sm:block" aria-hidden />
          <span className="capitalize text-text-muted">{date}</span>
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden text-[11px] font-bold uppercase tracking-wider text-text-muted lg:inline">Siga:</span>
          <a href="https://facebook.com" target="_blank" rel="noopener" aria-label="Facebook" className="grid h-7 w-7 place-items-center rounded-full bg-white text-text-muted shadow-sm ring-1 ring-black/5 hover:text-accent-soil">
            <i className="fi fi-rr-share text-[12px]" aria-hidden />
          </a>
          <a href="https://instagram.com" target="_blank" rel="noopener" aria-label="Instagram" className="grid h-7 w-7 place-items-center rounded-full bg-white text-text-muted shadow-sm ring-1 ring-black/5 hover:text-accent-soil">
            <i className="fi fi-rr-camera text-[12px]" aria-hidden />
          </a>
          <a href="https://x.com" target="_blank" rel="noopener" aria-label="X" className="grid h-7 w-7 place-items-center rounded-full bg-white text-text-muted shadow-sm ring-1 ring-black/5 hover:text-accent-soil">
            <i className="fi fi-rr-paper-plane text-[12px]" aria-hidden />
          </a>
          <span className="h-5 w-px bg-black/10" aria-hidden />
          <Link href="/?search=" aria-label="Buscar" className="inline-flex items-center gap-1.5 rounded-full bg-text-primary px-3 py-1.5 text-[11px] font-black uppercase tracking-wider text-white shadow-sm hover:bg-accent-soil">
            <i className="fi fi-rr-search text-[11px]" aria-hidden /> Buscar
          </Link>
        </div>
      </div>
    </div>
  );
}
