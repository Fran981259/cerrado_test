export const CATEGORIES = {
  tech: { label: "Tecnologia", icon: "💻", color: "#e63946" },
  sports: { label: "Esportes", icon: "⚽", color: "#2a9d8f" },
  politics: { label: "Política", icon: "🏛️", color: "#264653" },
  economy: { label: "Economia", icon: "📈", color: "#e9c46a", textDark: true },
  health: { label: "Saúde", icon: "🏥", color: "#e76f51" },
  security: { label: "Segurança", icon: "🚨", color: "#9d0208" },
  science: { label: "Ciência", icon: "🔬", color: "#457b9d" },
  entertainment: { label: "Entretenimento", icon: "🎬", color: "#8338ec" },
  agriculture: { label: "Agronegócio", icon: "🌾", color: "#606c38" },
  education: { label: "Educação", icon: "🎓", color: "#0081a7" },
  culture: { label: "Cultura", icon: "🎭", color: "#7209b7" },
  general: { label: "Geral", icon: "📰", color: "#6c757d" },
} as const;

export type CategorySlug = keyof typeof CATEGORIES;

export function getCategory(slug?: string) {
  if (!slug) return CATEGORIES.general;
  return (CATEGORIES as Record<string, (typeof CATEGORIES)[CategorySlug]>)[slug] ?? CATEGORIES.general;
}

export const CATEGORY_LIST = Object.entries(CATEGORIES).map(([slug, v]) => ({ slug, ...v }));

export const PATTERN_IMAGES: Record<string, string> = {
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
  general: "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&h=400&fit=crop",
};
