export const CATEGORIES = {
  tech: { label: "Tecnologia", iconClass: "fi-rr-laptop", color: "#e63946" },
  sports: { label: "Esportes", iconClass: "fi-rr-football", color: "#2a9d8f" },
  politics: { label: "Política", iconClass: "fi-rr-landmark", color: "#264653" },
  economy: { label: "Economia", iconClass: "fi-rr-chart-histogram", color: "#e9c46a", textDark: true },
  health: { label: "Saúde", iconClass: "fi-rr-hospital", color: "#e76f51" },
  security: { label: "Segurança", iconClass: "fi-rr-shield-check", color: "#9d0208" },
  science: { label: "Ciência", iconClass: "fi-rr-microscope", color: "#457b9d" },
  entertainment: { label: "Entretenimento", iconClass: "fi-rr-clapperboard-play", color: "#8338ec" },
  agriculture: { label: "Agronegócio", iconClass: "fi-rr-wheat", color: "#606c38" },
  education: { label: "Educação", iconClass: "fi-rr-graduation-cap", color: "#0081a7" },
  culture: { label: "Cultura", iconClass: "fi-rr-palette", color: "#7209b7" },
  clima: { label: "Clima", iconClass: "fi-rr-cloud-sun", color: "#0284c7" },
  general: { label: "Geral", iconClass: "fi-rr-newspaper", color: "#6c757d" },
} as const;

// Aliases: o banco usa o nome da role do repórter; o frontend usa chaves curtas
const CATEGORY_ALIASES: Record<string, CategorySlug> = {
  technology: "tech",
  security: "security",
  politics: "politics",
  economy: "economy",
  health: "health",
  agriculture: "agriculture",
  education: "education",
  culture: "culture",
  entertainment: "entertainment",
  sports: "sports",
  science: "science",
  clima: "clima",
  general: "general",
};

export type CategorySlug = keyof typeof CATEGORIES;

export function getCategory(slug?: string) {
  if (!slug) return CATEGORIES.general;
  const key = CATEGORY_ALIASES[slug] ?? (CATEGORIES as Record<string, unknown>)[slug];
  if (typeof key === "string") return CATEGORIES[key as CategorySlug] ?? CATEGORIES.general;
  return (key as (typeof CATEGORIES)[CategorySlug]) ?? CATEGORIES.general;
}

export const CATEGORY_LIST = Object.entries(CATEGORIES).map(([slug, v]) => ({ slug, ...v }));

export function categorySlug(value: unknown): string | null {
  if (typeof value !== "string") return null;
  const aliases: Record<string, string> = {
    technology: "tech",
    entertainment: "culture",
    ciencia: "science",
  };
  const slug = Object.hasOwn(aliases, value) ? aliases[value] : value;
  return Object.hasOwn(CATEGORIES, slug) ? slug : null;
}

export const PATTERN_IMAGES: Record<string, string> = {
  technology: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop",
  tech: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&h=400&fit=crop",
  sports: "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&h=400&fit=crop",
  politics: "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=600&h=400&fit=crop",
  economy: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&h=400&fit=crop",
  health: "https://images.unsplash.com/photo-1559757175-5700dde675bc?w=600&h=400&fit=crop",
  security: "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&h=400&fit=crop",
  science: "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=600&h=400&fit=crop",
  entertainment: "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=600&h=400&fit=crop",
  agriculture: "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?w=600&h=400&fit=crop",
  education: "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=600&h=400&fit=crop",
  culture: "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=600&h=400&fit=crop",
  clima: "https://images.unsplash.com/photo-1504608524841-42fe6f032b4b?w=600&h=400&fit=crop",
  general: "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&h=400&fit=crop",
};
