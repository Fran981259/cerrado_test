export const REPORTERS: Record<string, { name: string; specialty: string }> = {
  "enzo.bianchi": { name: "Enzo Bianchi", specialty: "Tecnologia" },
  "marcus.teixeira": { name: "Marcus Teixeira", specialty: "Esportes" },
  "luciana.freitas": { name: "Luciana Freitas", specialty: "Política" },
  "bia.fernandes": { name: "Bia Fernandes", specialty: "Agronegócio" },
  "rafael.dumas": { name: "Rafael Dumas", specialty: "Segurança" },
  "maya.santos": { name: "Maya Santos", specialty: "Saúde" },
  "camila.rocha": { name: "Camila Rocha", specialty: "Economia" },
  "lucas.nakamura": { name: "Lucas Nakamura", specialty: "Educação" },
  "leon.vaz": { name: "Leon Vaz", specialty: "Cultura" },
  "carlos.nunes": { name: "Carlos Nunes", specialty: "Economia" },
  "fernanda.lima": { name: "Fernanda Lima", specialty: "Ciência" },
  "pedro.mendes": { name: "Pedro Mendes", specialty: "Entretenimento" },
};

export function getReporter(slug?: string) {
  if (!slug) return { name: "Redação", specialty: "Geral" };
  return REPORTERS[slug] ?? { name: slug, specialty: "Geral" };
}
