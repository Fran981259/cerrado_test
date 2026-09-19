import type { Metadata } from "next";

export const metadata: Metadata = { title: "Sobre" };

export default function SobrePage() {
  return (
    <div className="bg-[linear-gradient(180deg,#09090b_0%,#18181b_100%)] py-14">
      <div className="container-custom max-w-4xl">
        <section className="overflow-hidden rounded-[2rem] border border-white/5 bg-[#09090b] shadow-[0_28px_90px_rgba(0,0,0,0.5)]">
          <div className="bg-white/5 p-8 text-white sm:p-12">
            <p className="text-xs font-black uppercase tracking-[0.28em] text-white/55">Mato Grosso do Sul • Jornalismo 24 horas</p>
            <h1 className="mt-4 font-display text-5xl font-black leading-none tracking-tight sm:text-7xl">Sobre o Portal Cerrado</h1>
          </div>

      <div className="content-page p-8 sm:p-12">
          <p>
            O <strong>Portal Cerrado</strong> dedica-se a cobrir os fatos de Mato Grosso do Sul com profundidade, abrangendo política, economia, segurança,
            agronegócio, saúde, educação, cultura e tecnologia. Nosso compromisso é informar com rigor, rapidez e o contexto que nossa região exige.
          </p>
          <h2>Nossa redação</h2>
          <p>
            Trabalhamos com uma equipe de repórteres especializados, cada um responsável por monitorar as dinâmicas de sua editoria. A curadoria humana está presente em todas as etapas, desde a apuração de fontes até a revisão final das matérias, garantindo a qualidade e a veracidade de tudo que publicamos.
          </p>
        <h2>Transparência</h2>
        <ul>
          <li>Citação obrigatória da fonte original com link</li>
          <li>Sem cópia integral — reescrita com voz própria</li>
          <li>Correções publicadas com nota de atualização</li>
          <li>Política clara de privacidade e termos de uso</li>
        </ul>
        <h2>Fale conosco</h2>
        <p>
          Sugestões, correções ou parcerias? Escreva para <a href="mailto:contato@portalcerrado.com.br">contato@portalcerrado.com.br</a> ou use a página de{" "}
          <a href="/contato">contato</a>.
        </p>
      </div>
        </section>
      </div>
    </div>
  );
}
