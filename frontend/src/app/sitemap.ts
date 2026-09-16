import type { MetadataRoute } from "next";
import { getAllRealArticles } from "@/lib/api";

export const revalidate = 3600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = process.env.NEXT_PUBLIC_SITE_URL || "http://100.95.111.24:3000";
  const staticPages: MetadataRoute.Sitemap = [
    { url: `${base}/`, lastModified: new Date(), changeFrequency: "hourly", priority: 1 },
    { url: `${base}/sobre`, lastModified: new Date(), changeFrequency: "monthly", priority: 0.6 },
    { url: `${base}/privacidade`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${base}/termos`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.3 },
    { url: `${base}/contato`, lastModified: new Date(), changeFrequency: "yearly", priority: 0.5 },
  ];

  let articles: Awaited<ReturnType<typeof getAllRealArticles>> = [];
  try {
    articles = await getAllRealArticles();
  } catch {
    return staticPages;
  }
  const news = articles
    .filter((a) => a.slug)
    .map((a) => ({
      url: `${base}/noticia/${a.slug}`,
      lastModified: a.updated_at || a.published_at ? new Date(a.updated_at || a.published_at!) : undefined,
      changeFrequency: "daily" as const,
      priority: 0.8,
    }));
  return [...staticPages, ...news];
}
