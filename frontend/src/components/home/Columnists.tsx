import Link from "next/link";
import { REPORTERS, reporterInitials, type ReporterBio } from "@/lib/reporters";
import { fetchNewsResponse } from "@/lib/api";
import { getCategory } from "@/lib/categories";
import { formatRelativeTime } from "@/lib/time";
import { SectionHeading } from "./SectionHeading";
import type { Article } from "@/lib/api";

const COLUMNIST_SLUGS = ["luciana.freitas", "camila.rocha", "bia.fernandes", "rafael.dumas", "maya.santos", "leon.vaz", "enzo.bianchi", "marcus.teixeira"];

type ColumnistEntry = {
  slug: string;
  bio: ReporterBio;
  latest?: Article;
};

async function loadColumnists(): Promise<ColumnistEntry[]> {
  const settled = await Promise.allSettled(
    COLUMNIST_SLUGS.map((slug) => fetchNewsResponse({ reporterSlug: slug, limit: 1, sortBy: "recent" }).then((res) => res.news[0])),
  );
  return COLUMNIST_SLUGS.map((slug, index) => ({
    slug,
    bio: REPORTERS[slug],
    latest: settled[index].status === "fulfilled" && settled[index].value ? settled[index].value : undefined,
  }));
}

function latestHref(article: Article): string {
  return article.slug ? `/noticia/${article.slug}` : article.url || "#";
}

export async function Columnists() {
  const entries = await loadColumnists();

  return (
    <section aria-labelledby="colunistas-heading" className="container-editorial py-10">
      <SectionHeading eyebrow="Colunistas" title="Assinaturas do Portal" id="colunistas-heading" href="/contato" linkLabel="seja um colunista" />
      <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {entries.map(({ slug, bio, latest }) => (
          <article key={slug} className="flex h-full flex-col rounded-md border border-black/10 bg-surface p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <span aria-hidden="true" className="grid h-11 w-11 shrink-0 place-items-center rounded-full bg-gold font-display text-sm font-bold text-charcoal">
                {reporterInitials(bio.name)}
              </span>
              <div className="min-w-0">
                <h3 className="truncate font-display text-base font-bold text-text-primary">{bio.name}</h3>
                <p className="truncate text-[11px] uppercase tracking-wider text-text-muted">{bio.beat}</p>
              </div>
            </div>
            <p className="mt-3 line-clamp-2 text-xs leading-relaxed text-text-muted">{bio.bio}</p>
            <div className="mt-auto pt-4">
              {latest ? (
                <Link href={latestHref(latest)} className="group block border-t border-black/8 pt-3" aria-label={`Última coluna de ${bio.name}: ${latest.title}`}>
                  <span className="text-[10px] font-black uppercase tracking-wider text-accent-soil">{getCategory(latest.category).label}</span>
                  <h4 className="mt-1 line-clamp-2 font-display text-[15px] font-bold leading-snug text-text-primary transition-colors group-hover:text-accent-soil">{latest.title}</h4>
                  <span className="mt-1 block text-[11px] text-text-muted">{formatRelativeTime(latest.published_at)}</span>
                </Link>
              ) : (
                <p className="border-t border-black/8 pt-3 text-[11px] text-text-muted">Sem colunas publicadas ainda.</p>
              )}
              <Link href={`/reporter/${slug}`} className="mt-3 inline-flex items-center gap-2 text-[11px] font-bold uppercase tracking-wider text-accent-soil transition-colors hover:text-gold-deep">
                Ver perfil
                <span aria-hidden="true">→</span>
              </Link>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}