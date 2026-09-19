import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'Contato' };

export default function ContatoPage() {
  return (
    <div className="bg-canvas py-14">
      <div className="container-editorial max-w-3xl">
        <section className="border-y-2 border-charcoal">
          <div className="border-b border-black/10 py-8 text-text-primary sm:py-12">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-gold-deep">
              Redação aberta
            </p>
            <h1 className="mt-4 font-display text-5xl font-black leading-none tracking-tight sm:text-7xl">
              Fale com o Portal Cerrado
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-relaxed text-text-muted">
              Sugestões de pauta, correções, denúncias documentadas e parcerias comerciais entram
              por um canal direto com a redação.
            </p>
          </div>
          <div className="grid gap-6 py-8 md:grid-cols-[1fr_320px] sm:py-10">
            <div>
              <h2 className="font-display text-3xl font-black text-text-primary">
                Envie sua mensagem
              </h2>
              <p className="mt-3 leading-relaxed text-text-muted">
                Para acelerar a apuração, inclua cidade, data, contexto, documentos públicos quando
                houver e um telefone de retorno.
              </p>
              <a
                href="mailto:contato@portalcerrado.com.br"
                className="mt-7 inline-flex rounded bg-accent-soil px-6 py-3 font-black text-white transition-colors hover:bg-text-primary"
              >
                contato@portalcerrado.com.br
              </a>
            </div>
            <div className="border-l-4 border-gold bg-surface p-6 text-sm text-text-muted">
              <p className="font-black uppercase tracking-widest text-accent-soil">Atendimento</p>
              <p className="mt-4 font-semibold text-text-primary">
                Campo Grande • Mato Grosso do Sul
              </p>
              <p className="mt-3">
                O portal ainda não oferece formulário de envio nem assinatura de newsletter.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
