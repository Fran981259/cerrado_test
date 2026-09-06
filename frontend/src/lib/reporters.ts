export type ReporterBio = {
  name: string;
  specialty: string;
  role: string;
  beat: string;
  university: string;
  state: string;
  bio: string;
};

export const REPORTERS: Record<string, ReporterBio> = {
  "enzo.bianchi": {
    name: "Enzo Bianchi",
    specialty: "Tecnologia",
    role: "Jornalista de tecnologia",
    beat: "Tecnologia e inovação",
    university: "Universidade Federal de Minas Gerais (UFMG)",
    state: "Minas Gerais",
    bio: "Jornalista de tecnologia formado pela Universidade Federal de Minas Gerais (UFMG). Cobre inovação, startups e o impacto da tecnologia no cotidiano, com foco em como as novidades chegam a Mato Grosso do Sul.",
  },
  "marcus.teixeira": {
    name: "Marcus Teixeira",
    specialty: "Esportes",
    role: "Jornalista esportivo",
    beat: "Esportes e lazer",
    university: "Universidade Federal do Rio de Janeiro (UFRJ)",
    state: "Rio de Janeiro",
    bio: "Jornalista esportivo formado pela Universidade Federal do Rio de Janeiro (UFRJ). Narra o esporte sul-mato-grossense com empolgação e contexto, do futebol amador às grandes competições.",
  },
  "rafael.dumas": {
    name: "Rafael Dumas",
    specialty: "Segurança",
    role: "Jornalista policial",
    beat: "Polícia e segurança pública",
    university: "Universidade Federal da Bahia (UFBA)",
    state: "Bahia",
    bio: "Jornalista policial formado pela Universidade Federal da Bahia (UFBA). Apura segurança pública com rigor e objetividade, sempre a partir de fontes oficiais e dados verificados.",
  },
  "luciana.freitas": {
    name: "Luciana Freitas",
    specialty: "Política",
    role: "Jornalista política",
    beat: "Política e governo",
    university: "Universidade de Brasília (UnB)",
    state: "Distrito Federal",
    bio: "Jornalista política formada pela Universidade de Brasília (UnB). Acompanha os bastidores do poder em Campo Grande e no país com precisão, neutralidade e contexto para o leitor.",
  },
  "maya.santos": {
    name: "Maya Santos",
    specialty: "Saúde",
    role: "Jornalista de saúde e ciência",
    beat: "Saúde e ciência",
    university: "Universidade Federal de São Paulo (UNIFESP)",
    state: "São Paulo",
    bio: "Jornalista de saúde e ciência formada pela Universidade Federal de São Paulo (UNIFESP). Traduz estudos e orientações médicas para linguagem clara, sem sensacionalismo e com cautela científica.",
  },
  "lucas.nakamura": {
    name: "Lucas Nakamura",
    specialty: "Educação",
    role: "Jornalista de educação",
    beat: "Educação e concursos",
    university: "Universidade Federal do Rio Grande do Sul (UFRGS)",
    state: "Rio Grande do Sul",
    bio: "Jornalista de educação formado pela Universidade Federal do Rio Grande do Sul (UFRGS). Explica ensino, ENEM e concursos de forma didática, com foco em oportunidades para o leitor.",
  },
  "bia.fernandes": {
    name: "Bia Fernandes",
    specialty: "Agronegócio",
    role: "Jornalista de agronegócio",
    beat: "Agronegócio e mercado",
    university: "Universidade Federal de Goiás (UFG)",
    state: "Goiás",
    bio: "Jornalista de agronegócio formada pela Universidade Federal de Goiás (UFG). Cobre o campo com olhar profissional e territorial, ligando safra, mercado e a economia de Mato Grosso do Sul.",
  },
  "leon.vaz": {
    name: "Leon Vaz",
    specialty: "Cultura",
    role: "Jornalista cultural",
    beat: "Cultura e eventos",
    university: "Universidade Federal de Mato Grosso do Sul (UFMS)",
    state: "Mato Grosso do Sul",
    bio: "Jornalista cultural formado pela Universidade Federal de Mato Grosso do Sul (UFMS). Conta a cena cultural do Estado com sensibilidade, do Pantanal aos palcos de Campo Grande.",
  },
  "camila.rocha": {
    name: "Camila Rocha",
    specialty: "Economia",
    role: "Jornalista de economia",
    beat: "Economia e empregos",
    university: "Universidade Federal de Pernambuco (UFPE)",
    state: "Pernambuco",
    bio: "Jornalista de economia formada pela Universidade Federal de Pernambuco (UFPE). Analisa preços, empregos e mercado com pragmatismo, mostrando o que os números significam no bolso do leitor.",
  },
  "carlos.nunes": { name: "Carlos Nunes", specialty: "Economia", role: "Jornalista", beat: "Economia", university: "Universidade Federal de Pernambuco (UFPE)", state: "Pernambuco", bio: "Repórter da equipe econômica do Portal Cerrado." },
  "fernanda.lima": { name: "Fernanda Lima", specialty: "Ciência", role: "Jornalista", beat: "Ciência", university: "Universidade Federal de São Paulo (UNIFESP)", state: "São Paulo", bio: "Repórter da equipe de ciência do Portal Cerrado." },
  "pedro.mendes": { name: "Pedro Mendes", specialty: "Entretenimento", role: "Jornalista", beat: "Entretenimento", university: "Universidade Federal de Mato Grosso do Sul (UFMS)", state: "Mato Grosso do Sul", bio: "Repórter da equipe de entretenimento do Portal Cerrado." },
};

export const REPORTER_LIST = Object.entries(REPORTERS).map(([slug, v]) => ({ slug, ...v }));

export function getReporter(slug?: string) {
  if (!slug) return { name: "Redação", specialty: "Geral", role: "Redação", beat: "Geral", university: "", state: "", bio: "" };
  return REPORTERS[slug] ?? { name: slug, specialty: "Geral", role: "Jornalista", beat: "Geral", university: "", state: "", bio: "" };
}

export function reporterInitials(name: string) {
  return name.split(" ").map((p) => p[0]).slice(0, 2).join("").toUpperCase();
}
