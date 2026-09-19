import Link from "next/link";

export default function Footer() {
  return (
    <footer className="mt-16 bg-[#040405] text-zinc-300 border-t border-white/5">
      <div className="container-custom grid gap-8 py-14 md:grid-cols-[1.5fr_1fr_1fr_1.2fr]">
        <div>
          <div className="font-display text-3xl font-black text-white">Portal<span className="text-accent-soil"> Cerrado</span></div>
          <p className="mt-3 text-sm leading-relaxed opacity-80">
            Tudo que acontece em Campo Grande e nas principais cidades de Mato Grosso do Sul com isenção e credibilidade. Política, economia, segurança, agronegócio, clima e tecnologia com apuração 24h.
          </p>
          <div className="mt-4 flex gap-2">
            <a href="https://facebook.com" target="_blank" rel="noopener" aria-label="Facebook" className="grid h-8 w-8 place-items-center rounded-full bg-white/10 hover:bg-white hover:text-text-primary"><i className="fi fi-rr-share text-xs" /></a>
            <a href="https://instagram.com" target="_blank" rel="noopener" aria-label="Instagram" className="grid h-8 w-8 place-items-center rounded-full bg-white/10 hover:bg-white hover:text-text-primary"><i className="fi fi-rr-camera text-xs" /></a>
            <a href="https://x.com" target="_blank" rel="noopener" aria-label="X" className="grid h-8 w-8 place-items-center rounded-full bg-white/10 hover:bg-white hover:text-text-primary"><i className="fi fi-rr-paper-plane text-xs" /></a>
          </div>
        </div>
        <div>
          <h4 className="font-bold text-white text-sm">Editorias</h4>
          <ul className="mt-3 space-y-2 text-sm opacity-80">
            <li><Link href="/categoria/politics" className="hover:text-white">Política e Poder</Link></li>
            <li><Link href="/categoria/security" className="hover:text-white">Polícia e Justiça</Link></li>
            <li><Link href="/categoria/clima" className="hover:text-white">Cotidiano</Link></li>
            <li><Link href="/categoria/sports" className="hover:text-white">Esporte</Link></li>
            <li><Link href="/categoria/economy" className="hover:text-white">Economia e Agronegócio</Link></li>
            <li><Link href="/categoria/culture" className="hover:text-white">Cultura e Entretenimento</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-white text-sm">Institucional</h4>
          <ul className="mt-3 space-y-2 text-sm opacity-80">
            <li><Link href="/sobre" className="hover:text-white">Sobre Nós</Link></li>
            <li><Link href="/privacidade" className="hover:text-white">Privacidade</Link></li>
            <li><Link href="/termos" className="hover:text-white">Termos de uso</Link></li>
            <li><Link href="/contato" className="hover:text-white">Contato</Link></li>
            <li><Link href="/sobre" className="hover:text-white">Expediente</Link></li>
            <li><Link href="/contato" className="hover:text-white">Reportar News</Link></li>
          </ul>
        </div>
        <div>
          <h4 className="font-bold text-white text-sm">Contato</h4>
          <p className="mt-3 text-sm opacity-80">
            <span className="font-semibold text-white">(67) 3042-4141</span><br />
            contato@portalcerrado.com.br<br />
            Campo Grande — MS
          </p>
          <p className="mt-3 text-xs leading-relaxed opacity-60">Informe Publicitário • Capital Play • Oportunidades • Rural</p>
          <p className="mt-4 text-xs opacity-60">© {new Date().getFullYear()} Portal Cerrado. Todos os direitos reservados.</p>
        </div>
      </div>
      <div className="border-t border-white/10">
        <div className="container-custom py-4 text-xs opacity-60 flex flex-wrap gap-4 justify-between">
          <span>Jornalismo sério com compromisso local.</span>
          <span>Produzido em Mato Grosso do Sul — paleta Cerrado</span>
        </div>
      </div>
    </footer>
  );
}
