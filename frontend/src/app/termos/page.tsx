import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'Termos de Uso' };

export default function TermosPage() {
  return (
    <div className="bg-canvas py-14">
      <div className="container-editorial max-w-4xl">
        <section className="border-y-2 border-charcoal">
          <div className="border-b border-black/10 py-8 sm:py-12">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-gold-deep">
              Regras editoriais e de uso
            </p>
            <h1 className="mt-4 font-display text-5xl font-black leading-none tracking-tight sm:text-7xl">
              Termos de Uso
            </h1>
          </div>
          <div className="content-page py-8 sm:py-12">
            <h2>Uso do conteúdo</h2>
            <p>
              O conteúdo é protegido por direitos autorais. É permitido compartilhar trechos com
              crédito e link para a matéria original. Reprodução integral sem autorização é proibida
              (Lei 9.610/98).
            </p>
            <h2>Fontes</h2>
            <p>
              Todas as matérias citam a fonte original. Buscamos reescrita com voz própria e sem
              plágio.
            </p>
            <h2>Responsabilidade</h2>
            <p>
              Notícias são baseadas em fontes públicas no momento da publicação. Correções são
              indicadas com nota de atualização.
            </p>
            <h2>Canais de contato</h2>
            <p>
              O portal não mantém comentários públicos enquanto não houver uma moderação e uma
              política de comunidade implementadas.
            </p>
            <h2>Foro</h2>
            <p>Fica eleito o foro de Campo Grande/MS para dirimir dúvidas destes termos.</p>
          </div>
        </section>
      </div>
    </div>
  );
}
