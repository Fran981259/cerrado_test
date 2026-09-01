import type { Metadata } from "next";
export const metadata: Metadata = { title: "Política de Privacidade" };

export default function PrivacidadePage() {
  return (
    <div className="container-custom py-10 max-w-3xl">
      <h1 className="text-3xl font-black text-zinc-900">Política de Privacidade</h1>
      <p className="mt-2 text-sm text-zinc-500">Última atualização: {new Date().toLocaleDateString("pt-BR")}</p>
      <div className="mt-8 prose prose-zinc max-w-none prose-p:leading-relaxed prose-headings:font-bold">
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
    </div>
  );
}
