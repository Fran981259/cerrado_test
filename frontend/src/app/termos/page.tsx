import type { Metadata } from "next";
export const metadata: Metadata = { title: "Termos de Uso" };

export default function TermosPage() {
  return (
    <div className="bg-[linear-gradient(180deg,#fdfbf7_0%,#f7f1e8_100%)] py-14">
      <div className="container-custom max-w-4xl">
        <section className="overflow-hidden rounded-[2rem] border border-black/5 bg-white shadow-[0_28px_90px_rgba(45,41,38,0.12)]">
          <div className="bg-text-primary p-8 text-white sm:p-12">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-white/55">Regras editoriais e de uso</p>
            <h1 className="mt-4 font-display text-5xl font-black leading-none tracking-tight sm:text-7xl">Termos de Uso</h1>
          </div>
      <div className="content-page p-8 sm:p-12">
        <h2>Uso do conteúdo</h2>
        <p>
          O conteúdo é protegido por direitos autorais. É permitido compartilhar trechos com crédito e link para a matéria original. Reprodução
          integral sem autorização é proibida (Lei 9.610/98).
        </p>
        <h2>Fontes</h2>
        <p>Todas as matérias citam a fonte original. Buscamos reescrita com voz própria e sem plágio.</p>
        <h2>Responsabilidade</h2>
        <p>Notícias são baseadas em fontes públicas no momento da publicação. Correções são indicadas com nota de atualização.</p>
        <h2>Comentários</h2>
        <p>Comentários ofensivos, discriminatórios ou com desinformação podem ser removidos.</p>
        <h2>Foro</h2>
        <p>Fica eleito o foro de Campo Grande/MS para dirimir dúvidas destes termos.</p>
      </div>
        </section>
      </div>
    </div>
  );
}
