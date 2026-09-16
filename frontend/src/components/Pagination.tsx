import Link from "next/link";

export function Pagination({ page, totalPages, base }: { page: number; totalPages: number; base: string }) {
  if (totalPages <= 1) return null;
  const href = (number: number) => number === 1 ? base : `${base}?page=${number}`;
  return (
    <nav aria-label="Paginação" className="mt-12 flex flex-wrap items-center justify-between gap-3 rounded-[1.5rem] border border-black/5 bg-white px-5 py-4 text-sm font-semibold shadow-sm">
      <span className="text-text-muted">Página <strong className="text-text-primary">{page}</strong> de {totalPages}</span>
      <div className="flex gap-2">
        {page > 1 ? <Link className="rounded-full bg-canvas px-4 py-2 font-black text-text-primary hover:bg-zinc-200" href={href(page - 1)}>Anterior</Link> : <span aria-disabled="true" className="px-4 py-2 text-zinc-400">Anterior</span>}
        {page < totalPages ? <Link className="rounded-full bg-text-primary px-4 py-2 font-black text-white hover:bg-accent-soil" href={href(page + 1)}>Próxima</Link> : <span aria-disabled="true" className="px-4 py-2 text-zinc-400">Próxima</span>}
      </div>
    </nav>
  );
}
