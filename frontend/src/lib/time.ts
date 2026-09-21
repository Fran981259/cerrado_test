const CAMPO_GRANDE_TIMEZONE = "America/Campo_Grande";

function parseDate(iso?: string | null): Date | null {
  if (!iso) return null;
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return null;
  return date;
}

export function formatRelativeTime(iso?: string | null): string {
  const date = parseDate(iso);
  if (!date) return "";
  const diffMs = Date.now() - date.getTime();
  if (diffMs < 0) return "agora";
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return "agora";
  if (minutes < 60) return `há ${minutes} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `há ${hours} h`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `há ${days} ${days === 1 ? "dia" : "dias"}`;
  return formatCampoGrandeDate(iso, { day: "2-digit", month: "short", year: "numeric" });
}

export function formatCampoGrandeDate(iso?: string | null, opts?: Intl.DateTimeFormatOptions): string {
  const date = parseDate(iso);
  if (!date) return "";
  try {
    return new Intl.DateTimeFormat("pt-BR", { timeZone: CAMPO_GRANDE_TIMEZONE, ...opts }).format(date);
  } catch {
    return new Intl.DateTimeFormat("pt-BR", opts).format(date);
  }
}

export function formatMarketTime(iso?: string | null): string {
  return formatCampoGrandeDate(iso, { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
}