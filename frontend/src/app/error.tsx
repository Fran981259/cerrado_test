"use client";

export default function ErrorPage({ reset }: { reset: () => void }) {
  return <div role="alert" className="bg-[linear-gradient(180deg,#fdfbf7_0%,#f7f1e8_100%)] py-16">
    <div className="container-custom max-w-2xl text-center">
      <div className="rounded-[2rem] border border-black/5 bg-white p-10 shadow-[0_28px_90px_rgba(45,41,38,0.12)]">
        <p className="text-xs font-black uppercase tracking-[0.28em] text-accent-soil">Instabilidade</p>
        <h1 className="mt-3 font-display text-4xl font-black text-text-primary">Conteúdo temporariamente indisponível</h1>
        <p className="my-5 text-text-muted">Não foi possível consultar o portal. Tente novamente em instantes.</p>
        <button onClick={reset} className="rounded-full bg-text-primary px-5 py-3 font-black text-white hover:bg-accent-soil">Tentar novamente</button>
      </div>
    </div>
  </div>;
}
