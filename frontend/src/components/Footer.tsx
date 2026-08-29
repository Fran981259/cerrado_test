import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-[#1a1a2e] text-zinc-300 mt-16">
      <div className="container-custom py-12 grid gap-8 md:grid-cols-4">
        <div>
          <div className="text-xl font-black text-white">ATUALIZA<span className="text-[#e63946]">BRASIL</span></div>
          <p className="mt-3 text-sm leading-relaxed opacity-80">
            Portal de notícias de Mato Grosso do Sul. Política, economia, segurança, agronegócio e tecnologia com apuração 24h.
          </p>
        </div>
        <div>
          <h4 className="font-bold text-white text-sm">Editorias</h4>
          <ul className="mt-3 space-y-2 text-sm opacity-80">
            <li><Link href="/?cat=politics" className="hover:text-white">Política</Link></li>
            <li><Link href="/?cat=economy" className="hover:text-white">Economia</Link></li>
            <li><Link href="/?cat=security" className="hover:text-white">Segurança</Link></li>
            <li><Link href="/?cat=agriculture" className="hover:text-white">Agronegócio</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-white text-sm">Institucional</h4>
          <ul className="mt-3 space-y-2 text-sm opacity-80">
            <li><Link href="/sobre" className="hover:text-white">Sobre</Link></li>
            <li><Link href="/privacidade" className="hover:text-white">Privacidade</Link></li>
            <li><Link href="/termos" className="hover:text-white">Termos de uso</Link></li>
            <li><Link href="/contato" className="hover:text-white">Contato</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-white text-sm">Contato</h4>
          <p className="mt-3 text-sm opacity-80">
            contato@atualizabrasil.news<br />
            Campo Grande — MS
          </p>
          <p className="mt-4 text-xs opacity-60">© {new Date().getFullYear()} Atualiza Brasil. Todos os direitos reservados.</p>
        </div>
      </div>
      <div className="border-t border-white/10">
        <div className="container-custom py-4 text-xs opacity-60 flex flex-wrap gap-4 justify-between">
          <span>Conteúdo reescrito por repórteres de IA com revisão editorial.</span>
          <span>Feito com ♥ em MS</span>
        </div>
      </div>
    </footer>
  );
}
