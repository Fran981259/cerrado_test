import { Suspense } from "react";
import { Icon } from "@/components/Icon";

type Weather = {
  temp: number;
  feels: number;
  humidity: number;
  wind: number;
  code: number;
  tmax: number;
  tmin: number;
};

// Tempo REAL via Open-Meteo (grátis, sem chave) — Campo Grande/MS.
// Server-side com revalidação de 15 min. Sem dado fake: se a API falhar,
// o módulo some em vez de inventar número.
const WMO: Record<number, { label: string; iconClass: string }> = {
  0: { label: "Céu limpo", iconClass: "fi-rr-sun" },
  1: { label: "Quase limpo", iconClass: "fi-rr-cloud-sun" },
  2: { label: "Parcialmente nublado", iconClass: "fi-rr-cloud-sun" },
  3: { label: "Nublado", iconClass: "fi-rr-cloud" },
  45: { label: "Nevoeiro", iconClass: "fi-rr-fog" },
  48: { label: "Nevoeiro com geada", iconClass: "fi-rr-fog" },
  51: { label: "Garoa leve", iconClass: "fi-rr-cloud-drizzle" },
  53: { label: "Garoa", iconClass: "fi-rr-cloud-drizzle" },
  55: { label: "Garoa forte", iconClass: "fi-rr-cloud-drizzle" },
  61: { label: "Chuva leve", iconClass: "fi-rr-cloud-rain" },
  63: { label: "Chuva", iconClass: "fi-rr-cloud-rain" },
  65: { label: "Chuva forte", iconClass: "fi-rr-cloud-rain" },
  71: { label: "Neve leve", iconClass: "fi-rr-snowflake" },
  73: { label: "Neve", iconClass: "fi-rr-snowflake" },
  75: { label: "Neve forte", iconClass: "fi-rr-snowflake" },
  80: { label: "Pancadas leves", iconClass: "fi-rr-cloud-rain" },
  81: { label: "Pancadas", iconClass: "fi-rr-cloud-rain" },
  82: { label: "Pancadas fortes", iconClass: "fi-rr-cloud-rain" },
  95: { label: "Tempestade", iconClass: "fi-rr-thunderstorm" },
  96: { label: "Tempestade com granizo", iconClass: "fi-rr-thunderstorm" },
  99: { label: "Tempestade forte", iconClass: "fi-rr-thunderstorm" },
};

async function load(): Promise<Weather | null> {
  try {
    const r = await fetch(
      "https://api.open-meteo.com/v1/forecast?latitude=-20.4697&longitude=-54.6201&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FCampo_Grande&forecast_days=1",
      { next: { revalidate: 900 } }
    );
    if (!r.ok) return null;
    const d = await r.json();
    return {
      temp: d.current.temperature_2m,
      feels: d.current.apparent_temperature,
      humidity: d.current.relative_humidity_2m,
      wind: d.current.wind_speed_10m,
      code: d.current.weather_code,
      tmax: d.daily.temperature_2m_max[0],
      tmin: d.daily.temperature_2m_min[0],
    };
  } catch {
    return null;
  }
}

async function Card() {
  const w = await load();
  if (!w) return null;
  const cond = WMO[w.code] ?? { label: "Tempo instável", iconClass: "fi-rr-cloud-sun" };
  const fmt = (v: number) => `${Math.round(v)}°`;
  return (
    <div className="overflow-hidden rounded-[1.75rem] border border-white/50 bg-gradient-to-br from-[#325d7d] via-[#4a6741] to-[#2d2926] p-5 text-white shadow-[0_20px_60px_rgba(45,41,38,0.16)]">
      <p className="text-[11px] font-black uppercase tracking-[0.22em] text-white/75">Tempo agora • Campo Grande/MS</p>
      <div className="mt-2 flex items-center gap-3">
        <Icon name={cond.iconClass} className="text-4xl" />
        <span className="font-display text-6xl font-black tracking-tight">{fmt(w.temp)}</span>
        <span className="text-sm leading-snug opacity-90">
          {cond.label}<br />
          Sensação {fmt(w.feels)}
        </span>
      </div>
      <div className="mt-4 flex flex-wrap gap-2 text-xs font-bold text-white/90">
        <span>Máx. {fmt(w.tmax)} Min. {fmt(w.tmin)}</span>
        <span className="inline-flex items-center gap-1"><Icon name="fi-rr-raindrops" /> {w.humidity}%</span>
        <span className="inline-flex items-center gap-1"><Icon name="fi-rr-wind" /> {Math.round(w.wind)} km/h</span>
      </div>
    </div>
  );
}

export default function Weather() {
  return (
    <Suspense fallback={null}>
      <Card />
    </Suspense>
  );
}
