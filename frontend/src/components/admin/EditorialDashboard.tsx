"use client";

import { useMemo, useState } from "react";
import { CATEGORY_LIST } from "@/lib/categories";
import { type EditorialArticle, type EditorialChanges, type EditorialStatus, fetchEditorialQueue } from "@/lib/editorialApi";
import { EditorialReviewCard } from "./EditorialReviewCard";

const PAGE_SIZE = 12;

/** Provides a protected, paginated workspace for editorial corrections. */
export function EditorialDashboard() {
  const [apiKey, setApiKey] = useState("");
  const [articles, setArticles] = useState<EditorialArticle[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState<EditorialStatus | "all">("all");
  const [category, setCategory] = useState("all");
  const [page, setPage] = useState(0);

  const loadQueue = async (key = apiKey) => {
    if (!key.trim()) return setError("Informe a chave editorial para abrir a fila.");
    setIsLoading(true);
    setError("");
    try {
      const queue = await fetchEditorialQueue(key.trim());
      setApiKey(key.trim());
      setArticles(queue);
      setPage(0);
    } catch (loadError) {
      setError(loadError instanceof Error ? loadError.message : "Não foi possível carregar a fila.");
    } finally {
      setIsLoading(false);
    }
  };

  const filtered = useMemo(() => articles.filter((article) => {
    const matchesText = `${article.title} ${article.summary ?? ""}`.toLocaleLowerCase().includes(query.toLocaleLowerCase());
    return matchesText && (status === "all" || article.status === status) && (category === "all" || article.category === category);
  }), [articles, category, query, status]);
  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageArticles = filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  const saveArticle = (slug: string, changes: EditorialChanges) => {
    setArticles((current) => current.map((article) => article.slug === slug ? { ...article, ...changes } : article));
  };
  const clearSession = () => {
    setApiKey("");
    setArticles([]);
    setError("");
  };

  if (!articles.length) return <AccessPanel apiKey={apiKey} error={error} isLoading={isLoading} onChange={setApiKey} onSubmit={() => loadQueue()} />;

  return (
    <section className="container-editorial py-8 sm:py-12" aria-label="Mesa editorial">
      <header className="border-b border-text-primary/15 pb-6">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div><p className="eyebrow">Administração editorial</p><h1 className="mt-2 font-display text-3xl font-bold text-text-primary sm:text-4xl">Fila de curadoria</h1></div>
          <button className="min-h-11 rounded-md border border-text-primary/25 px-4 text-base font-bold text-text-primary" type="button" onClick={clearSession}>Sair</button>
        </div>
        <p className="mt-3 max-w-3xl text-base leading-relaxed text-text-muted">Revise a pauta antes de ela contaminar a home. Publicar é uma decisão explícita, não um efeito de filtro.</p>
      </header>

      <div className="mt-6 grid gap-4 lg:grid-cols-4">
        <FilterInput label="Buscar" value={query} onChange={(value) => { setQuery(value); setPage(0); }} />
        <FilterSelect label="Status" value={status} onChange={(value) => { setStatus(value as EditorialStatus | "all"); setPage(0); }} options={[{ value: "all", label: "Todos" }, ...statusOptions()]} />
        <FilterSelect label="Categoria" value={category} onChange={(value) => { setCategory(value); setPage(0); }} options={[{ value: "all", label: "Todas" }, ...CATEGORY_LIST.map((item) => ({ value: item.slug, label: item.label }))]} />
        <div className="rounded-md bg-canvas p-4"><p className="eyebrow">Na seleção</p><p className="mt-1 font-display text-2xl font-bold">{filtered.length}</p></div>
      </div>

      <div className="mt-6 grid gap-5">
        {pageArticles.map((article) => <EditorialReviewCard key={article.slug} article={article} apiKey={apiKey} onSaved={(changes) => saveArticle(article.slug, changes)} />)}
        {!pageArticles.length && <EmptyState onReset={() => { setQuery(""); setStatus("all"); setCategory("all"); }} />}
      </div>
      <Pagination page={page} pageCount={pageCount} onChange={setPage} />
    </section>
  );
}

type AccessPanelProps = { apiKey: string; error: string; isLoading: boolean; onChange: (value: string) => void; onSubmit: () => void };

function AccessPanel({ apiKey, error, isLoading, onChange, onSubmit }: AccessPanelProps) {
  return <section className="container-editorial py-12"><div className="mx-auto max-w-xl rounded-lg border border-text-primary/15 bg-surface p-6 sm:p-8"><p className="eyebrow">Acesso restrito</p><h1 className="mt-2 font-display text-3xl font-bold">Mesa editorial</h1><p className="mt-3 text-base leading-relaxed text-text-muted">Use a chave editorial. Ela fica apenas enquanto esta página estiver aberta.</p><label className="mt-6 grid gap-2 text-sm font-semibold">Chave editorial<input className="min-h-11 rounded-md border border-text-primary/20 bg-surface px-3 text-base font-normal" type="password" value={apiKey} onChange={(event) => onChange(event.target.value)} onKeyDown={(event) => event.key === "Enter" && onSubmit()} autoComplete="current-password" /></label><button className="mt-5 min-h-11 rounded-md bg-accent-soil px-4 text-base font-bold text-surface disabled:cursor-not-allowed disabled:opacity-60" type="button" onClick={onSubmit} disabled={isLoading}>{isLoading ? "Abrindo…" : "Abrir fila"}</button>{error && <p className="mt-4 text-sm font-semibold text-text-muted" role="alert">{error}</p>}</div></section>;
}

function statusOptions() { return ["draft", "classified", "review", "rewritten", "published", "failed"].map((value) => ({ value, label: value })); }
function FilterInput({ label, value, onChange }: { label: string; value: string; onChange: (value: string) => void }) { return <label className="grid gap-2 text-sm font-semibold">{label}<input className="min-h-11 rounded-md border border-text-primary/20 bg-surface px-3 text-base font-normal" value={value} onChange={(event) => onChange(event.target.value)} /></label>; }
function FilterSelect({ label, value, onChange, options }: { label: string; value: string; onChange: (value: string) => void; options: Array<{ value: string; label: string }> }) { return <label className="grid gap-2 text-sm font-semibold">{label}<select className="min-h-11 rounded-md border border-text-primary/20 bg-surface px-3 text-base font-normal" value={value} onChange={(event) => onChange(event.target.value)}>{options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select></label>; }
function EmptyState({ onReset }: { onReset: () => void }) { return <div className="rounded-lg border border-text-primary/15 bg-surface p-8 text-center"><h2 className="font-display text-2xl font-bold">Nenhuma matéria encontrada</h2><p className="mt-2 text-base text-text-muted">Limpe os filtros ou carregue a fila novamente.</p><button className="mt-4 min-h-11 rounded-md border border-text-primary/25 px-4 text-base font-bold" type="button" onClick={onReset}>Limpar filtros</button></div>; }
function Pagination({ page, pageCount, onChange }: { page: number; pageCount: number; onChange: (page: number) => void }) { if (pageCount === 1) return null; return <nav className="mt-6 flex items-center justify-between gap-4" aria-label="Paginação da fila"><button className="min-h-11 rounded-md border border-text-primary/25 px-4 text-base font-bold disabled:opacity-50" type="button" disabled={page === 0} onClick={() => onChange(page - 1)}>Anterior</button><p className="text-sm font-semibold text-text-muted">Página {page + 1} de {pageCount}</p><button className="min-h-11 rounded-md border border-text-primary/25 px-4 text-base font-bold disabled:opacity-50" type="button" disabled={page + 1 >= pageCount} onClick={() => onChange(page + 1)}>Próxima</button></nav>; }
