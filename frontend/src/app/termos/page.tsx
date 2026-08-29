import type { Metadata } from "next";
export const metadata: Metadata = { title: "Termos de Uso" };

export default function TermosPage() {
  return (
    <div className="container-custom py-10 max-w-3xl">
      <h1 className="text-3xl font-black text-zinc-900">Termos de Uso</h1>
      <div className="mt-8 prose prose-zinc max-w-none prose-p:leading-relaxed prose-headings:font-bold">
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
    </div>
  );
}
