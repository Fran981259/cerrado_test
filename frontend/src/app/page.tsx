import type { Metadata } from "next";
import { Suspense } from "react";
import { fetchNewsResponse, rankHomepageArticles, selectDynamicLocalNews, type Article } from "@/lib/api";
import { HeroGrid } from "@/components/home/HeroGrid";
import { AgroModule } from "@/components/home/AgroModule";
import { PoderModule } from "@/components/home/PoderModule";
import { Columnists } from "@/components/home/Columnists";
import { getPublicSiteUrl } from "@/lib/siteUrl";

const BASE = getPublicSiteUrl();

export const revalidate = 60;

export async function generateMetadata(): Promise<Metadata> {
  return {
    title: "Portal Cerrado — Notícias de Mato Grosso do Sul",
    description: "Agro, mercados e negócios regionais. Política, economia, segurança e agronegócio em Mato Grosso do Sul, com apuração 24 horas.",
    alternates: { canonical: BASE },
    openGraph: {
      title: "Portal Cerrado — Notícias de MS",
      description: "Agro, mercados e negócios regionais de Mato Grosso do Sul.",
      url: BASE,
      type: "website",
      locale: "pt_BR",
      siteName: "Portal Cerrado",
    },
  };
}

function pickHero(recent: Article[]): { main?: Article; side: Article[]; rail: Article[]; latest: Article[] } {
  const unique = recent.filter((article, index, all) => {
    const key = article.slug || article.title;
    return all.findIndex((item) => (item.slug || item.title) === key) === index;
  });
  return {
    main: unique[0],
    side: unique.slice(1, 3),
    rail: unique.slice(3, 6),
    latest: unique.slice(6, 10),
  };
}

const ORGANIZATION_JSON_LD = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "WebSite",
      "@id": `${BASE}/#website`,
      url: BASE,
      name: "Portal Cerrado",
      inLanguage: "pt-BR",
      description: "Notícias de Agro, Mercados e Negócios regionais de Mato Grosso do Sul.",
      potentialAction: {
        "@type": "SearchAction",
        target: { "@type": "EntryPoint", urlTemplate: `${BASE}/busca?q={search_term_string}` },
        "query-input": "required name=search_term_string",
      },
    },
    {
      "@type": "Organization",
      "@id": `${BASE}/#organization`,
      name: "Portal Cerrado",
      url: BASE,
      foundingLocation: "Campo Grande, Mato Grosso do Sul, Brasil",
      areaServed: "Mato Grosso do Sul, Brasil",
    },
  ],
};

export default async function Home() {
  const settled = await Promise.allSettled([
    fetchNewsResponse({ region: "ms", limit: 80, sortBy: "recent" }),
    fetchNewsResponse({ region: "ms", category: "agriculture", limit: 5, sortBy: "recent" }),
  ]);

  const [recentResult, agroResult] = settled;
  const recent = recentResult.status === "fulfilled" ? recentResult.value.news : [];
  const agro = agroResult.status === "fulfilled" ? agroResult.value.news : [];

  const { main, side, rail, latest } = pickHero(rankHomepageArticles(recent));
  const heroArticles = [main, ...side, ...rail, ...latest].filter((article): article is Article => Boolean(article));
  const rankedAgro = rankHomepageArticles(agro);
  const dynamicLocalNews = selectDynamicLocalNews(recent, [...heroArticles, ...rankedAgro], 6);
  const hardError = settled.every((result) => result.status === "rejected");

  return (
    <div className="bg-canvas">
      {hardError && (
        <div className="container-editorial pt-6" role="alert">
          <p className="rounded border border-red-700/25 bg-red-50 px-5 py-4 text-sm font-semibold text-red-800">
            A API de notícias não respondeu neste momento. As cotações de mercado seguem carregando de fontes independentes.
          </p>
        </div>
      )}

      <HeroGrid main={main} side={side} rail={rail} latest={latest} />

      <AgroModule articles={rankedAgro} />

      <PoderModule articles={dynamicLocalNews} />

      <Suspense
        fallback={
          <section aria-label="Carregando colunistas" className="container-editorial py-10">
            <div className="h-2 w-28 rounded bg-black/10" />
            <div className="mt-2 h-7 w-72 rounded bg-black/10" />
            <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
                <div key={i} className="rounded-md">
                  <div className="aspect-[16/10] rounded-md bg-black/10" />
                  <div className="mt-4 h-3 w-1/4 rounded bg-black/10" />
                  <div className="mt-3 h-5 w-11/12 rounded bg-black/10" />
                  <div className="mt-2 h-5 w-3/4 rounded bg-black/10" />
                </div>
              ))}
            </div>
          </section>
        }
      >
        <Columnists />
      </Suspense>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(ORGANIZATION_JSON_LD) }}
      />
    </div>
  );
}
