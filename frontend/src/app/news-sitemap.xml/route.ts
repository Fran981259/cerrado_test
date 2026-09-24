import { getRecentNewsSitemapArticles, type NewsSitemapArticle } from '@/lib/api';
import { getPublicSiteUrl } from '@/lib/siteUrl';

const NEWS_SITEMAP_HEADERS = {
  'Cache-Control': 'public, max-age=300, stale-while-revalidate=600',
  'Content-Type': 'application/xml; charset=utf-8',
};

function escapeXml(value: string): string {
  return value.replace(/[<>&'\"]/g, (character) => {
    const entities: Record<string, string> = {
      '"': '&quot;',
      '&': '&amp;',
      "'": '&apos;',
      '<': '&lt;',
      '>': '&gt;',
    };
    return entities[character];
  });
}

function newsUrlXml(article: NewsSitemapArticle): string {
  const url = `${getPublicSiteUrl()}/noticia/${article.slug}`;
  const lastModified = article.updated_at ? `<lastmod>${article.updated_at}</lastmod>` : '';
  return `<url><loc>${escapeXml(url)}</loc><news:news><news:publication><news:name>Portal Cerrado</news:name><news:language>pt</news:language></news:publication><news:publication_date>${escapeXml(article.published_at)}</news:publication_date><news:title>${escapeXml(article.title)}</news:title></news:news>${lastModified}</url>`;
}

/** Serves recent editorial URLs in the Google News sitemap format. */
export async function GET(): Promise<Response> {
  try {
    const articles = await getRecentNewsSitemapArticles();
    const urls = articles.map(newsUrlXml).join('');
    const xml = `<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">${urls}</urlset>`;
    return new Response(xml, { headers: NEWS_SITEMAP_HEADERS });
  } catch {
    return new Response('Sitemap de notícias temporariamente indisponível.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain; charset=utf-8' },
    });
  }
}
