import { Suspense } from "react";

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
const WMO: Record<number, { label: string; icon: string }> = {
  0: { label: "Céu limpo", icon: "☀️" },
  1: { label: "Quase limpo", icon: "🌤️" },
  2: { label: "Parcialmente nublado", icon: "⛅" },
  3: { label: "Nublado", icon: "☁️" },
  45: { label: "Nevoeiro", icon: "🌫️" },
  48: { label: "Nevoeiro com geada", icon: "🌫️" },
  51: { label: "Garoa leve", icon: "🌦️" },
  53: { label: "Garoa", icon: "🌦️" },
  55: { label: "Garoa forte", icon: "🌧️" },
  61: { label: "Chuva leve", icon: "🌧️" },
  63: { label: "Chuva", icon: "🌧️" },
  65: { label: "Chuva forte", icon: "⛈️" },
  71: { label: "Neve leve", icon: "🌨️" },
  73: { label: "Neve", icon: "🌨️" },
  75: { label: "Neve forte", icon: "❄️" },
  80: { label: "Pancadas leves", icon: "🌦️" },
  81: { label: "Pancadas", icon: "🌧️" },
  82: { label: "Pancadas fortes", icon: "⛈️" },
  95: { label: "Tempestade", icon: "⛈️" },
  96: { label: "Tempestade com granizo", icon: "⛈️" },
  99: { label: "Tempestade forte", icon: "⛈️" },
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
  const cond = WMO[w.code] ?? { label: "Tempo instável", icon: "🌤️" };
  const fmt = (v: number) => `${Math.round(v)}°`;
  return (
    <div className="rounded-2xl border border-zinc-100 bg-gradient-to-br from-sky-500 to-blue-700 p-5 text-white shadow-sm">
      <p className="text-[11px] font-bold uppercase tracking-widest opacity-80">Tempo agora • Campo Grande/MS</p>
      <div className="mt-2 flex items-center gap-3">
        <span className="text-4xl">{cond.icon}</span>
        <span className="text-5xl font-black">{fmt(w.temp)}</span>
        <span className="text-sm leading-snug opacity-90">
          {cond.label}<br />
          Sensação {fmt(w.feels)}
        </span>
      </div>
      <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs font-semibold opacity-90">
        <span>⬆ {fmt(w.tmax)} ⬇ {fmt(w.tmin)}</span>
        <span>💧 {w.humidity}%</span>
        <span>💨 {Math.round(w.wind)} km/h</span>
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
