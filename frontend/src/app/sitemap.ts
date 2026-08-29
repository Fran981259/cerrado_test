import type { MetadataRoute } from "next";
import { fetchNews } from "@/lib/api";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "https://atualizabrasil.news";
  const staticPages: MetadataRoute.Sitemap = [
    { url: `${base}/`, lastModified: new Date(), changeFrequency: "hourly", priority: 1 },
    { url: `${base}/sobre`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/privacidade`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${base}/termos`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${base}/contato`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.5 },
  ];

  try {
    const articles = await fetchNews({ limit: 100 });
    const news = articles
      .filter((a) => a.slug)
      .map((a) => ({
        url: `${base}/noticia/${a.slug}`,
        lastModified: a.published_at ? new Date(a.published_at) : new Date(),
        changeFrequency: "daily" as const,
        priority: 0.8,
      }));
    return [...staticPages, ...news];
  } catch {
    return staticPages;
  }
}
