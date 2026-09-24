type ArticleQuickGuideProps = {
  categoryLabel: string;
  heading: string;
  minutes: number;
  reporterName: string;
  source?: { name?: string; url: string };
};

/** Displays the essential context needed before starting an article. */
export function ArticleQuickGuide({
  categoryLabel,
  heading,
  minutes,
  reporterName,
  source,
}: ArticleQuickGuideProps) {
  return (
    <section className="rounded-3xl border border-black/5 bg-white p-6">
      <p className="text-xs font-black uppercase tracking-[0.24em] text-accent-soil">
        Guia rápido
      </p>
      <h2 className="mt-2 font-display text-2xl font-black text-text-primary">{heading}</h2>
      <div className="mt-5 grid gap-3 text-sm">
        <div className="flex items-center justify-between rounded-2xl bg-canvas px-4 py-3">
          <span className="text-text-muted">Categoria</span>
          <strong>{categoryLabel}</strong>
        </div>
        <div className="flex items-center justify-between rounded-2xl bg-canvas px-4 py-3">
          <span className="text-text-muted">Tempo</span>
          <strong>{minutes} min</strong>
        </div>
        <div className="flex items-center justify-between rounded-2xl bg-canvas px-4 py-3">
          <span className="text-text-muted">Repórter</span>
          <strong>{reporterName}</strong>
        </div>
      </div>
      {source && (
        <a
          href={source.url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-5 flex min-h-11 items-center justify-between rounded-2xl bg-accent-soil px-4 py-3 text-sm font-black text-white transition hover:bg-text-primary"
        >
          <span>Fonte original</span>
          <span aria-hidden="true">↗</span>
        </a>
      )}
    </section>
  );
}
