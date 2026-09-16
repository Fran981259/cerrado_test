"""
Classificador de Notícias — Portal Cerrado
============================================
Avalia cada notícia minerada/coletada por:
- Grau de importância (impacto)
- Potencial de engajamento
- Score final combinado
"""

import re
import logging
from datetime import datetime, timezone
from typing import Dict, List, Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportanceLevel(Enum):
    """Níveis de importância da notícia."""
    CRITICAL = 5  # Acontecimentos globais majeures
    HIGH = 4      # Impacto regional/nacional forte
    MEDIUM = 3    # Relevante mas não excepcional
    LOW = 2       # Interesse local/curiosidade
    MINIMAL = 1   # Preenchimento, sem grande impacto


class EngagementLevel(Enum):
    """Níveis de potencial de engajamento."""
    VIRAL = 5  # Potencial para viralizar (celebridades, escândalos)
    HIGH = 4   # Alto engajamento (polêmicas, novidades)
    MEDIUM = 3 # Engajamento moderado
    LOW = 2    # Baixo engajamento
    MINIMAL = 1 # Pouco interesse


class NewsClassifier:
    """Classificador de notícias por importância e engajamento."""
    
    # Pesos para cálculo do score final
    WEIGHT_IMPORTANCE = 0.6   # 60% importância
    WEIGHT_ENGAGEMENT = 0.4  # 40% engajamento
    
    def __init__(self):
        self._load_patterns()
    
    def _load_patterns(self):
        """Carrega padrões para classificação."""
        
        # ========== IMPORTÂNCIA ==========
        self.high_importance_keywords = {
            "war": 5, "guerra": 5, "conflict": 5, "conflito": 5,
            "invasion": 5, "invasão": 5, "sanctions": 5, "sanções": 5,
            "NATO": 4, "nuclear": 5, "terrorism": 5, "terrorismo": 5,
            "diplomatic crisis": 5, "crise diplomática": 5,
            "president": 3, "presidente": 3, "election": 4, "eleição": 4,
            "government": 3, "governo": 3, "congress": 3, "congresso": 3,
            "supreme court": 4, "suprema corte": 4,
            "BRICS": 3, "G7": 3, "G20": 3,
            
            "Federal Reserve": 4, "interest rate": 4, "taxa de juros": 4,
            "recession": 5, "recessão": 5, "inflation": 4, "inflação": 4,
            "stock market crash": 5, "crash": 5, "queda da bolsa": 5,
            "IPO": 3, "merger": 3, "fusão": 3, "acquisition": 3, "aquisição": 3,
            "GDP": 3, "PIB": 3, "unemployment": 4, "desemprego": 4,
            
            "OpenAI": 4, "ChatGPT": 4, "GPT": 4,
            "Google": 3, "Apple": 3, "Microsoft": 3, "Amazon": 3,
            "Meta": 3, "Tesla": 3, "Nvidia": 3,
            "breakthrough": 4, "descoberta": 4, "first ever": 4, "primeira vez": 4,
            "AI regulation": 4, "regulamentação IA": 4,
            "data breach": 4, "vazamento de dados": 4,
            
            "pandemic": 5, "pandemia": 5, "outbreak": 5, "surto": 5,
            "epidemic": 5, "epidemia": 5, "WHO": 3, "OMS": 3,
            "FDA approval": 4, "cancer cure": 5, "cura do câncer": 5,
            "vaccine": 4, "vacina": 4, "clinical trial": 3, "ensaio clínico": 3,
            
            "climate emergency": 5, "emergência climática": 5,
            "natural disaster": 5, "desastre natural": 5,
            "earthquake": 5, "terremoto": 5, "tsunami": 5,
            "hurricane": 4, "furacão": 4,
            "Amazon deforestation": 4, "desmatamento": 4,
        }
        
        self.low_importance_keywords = {
            "celebrity": 1, "celebridade": 1,
            "gossip": 1, "fofoca": 1,
            "lifestyle": 1, "estilo de vida": 1,
            "recipe": 1, "receita": 1,
            "horoscope": 1, "horóscopo": 1,
            "viral video": 1, "vídeo viral": 1,
            "meme": 1,
        }
        
        # ========== ENGAJAMENTO ==========
        self.high_engagement_keywords = {
            "scandal": 5, "escândalo": 5, "controversy": 4, "polêmica": 4,
            "exposed": 4, "exposto": 4, "leaked": 4, "vazou": 4,
            "arrested": 4, "preso": 4, "caught": 3, "pego": 3,
            "shocking": 4, "chocante": 4, "unbelievable": 4, "inacreditável": 4,
            "celebrity": 4, "celebridade": 4, "famous": 3, "famoso": 3,
            "death": 4, "morte": 4, "dies": 4, "morre": 4,
            "born": 3, "nasce": 3, "pregnant": 4, "grávida": 4,
            "millionaire": 4, "milionário": 4, "lottery": 4, "loteria": 4,
            "won": 3, "ganhou": 3, "prize": 3, "prêmio": 3,
            "launch": 3, "lançamento": 3, "new": 2, "novo": 2,
            "first": 3, "primeiro": 3, "exclusive": 4, "exclusivo": 4,
            "leak": 4, "vazamento": 4, "rumor": 3, "especulação": 3,
            "update": 2, "atualização": 2,
            "championship": 4, "campeonato": 4, "final": 3, "decisão": 3,
            "win": 3, "vitória": 3, "lose": 2, "derrota": 2,
            "transfer": 3, "transferência": 3, "signing": 3, "contratação": 3,
            "record": 3, "recorde": 3,
            "your money": 4, "seu dinheiro": 4,
            "your health": 4, "sua saúde": 4,
            "your job": 4, "seu emprego": 4,
            "you need to know": 4, "você precisa saber": 4,
            "alert": 3, "alerta": 3, "warning": 3, "aviso": 3,
        }
        
        self.low_engagement_keywords = {
            "report": 1, "relatório": 1, "study": 1, "estudo": 1,
            "analysis": 1, "análise": 1, "research": 1, "pesquisa": 1,
            "statistics": 1, "estatísticas": 1, "data": 1, "dados": 1,
            "document": 1, "documento": 1, "filing": 1, "processo": 1,
        }
    
    def classify(self, article: Dict) -> Dict:
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        combined = title + ' ' + summary
        
        importance_score = self._calculate_importance(combined, article)
        engagement_score = self._calculate_engagement(combined, article)
        
        final_score = (
            importance_score * self.WEIGHT_IMPORTANCE +
            engagement_score * self.WEIGHT_ENGAGEMENT
        )
        
        importance_level = self._get_importance_level(importance_score)
        engagement_level = self._get_engagement_level(engagement_score)
        priority_tier = self._get_priority_tier(final_score)
        
        article['classification'] = {
            'importance_score': round(importance_score, 2),
            'engagement_score': round(engagement_score, 2),
            'final_score': round(final_score, 2),
            'importance_level': importance_level.name,
            'engagement_level': engagement_level.name,
            'priority_tier': priority_tier,
            'classified_at': datetime.now(timezone.utc).isoformat(),
        }
        return article
    
    def classify_category(self, text: str) -> str:
        """Heurística para classificar categoria. Retorna nome canônico de contracts.CATEGORIES."""
        from app.contracts import category_name
        text = text.lower()
        mapping = {
            "technology": [
                "bitcoin", "tecnologia", "startup", "app", "software", "digital",
                "inteligência artificial", "computador", "sistema", "rede", "cyber",
                "celular", "smartphone", "plataforma", "algoritmo", "dados",
                # EN keywords
                "ai", "artificial intelligence", "tech", "startup", "software",
                "cyber", "data", "digital", "openai", "chatgpt", "tesla",
                "silicon valley", "blockchain", "crypto", "robot",
            ],
            "sports": [
                "futebol", "esporte", "time", "campeonato", "jogador", "gol",
                "copa", "liga", "atleta", "olimpíada", "torneio",
                "nba", "nfl", "fórmula", "corrida",
                "seleção", "caiaque", "kung fu", "maratona", "competição",
                "extremo", "esportivo",
                # EN keywords
                "football", "soccer", "sports", "championship", "tournament",
                "athlete", "player", "league", "nba", "nfl", "premier league",
                "cricket", "rugby", "tennis", "boxing", "ufc", "mma",
            ],
            "politics": [
                "governo", "política", "eleição", "congresso", "presidente",
                "senador", "deputado", "prefeito", "mandato", "câmara",
                "senado", "lei", "projeto", "votação", "campanha",
                "eleitoral", "eleitor", "candidato", "turnstile",
                "justiça", "juiz", "tribunal", "sentença", "júri",
                "orçamento", "público", "municipal", "estadual",
                # EN keywords
                "government", "election", "president", "congress", "senate",
                "parliament", "minister", "political", "vote", "democracy",
                "afv", "afd", "geopolitics", "trade war", "sanctions",
                "military", "war", "conflict", "refugee", "diplomat",
                "rubio", "ukraine", "israel", "gaza", "lebanon", "serbia",
                "taiwan", "china", "canada",
            ],
            "economy": [
                "economia", "pib", "inflação", "juros", "dólar", "mercado",
                "financeiro", "bolsa", "investimento", "empresa", "faturamento",
                "receita", "desemprego", "trabalho", "emprego", "salário",
                "crédito", "produtores", "bnDES", "empréstimo",
                # EN keywords
                "economy", "inflation", "gdp", "interest rate", "stock",
                "market", "financial", "trade", "export", "import",
                "recession", "unemployment", "central bank", "federal reserve",
                "bloomberg", "business",
            ],
            "health": [
                "saúde", "hospital", "médico", "vacina", "doença", "tratamento",
                "paciente", "clínica", "exame", "diagnóstico", "câncer",
                "sintoma", "medicamento", "cirurgia", "enfermagem",
                # EN keywords
                "health", "hospital", "doctor", "vaccine", "disease",
                "treatment", "patient", "medical", "clinic", "cancer",
                "diagnosis", "pharmaceutical",
            ],
"security": [
                 "polícia", "segurança", "crime", "delegacia", "tiroteio",
                 "assassinato", "roubo", "tráfico", "prisão",
                 "vitima", "suspeito", "ocorrência", "violência",
                 "baleado", "baleada", "esfaqueado",
                 "atropelado", "tiros", "balas",
                 "sequestro",
                 "feminicídio", "homicídio", "latrocínio",
                 "sequestro",
                 # EN keywords
                 "police", "crime", "murder", "killed", "shot", "stabbed",
                 "arrest", "prison", "security", "violence", "attack",
                 "robbery",
                 "trafficking", "homicide", "victim", "suspect",
             ],
            "agriculture": [
                "agronegócio", "fazenda", "campo", "agro", "soja",
                "pecuária", "colheita", "plantio", "rural", "gado",
                "safra", "agrícola", "milho", "boi",
                # EN keywords
                "agriculture", "farm", "crop", "soy", "cattle", "harvest",
                "rural", "agribusiness",
            ],
            "education": [
                "escola", "educação", "universidade", "estudante", "aluno",
                "professor", "ensino", "escolar", "aula", "vestibular",
                "enem", "faculdade", "educação",
                # EN keywords
                "education", "school", "university", "student", "teacher",
                "college", "academic", "curriculum",
            ],
            "culture": [
                "cultura", "arte", "música", "filme", "festival",
                "teatro", "exposição", "literatura", "artístico",
                "cinema", "show", "museu", "documentário", "patrimônio",
                "história", "milagre", "santo",
                # EN keywords
                "culture", "art", "music", "film", "museum", "theater",
                "theatre", "festival", "concert", "literature", "gallery",
            ],
            "clima": [
                "clima", "chuva", "temperatura", "el niño", "previsão",
                "sol", "tempo", "frio", "calor", "seca", "inundaç",
                "cheia", "meteorolog", "granizo", "nevoeiro", "tempestade",
                "estiagem", "nível", "rio", "enchente",
                # EN keywords
                "climate", "weather", "rain", "temperature", "storm",
                "flood", "drought", "forecast", "hurricane", "cyclone",
            ],
        }
        for cat, keywords in mapping.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', text) for kw in keywords):
                return category_name(cat)
        return category_name("general")
        
    def _calculate_importance(self, text: str, article: Dict) -> float:
        score = 3.0
        for keyword, weight in self.high_importance_keywords.items():
            if keyword.lower() in text:
                score = max(score, weight)
                if weight >= 4:
                    break
        for keyword, weight in self.low_importance_keywords.items():
            if keyword.lower() in text:
                score = min(score, weight)
        category = article.get('category', '')
        from app.contracts import category_name
        cat = category_name(category)
        if cat in ('politics', 'economy', 'health', 'agriculture', 'technology', 'security'):
            score = min(5.0, score + 0.4)
        elif cat == 'sports':
            score = max(2.0, score - 0.5)
        source = article.get('source', '').lower()
        tier1_sources = ['reuters', 'bloomberg', 'financial times', 'nature', 'science']
        if any(s in source for s in tier1_sources):
            score = min(5.0, score + 0.3)
        return max(1.0, min(5.0, score))
    
    def _calculate_engagement(self, text: str, article: Dict) -> float:
        score = 3.0
        for keyword, weight in self.high_engagement_keywords.items():
            if keyword.lower() in text:
                score = max(score, weight)
                if weight >= 4:
                    break
        for keyword, weight in self.low_engagement_keywords.items():
            if keyword.lower() in text:
                score = min(score, weight)
        exclamations = text.count('!')
        questions = text.count('?')
        if exclamations >= 2 or questions >= 2:
            score = min(5.0, score + 0.5)
        title_len = len(article.get('title', ''))
        if title_len > 150:
            score = max(1.0, score - 0.5)
        elif 40 <= title_len <= 90:
            score = min(5.0, score + 0.3)
        return max(1.0, min(5.0, score))
    
    def _get_importance_level(self, score: float) -> ImportanceLevel:
        if score >= 4.5: return ImportanceLevel.CRITICAL
        elif score >= 3.5: return ImportanceLevel.HIGH
        elif score >= 2.5: return ImportanceLevel.MEDIUM
        elif score >= 1.5: return ImportanceLevel.LOW
        else: return ImportanceLevel.MINIMAL
    
    def _get_engagement_level(self, score: float) -> EngagementLevel:
        if score >= 4.5: return EngagementLevel.VIRAL
        elif score >= 3.5: return EngagementLevel.HIGH
        elif score >= 2.5: return EngagementLevel.MEDIUM
        elif score >= 1.5: return EngagementLevel.LOW
        else: return EngagementLevel.MINIMAL
    
    def _get_priority_tier(self, final_score: float) -> str:
        if final_score >= 4.0: return "TIER_1"
        elif final_score >= 3.0: return "TIER_2"
        elif final_score >= 2.0: return "TIER_3"
        else: return "REJECT"
    
    def filter_by_priority(self, articles: List[Dict], min_tier: str = "TIER_3") -> List[Dict]:
        tier_order = {"TIER_1": 4, "TIER_2": 3, "TIER_3": 2, "REJECT": 1}
        min_level = tier_order.get(min_tier, 2)
        filtered = []
        for article in articles:
            tier = article.get('classification', {}).get('priority_tier', 'REJECT')
            if tier_order.get(tier, 0) >= min_level:
                filtered.append(article)
        filtered.sort(key=lambda a: a.get('classification', {}).get('final_score', 0), reverse=True)
        return filtered
