"use client";

import { useState } from "react";

type Comment = { name: string; text: string; at: string };

function load(key: string): Comment[] {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

// Comentários locais (navegador) — engajamento imediato sem login.
// Quando o backend de comunidade existir, migra-se para API mantendo o layout.
export default function Comments({ slug, title }: { slug: string; title: string }) {
  const key = `pc-comments-${slug}`;
  const [items, setItems] = useState<Comment[]>(() => load(key));
  const [name, setName] = useState("");
  const [text, setText] = useState("");
  const [error, setError] = useState("");

  const send = () => {
    const n = name.trim().slice(0, 40);
    const t = text.trim().slice(0, 600);
    if (n.length < 2) {
      setError("Informe seu nome.");
      return;
    }
    if (t.length < 3) {
      setError("Escreva seu comentário.");
      return;
    }
    const next = [{ name: n, text: t, at: new Date().toISOString() }, ...items].slice(0, 100);
    setItems(next);
    try {
      localStorage.setItem(key, JSON.stringify(next));
    } catch {}
    setName("");
    setText("");
    setError("");
  };

  return (
    <section className="mt-10 rounded-2xl border border-zinc-100 bg-white p-5 shadow-sm" aria-label={`Comentários sobre ${title}`}>
      <h3 className="font-extrabold text-zinc-900">💬 Comentários {items.length > 0 && <span className="text-sm font-bold text-zinc-400">({items.length})</span>}</h3>

      <div className="mt-4 grid gap-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Seu nome"
          maxLength={40}
          className="w-full rounded-xl border border-zinc-200 px-4 py-2.5 text-sm outline-none focus:border-[#e63946]"
        />
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Participe da conversa…"
          rows={3}
          maxLength={600}
          className="w-full resize-y rounded-xl border border-zinc-200 px-4 py-2.5 text-sm outline-none focus:border-[#e63946]"
        />
        {error && <p className="text-xs font-bold text-[#e63946]">{error}</p>}
        <button
          onClick={send}
          className="justify-self-start rounded-full bg-[#e63946] px-6 py-2.5 text-sm font-bold text-white hover:brightness-110"
        >
          Comentar
        </button>
      </div>

      <div className="mt-6 space-y-4">
        {items.map((c, i) => (
          <div key={i} className="rounded-xl bg-zinc-50 p-4">
            <div className="flex items-baseline justify-between gap-2">
              <span className="text-sm font-extrabold text-zinc-800">{c.name}</span>
              <span className="shrink-0 text-[11px] text-zinc-400">
                {new Date(c.at).toLocaleDateString("pt-BR", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" })}
              </span>
            </div>
            <p className="mt-1 text-sm leading-relaxed text-zinc-700">{c.text}</p>
          </div>
        ))}
        {items.length === 0 && (
          <p className="text-sm text-zinc-400">Seja a primeira pessoa a comentar.</p>
        )}
      </div>
    </section>
  );
}
