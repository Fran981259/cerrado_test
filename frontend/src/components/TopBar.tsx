import Link from "next/link";

function formatTopDate() {
  try {
    return new Date().toLocaleDateString("pt-BR", {
      weekday: "long",
      day: "2-digit",
      month: "long",
      year: "numeric",
      timeZone: "America/Campo_Grande",
    });
  } catch {
    return "";
  }
}

async function MiniWeather() {
  let t: number | null = null;
  let label = "";
  try {
    const r = await fetch(
      "https://api.open-meteo.com/v1/forecast?latitude=-20.4697&longitude=-54.6201&current=temperature_2m,weather_code&timezone=America%2FCampo_Grande&forecast_days=1",
      { next: { revalidate: 900 } }
    );
    if (!r.ok) return null;
    const d = await r.json();
    t = Math.round(d.current.temperature_2m);
    const code = d.current.weather_code as number;
    label = ({ 0: "Céu limpo", 1: "Quase limpo", 2: "Parc. nublado", 3: "Nublado", 45: "Nevoeiro", 51: "Garoa", 61: "Chuva leve", 95: "Tempestade" } as Record<number, string>)[code] || "";
  } catch {
    return null;
  }
  return (
    <span className="inline-flex items-center gap-1.5 text-[11px] text-text-muted">
      <span className="h-1 w-1 rounded-full bg-accent-leaf" aria-hidden />
      <span className="font-black text-text-primary">{t}°</span>
      {label && <span className="hidden sm:inline">· {label}</span>}
    </span>
  );
}

export default async function TopBar() {
  const date = formatTopDate();
  return (
    <div className="hidden border-b border-white/5 bg-[#040405] text-xs md:block">
      <div className="container-custom flex items-center justify-between gap-4 py-1.5">
        <div className="flex items-center gap-2.5 text-text-muted">
          <span className="hidden font-semibold uppercase tracking-wider text-accent-soil sm:inline">Campo Grande — MS</span>
          <span className="hidden h-3 w-px bg-white/10 sm:block" aria-hidden />
          <span className="capitalize text-text-muted">{date}</span>
          <span className="hidden h-3 w-px bg-white/10 sm:block" aria-hidden />
          <MiniWeather />
        </div>
        <div className="flex items-center gap-3">
          <span className="hidden text-[11px] font-bold uppercase tracking-wider text-text-muted lg:inline">Siga:</span>
          <a href="https://facebook.com" target="_blank" rel="noopener" aria-label="Facebook" className="grid h-7 w-7 place-items-center rounded-full bg-white/10 text-white shadow-sm ring-1 ring-white/5 hover:bg-white hover:text-accent-soil transition-colors">
            <i className="fi fi-rr-share text-[12px]" aria-hidden />
          </a>
          <a href="https://instagram.com" target="_blank" rel="noopener" aria-label="Instagram" className="grid h-7 w-7 place-items-center rounded-full bg-white/10 text-white shadow-sm ring-1 ring-white/5 hover:bg-white hover:text-accent-soil transition-colors">
            <i className="fi fi-rr-camera text-[12px]" aria-hidden />
          </a>
          <a href="https://x.com" target="_blank" rel="noopener" aria-label="X" className="grid h-7 w-7 place-items-center rounded-full bg-white/10 text-white shadow-sm ring-1 ring-white/5 hover:bg-white hover:text-accent-soil transition-colors">
            <i className="fi fi-rr-paper-plane text-[12px]" aria-hidden />
          </a>
          <span className="h-5 w-px bg-white/10" aria-hidden />
          <Link href="/?search=" aria-label="Buscar" className="inline-flex items-center gap-1.5 rounded-full bg-white px-3 py-1.5 text-[11px] font-black uppercase tracking-wider text-black shadow-sm hover:bg-accent-soil hover:text-white transition-colors">
            <i className="fi fi-rr-search text-[11px]" aria-hidden /> Buscar
          </Link>
        </div>
      </div>
    </div>
  );
}
