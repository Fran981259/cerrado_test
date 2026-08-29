import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { fetchArticleBySlug, fetchNews, MOCK_ARTICLES } from "@/lib/api";
import { getCategory, PATTERN_IMAGES } from "@/lib/categories";
import { getReporter } from "@/lib/reporters";

export const revalidate = 60;

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const article = (await fetchArticleBySlug(slug)) ?? MOCK_ARTICLES.find((a) => a.slug === slug) ?? null;
  if (!article) return { title: "Notícia não encontrada" };
  return {
    title: article.title,
    description: article.summary || article.title,
    openGraph: { title: article.title, description: article.summary, type: "article" },
  };
}

export default async function NoticiaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  let article = await fetchArticleBySlug(slug);
  if (!article) article = MOCK_ARTICLES.find((a) => a.slug === slug) || null;
  if (!article) notFound();

  const cat = getCategory(article.category);
  const reporter = getReporter(article.reporter_slug);
  const img = (article as unknown as { image_url?: string }).image_url || PATTERN_IMAGES[article.category] || PATTERN_IMAGES.general;

  const related = (await fetchNews({ category: article.category, limit: 3 })).filter((a) => a.slug !== slug).slice(0, 3);

  return (
    <article className="container-custom py-8 max-w-4xl">
      <Link href="/" className="inline-flex items-center gap-2 text-sm font-bold text-zinc-600 hover:text-[#e63946]">← Voltar</Link>

      <div className="mt-6">
        <span className="inline-block rounded-full px-3 py-1 text-xs font-bold text-white" style={{ background: cat.color }}>{cat.icon} {cat.label}</span>
        <h1 className="mt-4 text-3xl md:text-4xl font-black leading-tight tracking-tight text-zinc-900">{article.title}</h1>
        {article.summary && <p className="mt-4 text-lg leading-relaxed text-zinc-600">{article.summary}</p>}

        <div className="mt-6 flex flex-wrap items-center gap-4 text-sm text-zinc-500 border-y border-zinc-100 py-4">
          <span className="font-semibold text-zinc-700">✍️ {reporter.name}</span>
          <span>•</span>
          <span>{article.published_at ? new Date(article.published_at).toLocaleDateString("pt-BR", { day: "2-digit", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" }) : ""}</span>
          {article.sources?.[0] && (
            <>
              <span>•</span>
              <a href={article.sources[0]} target="_blank" rel="noopener noreferrer" className="text-[#e63946] font-bold hover:underline">Fonte original</a>
            </>
          )}
        </div>
      </div>

      <div className="mt-8 overflow-hidden rounded-2xl bg-zinc-100">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src={img} alt={article.title} className="w-full h-[420px] object-cover" />
      </div>

      <div className="mt-8 prose prose-zinc max-w-none prose-p:leading-relaxed prose-a:text-[#e63946]">
        {article.content ? (
          <div dangerouslySetInnerHTML={{ __html: article.content }} />
        ) : (
          <>
            <p>{article.summary}</p>
            <p>
              Esta matéria foi apurada com base em fonte pública e reescrita pela nossa equipe de repórteres digitais. Citamos a fonte original
              e mantemos compromisso com correção e transparência.
            </p>
            <p>Conteúdo completo disponível na fonte original. Voltaremos com atualizações assim que houver novos desdobramentos.</p>
          </>
        )}
      </div>

      {article.tags && article.tags.length > 0 && (
        <div className="mt-8 flex flex-wrap gap-2">
          {article.tags.map((t) => (
            <span key={t} className="rounded-full bg-zinc-100 px-3 py-1 text-xs font-semibold text-zinc-600">#{t}</span>
          ))}
        </div>
      )}

      {related.length > 0 && (
        <div className="mt-12">
          <h3 className="font-extrabold text-zinc-900">Relacionadas</h3>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            {related.map((r) => (
              <Link key={r.slug || r.title} href={r.slug ? `/noticia/${r.slug}` : "#"} className="rounded-xl bg-white p-4 shadow-sm border border-zinc-100 hover:shadow-md">
                <span className="text-xs font-bold text-[#e63946]">{getCategory(r.category).label}</span>
                <p className="mt-2 line-clamp-2 text-sm font-bold leading-snug text-zinc-900">{r.title}</p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}
