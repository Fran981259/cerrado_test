import type { Article } from '@/lib/api';

type ArticleJsonLdOptions = {
  article: Article;
  canonicalUrl: string;
  categoryLabel: string;
  imageUrl: string;
  reporterName: string;
  reporterUrl?: string;
};

/** Builds structured data that describes one publicly accessible news article. */
export function buildArticleJsonLd({
  article,
  canonicalUrl,
  categoryLabel,
  imageUrl,
  reporterName,
  reporterUrl,
}: ArticleJsonLdOptions) {
  const updatedAt = article.updated_at || article.published_at || article.created_at || undefined;
  return {
    '@context': 'https://schema.org',
    '@type': 'NewsArticle',
    headline: article.title,
    description: article.summary || article.title,
    datePublished: article.published_at || article.created_at || undefined,
    dateModified: updatedAt,
    author: { '@type': 'Person', name: reporterName, url: reporterUrl },
    publisher: {
      '@type': 'Organization',
      '@id': `${new URL(canonicalUrl).origin}/#organization`,
      name: 'Portal Cerrado',
    },
    mainEntityOfPage: canonicalUrl,
    image: [imageUrl],
    articleSection: categoryLabel,
    inLanguage: 'pt-BR',
    isAccessibleForFree: true,
    keywords: [...new Set([categoryLabel, ...(article.tags || [])])],
    url: canonicalUrl,
  };
}
