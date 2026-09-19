import type { Metadata } from "next";
import { Suspense } from "react";
import { fetchNewsResponse, type Article } from "@/lib/api";
import { HeroGrid } from "@/components/home/HeroGrid";
import { AgroModule } from "@/components/home/AgroModule";
import { PoderModule } from "@/components/home/PoderModule";
import { Columnists } from "@/components/home/Columnists";

const BASE = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";

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

function pickHero(recent: Article[]): { main?: Article; feature?: Article; rail: Article[] } {
  const picked: string[] = [];
  const used = (article: Article): boolean => {
    const key = article.slug || article.title;
    if (picked.includes(key)) return true;
    picked.push(key);
    return false;
  };
  const main = recent.find((a) => !used(a));
  const feature = recent.find((a) => !used(a));
  const rail = recent.filter((a) => !used(a)).slice(0, 2);
  return { main, feature, rail };
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
    fetchNewsResponse({ limit: 40, sortBy: "recent" }),
    fetchNewsResponse({ category: "agriculture", limit: 5, sortBy: "recent" }),
    fetchNewsResponse({ category: "politics", limit: 3, sortBy: "recent" }),
    fetchNewsResponse({ category: "economy", limit: 3, sortBy: "recent" }),
    fetchNewsResponse({ category: "security", limit: 2, sortBy: "recent" }),
  ]);

  const [recentResult, agroResult, politicsResult, economyResult, securityResult] = settled;
  const recent = recentResult.status === "fulfilled" ? recentResult.value.news : [];
  const agro = agroResult.status === "fulfilled" ? agroResult.value.news : [];
  const politics = politicsResult.status === "fulfilled" ? politicsResult.value.news : [];
  const economy = economyResult.status === "fulfilled" ? economyResult.value.news : [];
  const security = securityResult.status === "fulfilled" ? securityResult.value.news : [];

  const { main, feature, rail } = pickHero(recent);
  const hardError = settled.every((r) => r.status === "rejected");

  return (
    <div className="bg-canvas">
      {hardError && (
        <div className="container-editorial pt-6" role="alert">
          <p className="rounded border border-red-700/25 bg-red-50 px-5 py-4 text-sm font-semibold text-red-800">
            A API de notícias não respondeu neste momento. As cotações de mercado seguem carregando de fontes independentes.
          </p>
        </div>
      )}

      <HeroGrid main={main} feature={feature} rail={rail} />

      <AgroModule articles={agro} />

      <PoderModule politics={politics} economy={economy} security={security} rural={agro.slice(1, 3)} />

      <Suspense
        fallback={
          <section aria-label="Carregando colunistas" className="container-editorial py-10">
            <div className="h-2 w-28 rounded bg-black/10" />
            <div className="mt-2 h-7 w-72 rounded bg-black/10" />
            <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
                <div key={i} className="h-56 rounded-md border border-black/10 bg-surface p-5">
                  <div className="h-11 w-11 rounded-full bg-black/10" />
                  <div className="mt-4 h-3 w-3/4 rounded bg-black/10" />
                  <div className="mt-2 h-3 w-1/2 rounded bg-black/10" />
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