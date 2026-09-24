"use client";

import { useState } from "react";

type ArticleShareActionsProps = {
  title: string;
  url: string;
};

/** Offers native sharing and link copying without moving the article page to the client. */
export function ArticleShareActions({ title, url }: ArticleShareActionsProps) {
  const [shareStatus, setShareStatus] = useState<"idle" | "copied" | "error">("idle");

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(url);
      setShareStatus("copied");
    } catch {
      setShareStatus("error");
    }
  }

  async function shareArticle() {
    try {
      if (navigator.share) {
        await navigator.share({ title, url });
        return;
      }
      await copyLink();
    } catch {
      setShareStatus("error");
    }
  }

  return (
    <div role="group" aria-label="Compartilhar matéria" className="flex flex-wrap gap-3">
      <button
        type="button"
        onClick={shareArticle}
        className="min-h-11 rounded-full border border-black/10 bg-white px-4 text-sm font-black text-text-primary transition hover:border-accent-soil hover:text-accent-soil"
      >
        Compartilhar
      </button>
      <button
        type="button"
        onClick={copyLink}
        className="min-h-11 rounded-full bg-accent-soil px-4 text-sm font-black text-white transition hover:bg-text-primary"
      >
        {shareStatus === "copied" ? "Link copiado" : "Copiar link"}
      </button>
      <a
        href={`https://wa.me/?text=${encodeURIComponent(`${title} ${url}`)}`}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-flex min-h-11 items-center rounded-full border border-black/10 bg-white px-4 text-sm font-black text-text-primary transition hover:border-accent-soil hover:text-accent-soil"
      >
        WhatsApp
      </a>
      <p aria-live="polite" className="sr-only">
        {shareStatus === "copied" && "Link copiado para a área de transferência."}
        {shareStatus === "error" && "Não foi possível copiar ou compartilhar o link."}
      </p>
    </div>
  );
}
