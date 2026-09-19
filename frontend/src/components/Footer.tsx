import Link from "next/link";
import { REPORTER_LIST, reporterInitials } from "@/lib/reporters";

const CITIES = ["Campo Grande", "Dourados", "Três Lagoas", "Corumbá", "Ponta Porã", "Aquidauana", "Jardim", "Naviraí", "Nova Andradina", "São Gabriel do Oeste", "Paranaíba", "Sidrolândia", "Chapadão do Sul", "Coxim"];

const EDITORIAS = [
  { label: "Política e Poder", href: "/categoria/politics" },
  { label: "Polícia e Justiça", href: "/categoria/security" },
  { label: "Economia", href: "/categoria/economy" },
  { label: "Agronegócio", href: "/categoria/agriculture" },
  { label: "Cotidiano e Clima", href: "/categoria/clima" },
  { label: "Esporte", href: "/categoria/sports" },
  { label: "Cultura e Entretenimento", href: "/categoria/culture" },
  { label: "Ciência e Tecnologia", href: "/categoria/tech" },
];

const INSTITUCIONAL = [
  { label: "Sobre Nós", href: "/sobre" },
  { label: "Privacidade", href: "/privacidade" },
  { label: "Termos de uso", href: "/termos" },
  { label: "Contato", href: "/contato" },
];

export default function Footer() {
  return (
    <footer className="mt-10 border-t-2 border-accent-soil bg-surface">
      <div className="container-editorial grid gap-10 py-12 md:grid-cols-2 lg:grid-cols-4">
        <div>
          <div className="flex items-center gap-3">
            <span aria-hidden="true" className="grid h-10 w-10 place-items-center rounded bg-accent-soil font-display text-base font-bold text-white">
              PC
            </span>
            <span className="font-display text-2xl font-bold tracking-tight text-text-primary">
              Portal <span className="text-accent-soil">Cerrado</span>
            </span>
          </div>
          <p className="mt-4 text-sm leading-relaxed text-text-muted">
            Jornalismo sério sobre agronegócio, mercados e negócios regionais. Produzido em Mato Grosso do Sul, com apuração a partir de fontes públicas e da imprensa local de cada cidade.
          </p>
          <p className="mt-4 text-xs leading-relaxed text-text-muted">
            Acompanhamos as principais cidades do Estado:
            <span className="mt-1 block font-medium">{CITIES.join(" · ")}.</span>
          </p>
        </div>

        <div>
          <h4 className="border-b border-black/10 pb-2 text-xs font-black uppercase tracking-[0.18em] text-accent-soil">Editorias</h4>
          <ul className="mt-4 space-y-2.5 text-sm">
            {EDITORIAS.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-text-muted transition-colors hover:text-accent-soil hover:underline hover:decoration-gold decoration-2 underline-offset-2">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h4 className="border-b border-black/10 pb-2 text-xs font-black uppercase tracking-[0.18em] text-accent-soil">Institucional</h4>
          <ul className="mt-4 space-y-2.5 text-sm">
            {INSTITUCIONAL.map((item) => (
              <li key={item.href}>
                <Link href={item.href} className="text-text-muted transition-colors hover:text-accent-soil hover:underline hover:decoration-gold decoration-2 underline-offset-2">
                  {item.label}
                </Link>
              </li>
            ))}
          </ul>
          <p className="mt-5 text-xs leading-relaxed text-text-muted">Redação em Campo Grande — MS.</p>
        </div>

        <div>
          <h4 className="border-b border-black/10 pb-2 text-xs font-black uppercase tracking-[0.18em] text-accent-soil">Colunistas</h4>
          <ul className="mt-4 space-y-2.5 text-sm">
            {REPORTER_LIST.filter((r) => r.slug !== "redacao.cerrado")
              .slice(0, 7)
              .map((reporter) => (
                <li key={reporter.slug} className="flex items-center gap-2.5">
                  <span aria-hidden="true" className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-gold/20 text-[10px] font-bold text-gold-deep">
                    {reporterInitials(reporter.name)}
                  </span>
                  <Link href={`/reporter/${reporter.slug}`} className="truncate text-text-muted transition-colors hover:text-accent-soil hover:underline hover:decoration-gold decoration-2 underline-offset-2">
                    {reporter.name}
                  </Link>
                </li>
              ))}
          </ul>
        </div>
      </div>
      <div className="border-t border-black/10">
        <div className="container-editorial flex flex-wrap items-center justify-between gap-4 py-5 text-xs text-text-muted">
          <span>© {new Date().getFullYear()} Portal Cerrado. Todos os direitos reservados.</span>
          <span>Jornalismo local com rigor editorial.</span>
        </div>
      </div>
    </footer>
  );
}