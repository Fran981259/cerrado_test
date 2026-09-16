import type { Metadata } from "next";
export const metadata: Metadata = { title: "Política de Privacidade" };

export default function PrivacidadePage() {
  return (
    <div className="bg-[linear-gradient(180deg,#fdfbf7_0%,#f7f1e8_100%)] py-14">
      <div className="container-custom max-w-4xl">
        <section className="overflow-hidden rounded-[2rem] border border-black/5 bg-white shadow-[0_28px_90px_rgba(45,41,38,0.12)]">
          <div className="bg-text-primary p-8 text-white sm:p-12">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-white/55">Última atualização: {new Date().toLocaleDateString("pt-BR")}</p>
            <h1 className="mt-4 font-display text-5xl font-black leading-none tracking-tight sm:text-7xl">Política de Privacidade</h1>
          </div>
      <div className="content-page p-8 sm:p-12">
        <p>Respeitamos sua privacidade e cumprimos a LGPD (Lei 13.709/2018).</p>
        <h2>Dados coletados</h2>
        <ul>
          <li>Dados de navegação (cookies, analytics) para melhorar a experiência</li>
          <li>E-mail, apenas se você assinar newsletter ou enviar contato</li>
          <li>Não coletamos dados sensíveis sem consentimento</li>
        </ul>
        <h2>Cookies</h2>
        <p>Usamos cookies essenciais e de analytics (ex.: Google Analytics/AdSense). Você pode bloquear cookies no navegador.</p>
        <h2>Compartilhamento</h2>
        <p>Não vendemos seus dados. Compartilhamos apenas com provedores necessários (hospedagem, analytics, e-mail).</p>
        <h2>Seus direitos</h2>
        <p>Você pode solicitar acesso, correção ou exclusão dos seus dados pelo e-mail contato@portalcerrado.com.br.</p>
        <h2>Contato do encarregado</h2>
        <p>Encarregado (DPO): contato@portalcerrado.com.br</p>
      </div>
        </section>
      </div>
    </div>
  );
}
