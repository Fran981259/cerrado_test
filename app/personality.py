"""
Sistema de Evolução de Personalidade — Atualiza Brasil
======================================================
Repórteres digitais evoluem com o tempo, como pessoas reais.
"""

import logging
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvolutionStage(Enum):
    """Estágios de evolução de um repórter digital."""
    NEWBORN = "newborn"              # 0-30 dias: Experimental
    DEVELOPING = "developing"        # 1-3 meses: Encontrando voz
    ESTABLISHED = "established"      # 3-6 meses: Voz consolidada
    MATURE = "mature"                # 6-12 meses: Confiança alta
    SIGNATURE = "signature"          # 12-24 meses: Marca registrada
    LEGENDARY = "legendary"          # 24+ meses: Referência no segmento


class PersonalityEvolution:
    """
    Gerencia a evolução de personalidade dos repórteres.
    
    Como uma pessoa real, o repórter:
    - Começa experimental
    - Encontra sua voz
    - Matura com experiência
    - Desenvolve estilo próprio
    - Torna-se referência
    """
    
    # Duração de cada estágio (em dias)
    STAGE_DURATIONS = {
        EvolutionStage.NEWBORN: 30,
        EvolutionStage.DEVELOPING: 60,   # 1-3 meses
        EvolutionStage.ESTABLISHED: 90,  # 3-6 meses
        EvolutionStage.MATURE: 180,      # 6-12 meses
        EvolutionStage.SIGNATURE: 365,   # 12-24 meses
        EvolutionStage.LEGENDARY: None,  # 24+ (sem fim)
    }
    
    def __init__(self):
        self.reporter_data = {}
    
    def initialize_reporter(self, slug: str, name: str, 
                           specialty: str, birth_date: datetime = None):
        """Inicializa um repórter em estágio NEWBORN."""
        self.reporter_data[slug] = {
            "slug": slug,
            "name": name,
            "specialty": specialty,
            "birth_date": birth_date or datetime.utcnow(),
            "current_stage": EvolutionStage.NEWBORN,
            "articles_published": 0,
            "experience_points": 0,
            "personality_traits": {
                "tone_confidence": 0.3,    # Começa baixo
                "style_distinctiveness": 0.2,
                "audience_trust": 0.1,
                "voice_maturity": 0.2,
                "expertise_level": 0.3,
            },
            "evolution_history": [],
            "milestones": [],
        }
        
        logger.info(f"👶 Novo repórter nasceu: {name} ({slug})")
        return self.reporter_data[slug]
    
    def get_current_stage(self, slug: str) -> EvolutionStage:
        """Retorna estágio atual do repórter baseado em idade."""
        if slug not in self.reporter_data:
            return EvolutionStage.NEWBORN
        
        data = self.reporter_data[slug]
        age_days = (datetime.utcnow() - data["birth_date"]).days
        
        cumulative_days = 0
        for stage, duration in self.STAGE_DURATIONS.items():
            if duration is None:  # LEGENDARY é o último
                return stage
            cumulative_days += duration
            if age_days < cumulative_days:
                return stage
        
        return EvolutionStage.LEGENDARY
    
    def get_personality_modifiers(self, slug: str) -> Dict:
        """
        Retorna modificadores de personalidade baseados no estágio.
        Estes modificadores são aplicados ao prompt do repórter.
        """
        stage = self.get_current_stage(slug)
        
        modifiers = {
            EvolutionStage.NEWBORN: {
                "tone": "experimental, descobrindo sua voz",
                "confidence": "cauteloso, aprendendo",
                "style_notes": "Segue padrões básicos, sem ousadia",
                "vocabulary": "simples, direto",
                "engagement_strategy": "factual, informativo",
            },
            EvolutionStage.DEVELOPING: {
                "tone": "ganhando confiança, voz emergindo",
                "confidence": "crescente, mais assertivo",
                "style_notes": "Começa a ter estilo próprio",
                "vocabulary": "expandindo repertório",
                "engagement_strategy": "contextual, adicionando personalidade",
            },
            EvolutionStage.ESTABLISHED: {
                "tone": "confiante, voz consolidada",
                "confidence": "alto, sabe quem é",
                "style_notes": "Estilo próprio reconhecível",
                "vocabulary": "rico e variado",
                "engagement_strategy": "conexão com leitor, opinião embasada",
            },
            EvolutionStage.MATURE: {
                "tone": "autoridade no assunto",
                "confidence": "muito alto, seguro",
                "style_notes": "Marca registrada, assinatura clara",
                "vocabulary": "preciso, terminologia específica",
                "engagement_strategy": "análise profunda, perspectiva única",
            },
            EvolutionStage.SIGNATURE: {
                "tone": "icônico, instantaneamente reconhecível",
                "confidence": "total, voz única",
                "style_notes": "Inconfundível, leitores fiéis",
                "vocabulary": "exclusivo, criou jargões próprios",
                "engagement_strategy": "provocativo inteligente, lealdade total",
            },
            EvolutionStage.LEGENDARY: {
                "tone": "lendário, referência no setor",
                "confidence": "absoluta, definiu o padrão",
                "style_notes": "Escola de jornalismo, citado por outros",
                "vocabulary": "criou termos, dita tendências",
                "engagement_strategy": "influencia o debate público",
            },
        }
        
        return modifiers.get(stage, modifiers[EvolutionStage.NEWBORN])
    
    def record_publication(self, slug: str, article: Dict):
        """Registra publicação e atualiza evolução."""
        if slug not in self.reporter_data:
            return
        
        data = self.reporter_data[slug]
        data["articles_published"] += 1
        data["experience_points"] += self._calculate_xp(article)
        
        # Atualiza traits baseado no XP
        self._update_personality_traits(slug)
        
        # Verifica milestones
        self._check_milestones(slug)
    
    def _calculate_xp(self, article: Dict) -> int:
        """Calcula XP baseado na qualidade do artigo."""
        xp = 10  # Base
        
        # Bônus por qualidade
        quality = article.get("quality_score", 5.0)
        if quality >= 9.0:
            xp += 20
        elif quality >= 7.0:
            xp += 10
        
        # Bônus por engajamento
        engagement = article.get("engagement_score", 3.0)
        if engagement >= 4.5:
            xp += 15
        
        # Bônus se for Tier 1
        if article.get("priority_tier") == "TIER_1":
            xp += 25
        
        return xp
    
    def _update_personality_traits(self, slug: str):
        """Atualiza traits de personalidade baseado em experiência."""
        data = self.reporter_data[slug]
        xp = data["experience_points"]
        articles = data["articles_published"]
        
        # Calcula novos traits (crescimento logarítmico)
        import math
        
        data["personality_traits"]["tone_confidence"] = min(
            1.0, 0.3 + math.log10(articles + 1) * 0.2
        )
        data["personality_traits"]["style_distinctiveness"] = min(
            1.0, 0.2 + math.log10(articles + 1) * 0.15
        )
        data["personality_traits"]["audience_trust"] = min(
            1.0, 0.1 + math.log10(articles + 1) * 0.18
        )
        data["personality_traits"]["voice_maturity"] = min(
            1.0, 0.2 + math.log10(articles + 1) * 0.22
        )
        data["personality_traits"]["expertise_level"] = min(
            1.0, 0.3 + math.log10(xp + 1) * 0.12
        )
    
    def _check_milestones(self, slug: str):
        """Verifica e registra milestones."""
        data = self.reporter_data[slug]
        articles = data["articles_published"]
        
        milestones_to_check = [
            (10, "primeira_materia", "🎉 Primeira matéria publicada"),
            (50, "voz_emergindo", "💫 Voz editorial emergindo"),
            (100, "centena", "💯 100 matérias publicadas"),
            (250, "estabelecido", "⭐ Repórter estabelecido"),
            (500, "autoridade", "👑 Autoridade no segmento"),
            (1000, "lendario", "🏆 Repórter lendário"),
            (2500, "mito", "🌟 Mito do jornalismo"),
        ]
        
        for count, milestone_id, description in milestones_to_check:
            if articles >= count and milestone_id not in [m["id"] for m in data["milestones"]]:
                milestone = {
                    "id": milestone_id,
                    "description": description,
                    "reached_at": datetime.utcnow().isoformat(),
                    "articles_at_milestone": count,
                }
                data["milestones"].append(milestone)
                logger.info(f"🎖️ {data['name']}: {description}")
    
    def get_evolution_prompt_modifier(self, slug: str) -> str:
        """
        Retorna texto para adicionar ao prompt do repórter
        baseado em seu estágio evolutivo.
        """
        stage = self.get_current_stage(slug)
        modifiers = self.get_personality_modifiers(slug)
        data = self.reporter_data.get(slug, {})
        traits = data.get("personality_traits", {})
        
        prompt_addition = f"""

=== EVOLUÇÃO EDITORIAL ===
Estágio atual: {stage.value.upper()}
- Tom: {modifiers['tone']}
- Confiança: {modifiers['confidence']}
- Estilo: {modifiers['style_notes']}
- Vocabulário: {modifiers['vocabulary']}
- Estratégia de engajamento: {modifiers['engagement_strategy']}

Traits de personalidade:
- Confiança no tom: {traits.get('tone_confidence', 0.3):.1%}
- Distintividade de estilo: {traits.get('style_distinctiveness', 0.2):.1%}
- Confiança do público: {traits.get('audience_trust', 0.1):.1%}
- Maturidade de voz: {traits.get('voice_maturity', 0.2):.1%}
- Nível de expertise: {traits.get('expertise_level', 0.3):.1%}

Total de matérias publicadas: {data.get('articles_published', 0)}
"""
        return prompt_addition
    
    def get_reporter_summary(self, slug: str) -> Dict:
        """Retorna resumo do estado evolutivo do repórter."""
        if slug not in self.reporter_data:
            return None
        
        data = self.reporter_data[slug]
        stage = self.get_current_stage(slug)
        
        return {
            "name": data["name"],
            "slug": data["slug"],
            "specialty": data["specialty"],
            "current_stage": stage.value,
            "age_days": (datetime.utcnow() - data["birth_date"]).days,
            "articles_published": data["articles_published"],
            "experience_points": data["experience_points"],
            "personality_traits": data["personality_traits"],
            "milestones_reached": len(data["milestones"]),
            "next_milestone": self._get_next_milestone(data["articles_published"]),
        }
    
    def _get_next_milestone(self, current_articles: int) -> Dict:
        """Retorna próximo milestone."""
        milestones = [10, 50, 100, 250, 500, 1000, 2500]
        for m in milestones:
            if current_articles < m:
                return {
                    "target": m,
                    "remaining": m - current_articles,
                    "progress": f"{(current_articles/m)*100:.1f}%",
                }
        return {"target": None, "remaining": 0, "progress": "100%"}


# ============================================================
# Instância global
# ============================================================
evolution_system = PersonalityEvolution()
