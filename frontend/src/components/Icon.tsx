export function Icon({ name, className = "" }: { name: string; className?: string }) {
  return <i aria-hidden="true" className={`fi ${name} inline-flex leading-none ${className}`} />;
}
