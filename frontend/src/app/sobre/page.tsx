import type { Metadata } from "next";

export const metadata: Metadata = { title: "Sobre" };

export default function SobrePage() {
  return (
    <div className="container-custom py-10 max-w-3xl">
      <h1 className="text-3xl font-black tracking-tight text-zinc-900">Sobre o Atualiza Brasil</h1>
      <p className="mt-2 text-sm font-semibold text-[#e63946]">Mato Grosso do Sul • Jornalismo 24 horas</p>

      <div className="mt-8 prose prose-zinc max-w-none prose-p:leading-relaxed prose-headings:font-extrabold">
        <p>
          O <strong>Atualiza Brasil</strong> é um portal de notícias focado em Mato Grosso do Sul, com cobertura de política, economia, segurança,
          agronegócio, saúde, educação, cultura e tecnologia. Nosso compromisso é informar com rapidez, precisão e contexto local.
        </p>
        <h2>Como produzimos</h2>
        <p>
          Utilizamos um sistema automatizado de mineração de fontes públicas (RSS e portais com permissão) e reescrita por repórteres digitais com
          vozes especializadas. Cada matéria cita a fonte original, passa por filtros de duplicata e sensível, e recebe classificação por relevância.
        </p>
        <h2>Equipe</h2>
        <p>
          Nove repórteres digitais assinam as editorias, cada um com especialidade e tom próprio. A curadoria humana supervisiona auditoria, correções
          e evolução editorial.
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
          Sugestões, correções ou parcerias? Escreva para <a href="mailto:contato@atualizabrasil.news" className="text-[#e63946] font-bold">contato@atualizabrasil.news</a> ou use a página de{" "}
          <a href="/contato" className="text-[#e63946] font-bold">contato</a>.
        </p>
      </div>
    </div>
  );
}
