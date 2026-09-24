import type { MetadataRoute } from 'next';
import { getAllRealArticles } from '@/lib/api';
import { CATEGORY_LIST } from '@/lib/categories';
import { getPublicSiteUrl } from '@/lib/siteUrl';

export const revalidate = 3600;

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = getPublicSiteUrl();
  const staticPages: MetadataRoute.Sitemap = [
    { url: `${base}/`, changeFrequency: 'hourly', priority: 1 },
    { url: `${base}/sobre`, changeFrequency: 'monthly', priority: 0.6 },
    { url: `${base}/privacidade`, changeFrequency: 'yearly', priority: 0.3 },
    { url: `${base}/termos`, changeFrequency: 'yearly', priority: 0.3 },
    { url: `${base}/contato`, changeFrequency: 'yearly', priority: 0.5 },
  ];
  const categories: MetadataRoute.Sitemap = CATEGORY_LIST.map(({ slug }) => ({
    url: `${base}/categoria/${slug}`,
    changeFrequency: 'hourly',
    priority: 0.7,
  }));

  let articles: Awaited<ReturnType<typeof getAllRealArticles>> = [];
  try {
    articles = await getAllRealArticles();
  } catch {
    return [...staticPages, ...categories];
  }
  const news = articles
    .filter((a) => a.slug)
    .map((a) => ({
      url: `${base}/noticia/${a.slug}`,
      lastModified:
        a.updated_at || a.published_at ? new Date(a.updated_at || a.published_at!) : undefined,
      changeFrequency: 'daily' as const,
      priority: 0.8,
    }));
  return [...staticPages, ...categories, ...news];
}
