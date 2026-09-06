/**
 * AdSense real: só renderiza quando habilitado e configurado.
 */
export function AdSlot({
  slot,
  format = "auto",
  responsive = true,
  className = "",
  label,
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
    return null;
  }

  return (
    <ins
      className={`adsbygoogle ${className}`}
      style={{ display: "block" }}
      data-ad-client={client}
      data-ad-slot={slot}
      data-ad-format={format}
      data-full-width-responsive={responsive ? "true" : "false"}
      aria-label={label}
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
