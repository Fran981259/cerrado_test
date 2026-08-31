/**
 * AdSense — placeholder seguro para aprovação.
 * Só renderiza quando NEXT_PUBLIC_ADSENSE_ENABLED=true e tem CLIENT_ID.
 * Antes da aprovação, mostra espaço reservado sem quebrar layout.
 */
export function AdSlot({
  slot,
  format = "auto",
  responsive = true,
  className = "",
  label = "Publicidade",
}: {
  slot?: string;
  format?: string;
  responsive?: boolean;
  className?: string;
  label?: string;
}) {
  const enabled = process.env.NEXT_PUBLIC_ADSENSE_ENABLED === "true";
  const client = process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID;

  if (!enabled || !client) {
    // Placeholder discreto em dev / antes da aprovação
    return (
      <div
        className={`flex items-center justify-center rounded-xl border border-dashed border-zinc-200 bg-zinc-50 text-[11px] font-semibold tracking-widest text-zinc-400 ${className}`}
        style={{ minHeight: 90 }}
        aria-label={label}
      >
        {label}
      </div>
    );
  }

  return (
    <ins
      className={`adsbygoogle ${className}`}
      style={{ display: "block" }}
      data-ad-client={client}
      data-ad-slot={slot}
      data-ad-format={format}
      data-full-width-responsive={responsive ? "true" : "false"}
    />
  );
}

// Variantes prontas para layout
export function AdHeader() {
  return <AdSlot className="w-full max-w-[728px] mx-auto" label="Publicidade — Header 728x90" />;
}
export function AdInContent() {
  return <AdSlot className="my-6 w-full" label="Publicidade — In Content" />;
}
export function AdSidebar() {
  return <AdSlot className="w-full h-[250px]" label="Publicidade — Sidebar 300x250" />;
}
