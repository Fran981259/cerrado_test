import Link from "next/link";
import { getReporter } from "@/lib/reporters";
import { formatRelativeTime } from "@/lib/time";
import type { Article } from "@/lib/api";
import { SectionHeading } from "./SectionHeading";

function hrefOf(article: Article): string {
  return article.slug ? `/noticia/${article.slug}` : article.url || "#";
}

function PoderColumn({ title, articles }: { title: string; articles: Article[] }) {
  return (
    <div>
      <h3 className="flex items-center gap-2 border-b border-white/15 pb-2 text-[11px] font-black uppercase tracking-[0.2em] text-gold">
        <span className="h-1.5 w-1.5 rounded-full bg-gold" aria-hidden="true" />
        {title}
      </h3>
      {articles.length === 0 ? (
        <p className="mt-4 text-sm text-white/50">Sem conteúdo recente.</p>
      ) : (
        <ul className="mt-3 space-y-5">
          {articles.slice(0, 2).map((article) => (
            <li key={article.slug || article.title}>
              <Link href={hrefOf(article)} className="group block" aria-label={`${title}: ${article.title}`}>
                <span className="text-[11px] text-white/50">{formatRelativeTime(article.published_at)}</span>
                <h4 className="mt-1 font-display text-[17px] font-bold leading-snug text-white transition-colors group-hover:text-gold">{article.title}</h4>
                <span className="mt-1.5 block text-[11px] font-semibold text-white/60">{getReporter(article.reporter_slug).name}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function PoderModule({
  politics,
  economy,
  security,
  rural,
}: {
  politics: Article[];
  economy: Article[];
  security: Article[];
  rural: Article[];
}) {
  return (
    <section aria-labelledby="poder-heading" className="bg-charcoal text-white">
      <div className="container-editorial py-10">
        <SectionHeading eyebrow="Poder & Negócios" title="Poder, política e dinheiro público" id="poder-heading" dark />
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-white/60">Acompanhamento direto do que move decisões e recursos em Mato Grosso do Sul.</p>
        <div className="mt-8 grid gap-x-8 gap-y-10 border-t border-white/10 pt-8 sm:grid-cols-2 lg:grid-cols-4">
          <PoderColumn title="Política" articles={politics} />
          <PoderColumn title="Economia" articles={economy} />
          <PoderColumn title="Segurança" articles={security} />
          <PoderColumn title="Agro & Rural" articles={rural} />
        </div>
        <p className="mt-8 text-xs text-white/50">
          Acesse todas as editorias: <Link href="/categoria/politics" className="font-semibold text-gold underline decoration-gold/40 underline-offset-2 hover:text-white">Política</Link> ·{" "}
          <Link href="/categoria/economy" className="font-semibold text-gold underline decoration-gold/40 underline-offset-2 hover:text-white">Economia</Link> ·{" "}
          <Link href="/categoria/security" className="font-semibold text-gold underline decoration-gold/40 underline-offset-2 hover:text-white">Polícia e Justiça</Link>
        </p>
      </div>
    </section>
  );
}