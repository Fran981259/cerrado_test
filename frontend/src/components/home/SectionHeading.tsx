import Link from "next/link";

export function SectionHeading({
  eyebrow,
  title,
  href,
  linkLabel,
  id,
  dark = false,
}: {
  eyebrow: string;
  title: string;
  href?: string;
  linkLabel?: string;
  id?: string;
  dark?: boolean;
}) {
  return (
    <div className="flex items-end justify-between gap-4 border-b-2 border-charcoal pb-2">
      <div>
        <p className={`eyebrow ${dark ? "eyebrow-light" : ""}`}>{eyebrow}</p>
        <h2 id={id} className={`mt-1 font-display text-2xl font-bold sm:text-3xl ${dark ? "text-white" : "text-text-primary"}`}>
          {title}
        </h2>
      </div>
      {href && (
        <Link href={href} className="shrink-0 pb-1 text-xs font-bold uppercase tracking-wider text-accent-soil underline decoration-gold decoration-2 underline-offset-4 transition-colors hover:text-gold-deep">
          {linkLabel}
        </Link>
      )}
    </div>
  );
}