import Link from "next/link";
import { REPORTERS, reporterInitials, type ReporterBio } from "@/lib/reporters";
import { fetchNewsResponse } from "@/lib/api";
import { getCategory } from "@/lib/categories";
import { formatRelativeTime } from "@/lib/time";
import { SectionHeading } from "./SectionHeading";
import type { Article } from "@/lib/api";
import { ArticleImage } from "./ArticleImage";

const COLUMNIST_SLUGS = ["luciana.freitas", "camila.rocha", "bia.fernandes", "rafael.dumas", "maya.santos", "leon.vaz", "enzo.bianchi", "marcus.teixeira"];

type ColumnistEntry = {
  slug: string;
  bio: ReporterBio;
  latest?: Article;
};

async function loadColumnists(): Promise<ColumnistEntry[]> {
  const settled = await Promise.allSettled(
    COLUMNIST_SLUGS.map((slug) => fetchNewsResponse({ reporterSlug: slug, region: "ms", limit: 1, sortBy: "recent" }).then((res) => res.news[0])),
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
  const publishedEntries = entries.filter(
    (entry): entry is ColumnistEntry & { latest: Article } => Boolean(entry.latest),
  );

  if (publishedEntries.length === 0) return null;

  return (
    <section aria-labelledby="colunistas-heading" className="container-editorial py-9">
      <SectionHeading eyebrow="Por quem apura" title="Últimas assinaturas do Portal" id="colunistas-heading" href="/contato" linkLabel="fale com a redação" />
      <div className="mt-6 grid gap-x-6 gap-y-8 sm:grid-cols-2 lg:grid-cols-4">
        {publishedEntries.map(({ slug, bio, latest }) => (
          <article key={slug} className="group min-w-0">
            <Link href={latestHref(latest)} className="block" aria-label={`Matéria de ${bio.name}: ${latest.title}`}>
              <ArticleImage article={latest} showBadge={false} sizes="(max-width: 640px) 100vw, 25vw" className="aspect-[16/10] rounded-md" />
              <p className="mt-3 text-[10px] font-black uppercase tracking-[0.16em] text-accent-soil">{getCategory(latest.category).label}</p>
              <h3 className="mt-1.5 line-clamp-3 font-display text-xl font-bold leading-tight text-text-primary transition-colors group-hover:text-accent-soil">{latest.title}</h3>
            </Link>
            <div className="mt-3 flex items-center justify-between gap-3 text-xs text-text-muted">
              <Link href={`/reporter/${slug}`} className="inline-flex min-w-0 items-center gap-2 font-bold text-text-primary transition-colors hover:text-accent-soil">
                <span aria-hidden="true" className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-gold font-display text-[10px] font-bold text-charcoal">
                  {reporterInitials(bio.name)}
                </span>
                <span className="truncate">{bio.name}</span>
              </Link>
              <span className="shrink-0">{formatRelativeTime(latest.published_at)}</span>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
