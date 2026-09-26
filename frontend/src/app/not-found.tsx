import Link from "next/link";

/** Editorial fallback for unknown public routes and articles. */
export default function NotFound() {
  return (
    <div className="bg-canvas py-16">
      <div className="container-custom mx-auto max-w-2xl text-center">
        <div className="rounded-[2rem] bg-surface p-10 shadow-[0_28px_90px_rgba(45,41,38,0.12)]">
          <p className="eyebrow">404</p>
          <h1 className="mt-3 font-display text-4xl font-black text-text-primary">Página não encontrada</h1>
          <p className="my-5 text-base text-text-muted">O conteúdo que você procura não está disponível nesta edição.</p>
          <Link href="/" className="inline-flex min-h-11 items-center rounded-full bg-text-primary px-5 py-3 font-black text-white hover:bg-accent-soil">Voltar para a capa</Link>
        </div>
      </div>
    </div>
  );
}
