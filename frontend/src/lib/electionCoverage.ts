import type { Article } from "@/lib/api";

const ELECTION_TERMS = [
  "eleiç",
  "eleitoral",
  "presidencial",
  "tse",
  "tre",
  "urna",
  "debate",
  "pesquisa",
  "candidato",
  "candidata",
  "campanha",
  "lula",
  "bolsonaro",
];

const POLITICS_TERMS = [
  ...ELECTION_TERMS,
  "congresso",
  "senado",
  "câmara",
  "governo",
  "deputado",
  "senador",
  "presidente",
  "ministério",
];

const NON_POLITICS_TERMS = [
  "campeonato",
  "futebol",
  "partida",
  "sub-",
  "hospital",
  "paciente",
  "vacina",
  "homicídio",
  "polícia",
  "safra",
  "onça",
];

const MAX_ELECTION_AGE_MS = 7 * 24 * 60 * 60 * 1000;

function normalizedText(article: Article): string {
  return `${article.title} ${article.summary ?? ""}`.toLocaleLowerCase("pt-BR");
}

function hasTerm(article: Article, terms: string[]): boolean {
  const text = normalizedText(article);
  return terms.some((term) => text.includes(term));
}

function articleDate(article: Article): number {
  const timestamp = Date.parse(article.published_at ?? article.created_at ?? "");
  return Number.isNaN(timestamp) ? 0 : timestamp;
}

function uniqueArticles(articles: Article[]): Article[] {
  const seen = new Set<string>();
  return articles.filter((article) => {
    const key = article.slug ?? article.title;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

/** Identifies election coverage independently from a fallible generic category. */
export function isElectionArticle(article: Article): boolean {
  return hasTerm(article, ELECTION_TERMS);
}

/** Identifies political coverage without relying only on the stored editoria. */
export function isPoliticalArticle(article: Article): boolean {
  return !hasTerm(article, NON_POLITICS_TERMS) && (article.category === "politics" || hasTerm(article, POLITICS_TERMS));
}

/** Pins recent election coverage ahead of the generic home ranking. */
export function prioritizeElectionCoverage(articles: Article[], maxPinned = 2): Article[] {
  const unique = uniqueArticles(articles);
  const minimumDate = Date.now() - MAX_ELECTION_AGE_MS;
  const electionArticles = unique
    .filter((article) => isElectionArticle(article) && articleDate(article) >= minimumDate)
    .sort((left, right) => articleDate(right) - articleDate(left) || (right.final_score ?? 0) - (left.final_score ?? 0))
    .slice(0, maxPinned);
  const pinnedKeys = new Set(electionArticles.map((article) => article.slug ?? article.title));
  return [...electionArticles, ...unique.filter((article) => !pinnedKeys.has(article.slug ?? article.title))];
}

/** Builds the politics rail while avoiding stories that are already in the hero. */
export function selectPoliticalCoverage(articles: Article[], excluded: Article[], limit: number): Article[] {
  const excludedKeys = new Set(excluded.map((article) => article.slug ?? article.title));
  return uniqueArticles(articles)
    .filter((article) => !excludedKeys.has(article.slug ?? article.title) && isPoliticalArticle(article))
    .sort((left, right) => Number(isElectionArticle(right)) - Number(isElectionArticle(left)) || articleDate(right) - articleDate(left))
    .slice(0, limit);
}
