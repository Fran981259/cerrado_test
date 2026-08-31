import Link from "next/link";
import { fetchNews } from "@/lib/api";
import { NewsCard } from "@/components/NewsCard";
import { getCategory } from "@/lib/categories";

export const revalidate = 60;

export function generateStaticParams() {
  return [
    { slug: "politics" }, { slug: "economy" }, { slug: "security" },
    { slug: "agriculture" }, { slug: "sports" }, { slug: "health" },
    { slug: "general" }, { slug: "tech" },
  ];
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const cat = getCategory(slug);
  return {
    title: `${cat.label} | Atualiza Brasil`,
    description: `Notícias de ${cat.label} em Mato Grosso do Sul`,
  };
}

export default async function CategoriaPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const cat = getCategory(slug);
  // se slug desconhecido, mostra general mas não 404
  const articles = await fetchNews({ category: slug, limit: 24 });

  return (
    <div className="container-custom py-8">
      <div className="flex items-center gap-3 mb-6">
        <span className="text-2xl">{cat.icon}</span>
        <h1 className="text-2xl font-black text-zinc-900">{cat.label}</h1>
        <span className="text-sm text-zinc-500">— {articles.length} matérias</span>
      </div>
      {articles.length === 0 ? (
        <div className="py-16 text-center text-zinc-500">
          Nenhuma matéria em {cat.label} ainda.
          <Link href="/" className="block mt-4 text-[#e63946] font-bold">← Voltar</Link>
        </div>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {articles.map((a) => (
            <NewsCard key={a.slug || a.title} article={a} />
          ))}
        </div>
      )}
    </div>
  );
}
