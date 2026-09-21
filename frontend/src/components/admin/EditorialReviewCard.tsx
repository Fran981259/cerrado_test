"use client";

import { useState } from "react";
import { CATEGORY_LIST } from "@/lib/categories";
import {
  type EditorialArticle,
  type EditorialChanges,
  type EditorialStatus,
  updateEditorialArticle,
} from "@/lib/editorialApi";

const STATUS_OPTIONS: Array<{ value: EditorialStatus; label: string }> = [
  { value: "draft", label: "Rascunho" },
  { value: "classified", label: "Classificada" },
  { value: "review", label: "Revisão" },
  { value: "rewritten", label: "Reescrita" },
  { value: "published", label: "Publicar" },
  { value: "failed", label: "Rejeitada" },
];

type Props = {
  article: EditorialArticle;
  apiKey: string;
  onSaved: (changes: EditorialChanges) => void;
};

/** Displays one editable editorial decision without publishing automatically. */
export function EditorialReviewCard({ article, apiKey, onSaved }: Props) {
  const [changes, setChanges] = useState<EditorialChanges>({
    category: article.category,
    importance_score: article.importance_score ?? 0,
    engagement_score: article.engagement_score ?? 0,
    status: article.status,
  });
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState("");

  const save = async () => {
    setIsSaving(true);
    setMessage("");
    try {
      await updateEditorialArticle(apiKey, article.slug, changes);
      onSaved(changes);
      setMessage("Revisão salva.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "A revisão não foi salva.");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <article className="rounded-lg border border-text-primary/15 bg-surface p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <p className="eyebrow">{article.status}</p>
          <h2 className="mt-2 font-display text-xl font-bold leading-tight text-text-primary">{article.title}</h2>
          {article.summary && <p className="mt-3 text-base leading-relaxed text-text-muted">{article.summary}</p>}
        </div>
        <a className="text-sm font-semibold text-accent-soil underline" href={`/noticia/${article.slug}`} target="_blank" rel="noreferrer">
          Abrir matéria
        </a>
      </div>

      {!!article.writing_review?.length && (
        <p className="mt-4 rounded-md bg-canvas p-3 text-sm text-text-muted">
          {article.writing_review.length} alerta{article.writing_review.length === 1 ? "" : "s"} de redação detectado{article.writing_review.length === 1 ? "" : "s"}.
        </p>
      )}

      <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <label className="grid gap-2 text-sm font-semibold text-text-primary">
          Categoria
          <select
            className="min-h-11 rounded-md border border-text-primary/20 bg-surface px-3 text-base font-normal"
            value={changes.category}
            onChange={(event) => setChanges((current) => ({ ...current, category: event.target.value }))}
          >
            {CATEGORY_LIST.map((category) => <option key={category.slug} value={category.slug}>{category.label}</option>)}
          </select>
        </label>
        <ScoreInput label="Relevância" value={changes.importance_score} onChange={(importance_score) => setChanges((current) => ({ ...current, importance_score }))} />
        <ScoreInput label="Engajamento" value={changes.engagement_score} onChange={(engagement_score) => setChanges((current) => ({ ...current, engagement_score }))} />
        <label className="grid gap-2 text-sm font-semibold text-text-primary">
          Decisão
          <select
            className="min-h-11 rounded-md border border-text-primary/20 bg-surface px-3 text-base font-normal"
            value={changes.status}
            onChange={(event) => setChanges((current) => ({ ...current, status: event.target.value as EditorialStatus }))}
          >
            {STATUS_OPTIONS.map((status) => <option key={status.value} value={status.value}>{status.label}</option>)}
          </select>
        </label>
      </div>

      <div className="mt-5 flex flex-wrap items-center gap-3">
        <button className="min-h-11 rounded-md bg-accent-soil px-4 text-base font-bold text-surface disabled:cursor-not-allowed disabled:opacity-60" type="button" onClick={save} disabled={isSaving}>
          {isSaving ? "Salvando…" : "Salvar revisão"}
        </button>
        {message && <p className="text-sm font-semibold text-text-muted" role="status">{message}</p>}
      </div>
    </article>
  );
}

type ScoreInputProps = { label: string; value: number | null | undefined; onChange: (value: number) => void };

/** Collects a bounded editorial score and rejects invalid browser input. */
function ScoreInput({ label, value, onChange }: ScoreInputProps) {
  return (
    <label className="grid gap-2 text-sm font-semibold text-text-primary">
      {label}
      <input
        className="min-h-11 rounded-md border border-text-primary/20 bg-surface px-3 text-base font-normal"
        type="number"
        min="0"
        max="100"
        value={value ?? 0}
        onChange={(event) => onChange(Math.max(0, Math.min(100, Number(event.target.value) || 0)))}
      />
    </label>
  );
}
