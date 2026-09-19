import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'Política de Privacidade' };

export default function PrivacidadePage() {
  return (
    <div className="bg-canvas py-14">
      <div className="container-editorial max-w-4xl">
        <section className="border-y-2 border-charcoal">
          <div className="border-b border-black/10 py-8 sm:py-12">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-gold-deep">
              Privacidade e dados pessoais
            </p>
            <h1 className="mt-4 font-display text-5xl font-black leading-none tracking-tight sm:text-7xl">
              Política de Privacidade
            </h1>
          </div>
          <div className="content-page py-8 sm:py-12">
            <p>
              Esta política descreve como o Portal Cerrado trata dados pessoais de visitantes e
              contatos.
            </p>
            <h2>Dados coletados</h2>
            <ul>
              <li>
                Dados técnicos de navegação, como caminho acessado e página de origem, para medir o
                uso do portal
              </li>
              <li>E-mail e informações enviadas voluntariamente pelo canal de contato</li>
              <li>Não coletamos dados sensíveis sem consentimento</li>
            </ul>
            <h2>Cookies</h2>
            <p>
              O portal pode usar recursos técnicos essenciais do navegador. Você pode gerenciar
              cookies nas configurações do navegador.
            </p>
            <h2>Compartilhamento</h2>
            <p>
              Não vendemos dados pessoais. O compartilhamento, quando necessário, limita-se aos
              provedores técnicos indispensáveis para hospedagem e operação do portal.
            </p>
            <h2>Seus direitos</h2>
            <p>
              Você pode solicitar acesso, correção ou exclusão dos seus dados pelo e-mail
              contato@portalcerrado.com.br.
            </p>
            <h2>Contato do encarregado</h2>
            <p>Encarregado (DPO): contato@portalcerrado.com.br</p>
          </div>
        </section>
      </div>
    </div>
  );
}
