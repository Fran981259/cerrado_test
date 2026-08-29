"""
Curiosidades — Atualiza Brasil
==============================
Gerador e classificador de curiosidades para distribuição entre segmentos.
"""

import random
import logging
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CuriosityCategory(Enum):
    """Categorias de curiosidade por segmento."""
    TECHNOLOGY = "technology"
    SPORTS = "sports"
    SECURITY = "security"
    POLITICS = "politics"
    HEALTH = "health"
    EDUCATION = "education"
    AGRICULTURE = "agriculture"
    CULTURE = "culture"
    ECONOMY = "economy"


class CuriosityPatterns:
    """
    Padrões que indicam que uma matéria é uma curiosidade.
    
    Usado para DETECTAR curiosidades externas E gerar curiosidades próprias.
    """
    
    DETECTION_PATTERNS = {
        # English
        "did you know": "curiosity",
        "you may not know": "curiosity",
        "fun fact": "curiosity",
        "interesting fact": "curiosity",
        "little known": "curiosity",
        "rarely known": "curiosity",
        "surprising": "curiosity",
        "unbelievable": "curiosity",
        "amazing": "curiosity",
        "incredible": "curiosity",
        "strange but true": "curiosity",
        
        # Portuguese
        "você sabia": "curiosity",
        "sabia que": "curiosity",
        "curiosidade": "curiosity",
        "fato interessante": "curiosity",
        "poucos sabem": "curiosity",
        "raramente conhecido": "curiosity",
        "surpreendente": "curiosity",
        "incrível": "curiosity",
        "impressionante": "curiosity",
        "será que": "curiosity",
        "o número": "curiosity",
        "quantos": "curiosity",
        "quanto tempo": "curiosity",
        "a maior": "curiosity",
        "o menor": "curiosity",
        "o mais": "curiosity",
        "recorde": "curiosity",
        "nunca imaginou": "curiosity",
    }
    
    ENGAGEMENT_BOOST = 1.3  # Curiosidades têm +30% de engajamento


class CuriosityTemplates:
    """
    Templates de curiosidade por segmento.
    
    Estes são usados para GERAR curiosidades próprias baseadas em fatos reais.
    """
    
    TEMPLATES = {
        CuriosityCategory.TECHNOLOGY: [
            "Você sabia que o primeiro computador pesava cerca de 30 toneladas e ocupava um cômodo inteiro?",
            "O primeiro e-mail da história foi enviado em 1971. Você consegue imaginar a internet naquela época?",
            "Existem mais dispositivos móveis no mundo do que pessoas. O que isso significa para o futuro?",
            "O teclado QWERTY foi projetado para lentificar a digitação — tudo por causa das máquinas de escrever!",
            "Mais de 90% das pesquisas globais passam pelo Google. A internet é mais centralizada do que parece.",
            "A primeira mensagem enviada pela internet foi 'LO'. Era para ser 'LOGIN', mas o sistema travou.",
            "O Bluetooth foi nomeado em homenagem a um rei Viking do século X. Rei Harald Bluetooth.",
            "Seu smartphone tem mais poder de processamento do que os computadores que levaram astronautas à Lua.",
            "O primeiro tweet foi enviado em 2006: 'just setting up my twttr'. Como a comunicação mudou!",
            "Mais de 4 milhões de apps estão disponíveis nas stores. Já parou para pensar em quantos nunca foram baixados?",
        ],
        CuriosityCategory.SPORTS: [
            "A bola de futebol usada na primeira Copa do Mundo pesava quase o dobro das atuais. Impressionante, não?",
            "O maior estádio do mundo, em Pyongyang, na Coreia do Norte, comporta 114.000 pessoas. Gigantesco!",
            "O futebol é o esporte mais praticado no mundo. Mais de 4 bilhões de fãs ao redor do globo.",
            "O primeiro jogo de futebol profissional no Brasil aconteceu em 1895. Já pensou como era o futebol naquela época?",
            "A maratona tem exatamente 42.195 metros por causa da família real britânica. Curioso, não?",
            "O gol mais rápido da história foi marcado em apenas 2 segundos. Maldade pura!",
            "O Japão tem mais times de beisebol profissional do que os Estados Unidos. Quem diria, né?",
            "A primeira mulher a correr uma maratona oficialmente foi Kathrine Switzer, em 1967, mesmo sendo proibido.",
            "O futebol é responsável por mais de 4 milhões de empregos no mundo. Muito além das quadras.",
            "O recorde de público em um jogo de futebol no Brasil foi de 198.000 pessoas. Imperdível!",
        ],
        CuriosityCategory.HEALTH: [
            "O coração humano bate em média 100.000 vezes por dia. Mais de 35 milhões de vezes por ano. Incrível!",
            "Nosso corpo tem mais bactérias do que células próprias. A maioria é essencial para nossa saúde.",
            "Rir ativamente pode queimar calorias. Sim, rir é um exercício!",
            "O cérebro humano consome 20% de toda a energia do corpo. Só 2% do peso, mas 20% da energia!",
            "Você sabia que o estômago muda de tamanho ao longo do dia? Pode variar de 75ml a 1 litro.",
            "O nariz humano pode detectar mais de 1 trilhão de odores. Muito mais do que imaginamos.",
            "Cerca de 70% do sistema imunológico está no intestino. A saúde começa por dentro.",
            "O corpo humano emite luz visível. Somos literalmente brilhantes, mas a luz é fraca demais para ver.",
            "Cada pessoa tem uma impressão digital exclusiva. Nem mesmo gêmeos idênticos são exatamente iguais.",
            "O sangue percorre todo o corpo em apenas 60 segundos. A máquina perfeita.",
        ],
        CuriosityCategory.ECONOMY: [
            "O Brasil foi o único país do mundo que teve sua dívida pública paga por inteiro. Quando, em 2006.",
            "A primeira moeda brasileira, o Real, foi criada em 1695. Muito antes do Real atual.",
            "A maior nota já impressa no Brasil foi de 500 reais. Você chegou a ver uma?",
            "O termo 'salário' vem do latim 'salarium', que era a quantidade de sal dada aos soldados romanos.",
            "O Brasil é o 7º maior PIB do mundo, mas ainda enfrenta desafios de desigualdade econômica.",
            "A primeira bolsa de valores do mundo foi criada em Amberes, na Bélgica, em 1531. Quase 500 anos!",
            "O conceito de 'lucro' tem origem nas velas de sebo. Lucrum em latim significa ganho.",
            "Mais de 50% da riqueza mundial está nas mãos de apenas 1% da população. Desigualdade global.",
            "O Bitcoin foi criado em 2009. Menos de 15 anos e já mudou a forma de pensar sobre dinheiro.",
            "O Brasil é o maior produtor de laranja do mundo. Muito além do suco que consumimos.",
        ],
        CuriosityCategory.SECURITY: [
            "O primeiro hacker da história foi um adolescente de 15 anos em 1960. Chamava-se Kevin Mitnick.",
            "A senha mais comum do mundo ainda é '123456'. Mesmo após tantas violações conhecidas.",
            "O Brasil está entre os 10 países mais atacados por cibercrimes. A segurança digital é essencial.",
            "Mais de 80% das invasões digitais começam com um e-mail phishing. Cuidado com links suspeitos!",
            "O primeiro vírus de computador foi criado em 1971 e não causava danos — apenas mostrava um poema.",
            "A Polícia Federal brasileira foi criada em 1944, durante o governo de Getúlio Vargas.",
            "O CPF tem um dígito verificador calculado por um algoritmo específico. Você sabia disso?",
            "O Brasil tem mais de 130 milhões de veículos. Ruas cada vez mais disputadas.",
            "O primeiro sistema de segurança com senha foi criado em 1961 no MIT. A senha era fácil.",
            "Mais de 60% dos brasileiros já foram vítimas de algum tipo de crime virtual. Esteja atento!",
        ],
        CuriosityCategory.POLITICS: [
            "O Brasil foi descoberto em 1500, mas só virou independente em 1822. Mais de 300 anos de colônia.",
            "A primeira eleição direta para presidente no Brasil foi em 1985, após anos de ditadura militar.",
            "O Congresso Nacional brasileiro é bicameral: Câmara e Senado. Como nos Estados Unidos.",
            "O voto no Brasil é obrigatório para maiores de 18 anos. Uma das maiores democracias do mundo.",
            "A Carta Magna, primeiro documento sobre direitos humanos, tem 800 anos. De 1215, na Inglaterra.",
            "O Brasil tem 27 unidades federativas, mais o Distrito Federal. O maior país da América do Sul.",
            "A ONU foi criada em 1945, após a Segunda Guerra Mundial. 51 países assinaram inicialmente.",
            "A democracia ateniense, berço da palavra, não permitia voto de mulheres nem escravos. Ironia.",
            "O Brasil já teve 5 constituições. A atual é de 1988, após o fim da ditadura militar.",
            "Mais de 150 países têm eleição marcada em 2024. Um ano de escolhas globais.",
        ],
        CuriosityCategory.EDUCATION: [
            "A biblioteca mais antiga do mundo foi fundada no século VII a.C., no Egito. Milhares de rolos.",
            "A Universidade de Bologna, na Itália, é a mais antiga do mundo ainda em funcionamento. Desde 1088.",
            "O Brasil tem mais de 2.000 universidades. Mais de 8 milhões de estudantes universitários.",
            "A palavra 'escola' vem do grego 'schole', que significa 'ócio' ou 'tempo livre'. Para pensar!",
            "O primeiro diploma de medicina no Brasil foi concedido em 1808, no Rio de Janeiro.",
            "A prova do ENEM tem mais de 180 questões. Mais de 6 horas de prova em um dia.",
            "Mais de 70% dos adultos brasileiros usam o celular para estudar. A educação mudou para sempre.",
            "A primeira universidade brasileira foi fundada em 1920: a Universidade do Rio de Janeiro (UFRJ).",
            "Albert Einstein não foi reprovado em matemática. Fake news sobre gênios que marca.",
            "O Brasil está entre os 10 países que mais publicam artigos científicos. Pesquisa em alta.",
        ],
        CuriosityCategory.AGRICULTURE: [
            "O Brasil é o maior produtor de soja do mundo, com mais de 30% da produção global.",
            "Uma única árvore de eucalipto pode produzir mais papel do que meio hectare de floresta nativa.",
            "O café foi introduzido no Brasil em 1727, quando o sargento-mor Francisco de Melo Palheta plantou as primeiras mudas.",
            "O Brasil tem mais de 350 milhões de hectares de terra agricultável. Um terço do território nacional.",
            "A laranja é originária da Ásia, mas o Brasil é o maior produtor mundial há mais de 100 anos.",
            "Uma vaca produz em média 30 litros de leite por dia. Uma trabalhadora incansável do campo!",
            "O agronegócio representa quase 25% do PIB brasileiro. O campo sustenta o país.",
            "O Brasil é o maior exportador de carne bovina do mundo. Churrasco é questão nacional.",
            "A produtividade do leite brasileiro triplicou nas últimas décadas. Tecnologia no campo.",
            "Mais de 70% das terras indígenas não são utilizadas para agricultura. Preservação e tradição.",
        ],
        CuriosityCategory.CULTURE: [
            "A Mona Lisa não tem sobrancelhas. Na época, era comum raspá-las na França renascentista.",
            "O Brasil tem 215 milhões de habitantes e mais de 300 etnias indígenas. A maior diversidade do mundo.",
            "O primeiro filme brasileiro foi 'O Descobrimento do Brasil', de 1898. Mais de 120 anos de cinema.",
            "A capoeira foi criada por escravos como forma de resistência. Hoje é patrimônio da humanidade.",
            "O Museu do Amanhã, no Rio, foi considerado o melhor museu de ciências do mundo. Orgulho brasileiro.",
            "A palavra 'saudade' não tem tradução exata em nenhum outro idioma. Totalmente brasileira.",
            "O Brasil tem 8 patrimonios mundiais da UNESCO. Da Amazônia ao Rio, cultura de todos os jeitos.",
            "O frevo de Pernambuco tem mais de 100 anos e foi criado nos carnavais de Recife e Olinda.",
            "O funk brasileiro é o ritmo mais ouvido no Brasil. Da periferia para o mundo.",
            "O Brasil já venceu o Oscar de cinema três vezes com filmes como Central do Brasil e Cidade de Deus.",
        ],
    }
    
    # Templates de abertura para curiosidade
    OPENINGS = [
        "Você sabia que",
        "Curiosidade:",
        "Fato interessante:",
        "Poucos sabem que",
        "Impressionante:",
        "Surpreendente:",
        "Raramente conhecido:",
        "Vamos lá:",
        "Atenção:",
        "Falando em números:",
    ]


class CuriosityGenerator:
    """
    Gerador de curiosidades para cada segmento.
    
    Pode gerar curiosidades próprias OU detectar e potencializar curiosidades externas.
    """
    
    def __init__(self):
        self.templates = CuriosityTemplates()
        self.patterns = CuriosityPatterns()
        self._load_reporters()
    
    def _load_reporters(self):
        """Carrega mapeamento de repórteres por categoria."""
        self.reporter_map = {
            CuriosityCategory.TECHNOLOGY: "enzo.bianchi",
            CuriosityCategory.SPORTS: "marcus.teixeira",
            CuriosityCategory.HEALTH: "maya.santos",
            CuriosityCategory.ECONOMY: "camila.rocha",
            CuriosityCategory.SECURITY: "rafael.dumas",
            CuriosityCategory.POLITICS: "luciana.freitas",
            CuriosityCategory.EDUCATION: "lucas.nakamura",
            CuriosityCategory.AGRICULTURE: "bia.fernandes",
            CuriosityCategory.CULTURE: "leon.vaz",
        }
    
    def detect_curiosity(self, article: Dict) -> bool:
        """Detecta se um artigo é uma curiosidade."""
        title = article.get('title', '').lower()
        summary = article.get('summary', '').lower()
        combined = title + ' ' + summary
        
        for pattern in self.patterns.DETECTION_PATTERNS.keys():
            if pattern in combined:
                return True
        
        return False
    
    def boost_engagement(self, article: Dict) -> Dict:
        """Aumenta score de engajamento para curiosidades."""
        if self.detect_curiosity(article):
            current = article.get('classification', {}).get('engagement_score', 3.0)
            boosted = min(5.0, current * self.patterns.ENGAGEMENT_BOOST)
            
            if 'classification' not in article:
                article['classification'] = {}
            article['classification']['engagement_score'] = round(boosted, 2)
            article['classification']['is_curiosity'] = True
        
        return article
    
    def generate_curiosity(self, category: CuriosityCategory) -> Dict:
        """Gera uma curiosidade própria para uma categoria."""
        templates = self.templates.TEMPLATES.get(category, [])
        
        if not templates:
            return None
        
        # Escolhe curiosidade aleatória
        content = random.choice(templates)
        opening = random.choice(self.templates.OPENINGS)
        
        # Monta título com abertura
        if not any(content.startswith(o) for o in self.templates.OPENINGS):
            title = f"{opening} {content.split('.')[0]}!"
        else:
            title = content.split('.')[0] + "!"
        
        curiosity = {
            'title': title.capitalize(),
            'summary': content,
            'source': 'Curiosidade Própria',
            'source_url': '',
            'source_lang': 'pt-BR',
            'category': category.value,
            'image_url': None,
            'published_at': datetime.utcnow().isoformat(),
            'mined_at': datetime.utcnow().isoformat(),
            'hash': f"curiosity_{category.value}_{random.randint(1000, 9999)}",
            'requires_translation': False,
            'is_curiosity': True,
            'is_original_content': True,
            'reporter_slug': self.reporter_map.get(category),
            'classification': {
                'importance_score': 2.0,
                'engagement_score': 4.5,  # Curiosidades têm alto engajamento
                'final_score': 3.2,  # Bônus de engajamento
                'importance_level': 'LOW',
                'engagement_level': 'VIRAL',
                'priority_tier': 'TIER_2',
                'is_curiosity': True,
                'classified_at': datetime.utcnow().isoformat(),
            },
        }
        
        return curiosity
    
    def generate_daily_curiosities(self) -> List[Dict]:
        """Gera lote diário de curiosidades (1 por categoria)."""
        curiosities = []
        
        for category in CuriosityCategory:
            curiosity = self.generate_curiosity(category)
            if curiosity:
                curiosities.append(curiosity)
        
        return curiosities


class CuriosityMixer:
    """
    Misturador de curiosidades no fluxo de publicação.
    
    Adiciona curiosidades em momentos estratégicos do dia.
    """
    
    def __init__(self):
        self.generator = CuriosityGenerator()
    
    def inject_curiosities(self, articles: List[Dict], 
                          daily_target: int = 50,
                          curiosity_ratio: float = 0.15) -> List[Dict]:
        """
        Injeta curiosidades no fluxo de artigos.
        
        Args:
            articles: Lista de artigos classificados
            daily_target: Meta diária de publicação
            curiosity_ratio: % de curiosidades no total (15% = ~8 curiosidades/dia)
        
        Returns:
            Lista de artigos com curiosidades injetadas
        """
        # Quantidade de curiosidades a gerar
        n_curiosities = max(3, int(daily_target * curiosity_ratio))
        
        # Gera curiosidades
        generated = self.generator.generate_daily_curiosities()
        
        # Limita se necessário
        if len(generated) > n_curiosities:
            random.shuffle(generated)
            generated = generated[:n_curiosities]
        
        # Intercala curiosidades na lista de artigos
        result = []
        cur_idx = 0
        
        for i, article in enumerate(articles):
            result.append(article)
            
            # A cada ~7 artigos, injeta uma curiosidade
            if (i + 1) % 7 == 0 and cur_idx < len(generated):
                result.append(generated[cur_idx])
                cur_idx += 1
        
        # Adiciona curiosidades restantes no final
        while cur_idx < len(generated):
            result.append(generated[cur_idx])
            cur_idx += 1
        
        return result


# Funções de conveniência
def detect_curiosity(article: Dict) -> bool:
    """Detecta se um artigo é curiosidade."""
    generator = CuriosityGenerator()
    return generator.detect_curiosity(article)


def boost_article(article: Dict) -> Dict:
    """Aplica boost de engajamento em curiosidade."""
    generator = CuriosityGenerator()
    return generator.boost_engagement(article)


def generate_curiosity_for_category(category: str) -> Optional[Dict]:
    """Gera curiosidade para uma categoria específica."""
    generator = CuriosityGenerator()
    try:
        cat_enum = CuriosityCategory(category)
        return generator.generate_curiosity(cat_enum)
    except ValueError:
        return None


def generate_all_daily_curiosities() -> List[Dict]:
    """Gera curiosidades para todas as categorias."""
    generator = CuriosityGenerator()
    return generator.generate_daily_curiosities()


def mix_with_articles(articles: List[Dict], daily_target: int = 50) -> List[Dict]:
    """Mistura curiosidades com artigos normais."""
    mixer = CuriosityMixer()
    return mixer.inject_curiosities(articles, daily_target)


# Demo
if __name__ == "__main__":
    print("=" * 60)
    print("CURIOSIDADES DO DIA — ATUALIZA BRASIL")
    print("=" * 60)
    
    generator = CuriosityGenerator()
    
    print("\n📚 Curiosidades Geradas:\n")
    
    for cat in CuriosityCategory:
        curiosity = generator.generate_curiosity(cat)
        if curiosity:
            print(f"🗂️ {cat.value.upper()}")
            print(f"   📰 {curiosity['title']}")
            print(f"   ✍️  {curiosity['reporter_slug']}")
            print()
    
    print("-" * 60)
    print("\n📊 Resumo:")
    all_curiosities = generator.generate_daily_curiosities()
    print(f"Total: {len(all_curiosities)} curiosidades (1 por categoria)")
    
    print("\n⚡ Curiosidades têm +30% de engajamento!")
