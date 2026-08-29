"""
Tarefas de Auditoria — Atualiza Brasil
Agente HORUS + Evolução de Personalidade
"""

from app.celery_app import celery_app
from app.auditor import horus, HorusAuditor
from app.personality import evolution_system, PersonalityEvolution
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@celery_app.task(
    name="app.tasks.auditor_tasks.full_audit",
    bind=True,
    max_retries=3
)
def full_audit(self):
    """
    Executa auditoria completa do sistema (HORUS).
    Roda a cada hora.
    """
    try:
        logger.info("👁️ HORUS: Iniciando auditoria completa")
        auditor = HorusAuditor()
        report = auditor.audit_all()
        
        # Log do resultado
        logger.info(f"👁️ HORUS: Status = {report['overall_status']}")
        logger.info(f"👁️ HORUS: {len(report['alerts'])} alertas")
        
        return report
        
    except Exception as e:
        logger.error(f"👁️ HORUS: Erro na auditoria: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.auditor_tasks.audit_agents",
    bind=True,
    max_retries=3
)
def audit_agents(self):
    """Audita apenas os agentes."""
    try:
        logger.info("👁️ HORUS: Auditando agentes")
        auditor = HorusAuditor()
        agents = auditor._audit_agents()
        return {"status": "success", "agents": agents}
    except Exception as e:
        logger.error(f"👁️ HORUS: Erro ao auditar agentes: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.auditor_tasks.audit_reporters",
    bind=True,
    max_retries=3
)
def audit_reporters(self):
    """Audita apenas os repórteres."""
    try:
        logger.info("👁️ HORUS: Auditando repórteres")
        auditor = HorusAuditor()
        reporters = auditor._audit_reporters()
        return {"status": "success", "reporters": reporters}
    except Exception as e:
        logger.error(f"👁️ HORUS: Erro ao auditar repórteres: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.auditor_tasks.evolve_reporters",
    bind=True,
    max_retries=3
)
def evolve_reporters(self):
    """
    Atualiza evolução de personalidade dos repórteres.
    Roda 1x ao dia.
    """
    try:
        logger.info("📈 Sistema de Evolução: Atualizando repórteres")
        evolution = PersonalityEvolution()
        
        # Inicializa repórteres se necessário
        reporters = [
            ("enzo.bianchi", "Enzo Bianchi", "Tecnologia"),
            ("marcus.teixeira", "Marcus Teixeira", "Esportes"),
            ("rafael.dumas", "Rafael Dumas", "Segurança"),
            ("luciana.freitas", "Luciana Freitas", "Política"),
            ("maya.santos", "Maya Santos", "Saúde"),
            ("lucas.nakamura", "Lucas Nakamura", "Educação"),
            ("bia.fernandes", "Bia Fernandes", "Agronegócio"),
            ("leon.vaz", "Leon Vaz", "Cultura"),
            ("camila.rocha", "Camila Rocha", "Economia"),
        ]
        
        results = []
        for slug, name, specialty in reporters:
            if slug not in evolution.reporter_data:
                evolution.initialize_reporter(slug, name, specialty)
            
            summary = evolution.get_reporter_summary(slug)
            results.append(summary)
        
        logger.info(f"📈 {len(results)} repórteres atualizados")
        return {"status": "success", "reporters": results}
        
    except Exception as e:
        logger.error(f"📈 Erro na evolução: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.auditor_tasks.get_prompt_modifier",
    bind=True,
    max_retries=3
)
def get_prompt_modifier(self, reporter_slug: str):
    """
    Retorna modificador de prompt para o repórter
    baseado em seu estágio evolutivo.
    """
    try:
        evolution = PersonalityEvolution()
        
        # Inicializa se não existe
        if reporter_slug not in evolution.reporter_data:
            reporters = {
                "enzo.bianchi": ("Enzo Bianchi", "Tecnologia"),
                "marcus.teixeira": ("Marcus Teixeira", "Esportes"),
                "rafael.dumas": ("Rafael Dumas", "Segurança"),
                "luciana.freitas": ("Luciana Freitas", "Política"),
                "maya.santos": ("Maya Santos", "Saúde"),
                "lucas.nakamura": ("Lucas Nakamura", "Educação"),
                "bia.fernandes": ("Bia Fernandes", "Agronegócio"),
                "leon.vaz": ("Leon Vaz", "Cultura"),
                "camila.rocha": ("Camila Rocha", "Economia"),
            }
            if reporter_slug in reporters:
                name, specialty = reporters[reporter_slug]
                evolution.initialize_reporter(reporter_slug, name, specialty)
            else:
                return {"error": "Repórter não encontrado"}
        
        modifier = evolution.get_evolution_prompt_modifier(reporter_slug)
        summary = evolution.get_reporter_summary(reporter_slug)
        
        return {
            "status": "success",
            "prompt_modifier": modifier,
            "reporter_summary": summary,
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter modificador: {e}")
        raise self.retry(exc=e)


@celery_app.task(
    name="app.tasks.auditor_tasks.record_publication",
    bind=True,
    max_retries=3
)
def record_publication(self, reporter_slug: str, article: dict):
    """Registra publicação e atualiza XP do repórter."""
    try:
        evolution = PersonalityEvolution()
        evolution.record_publication(reporter_slug, article)
        return {"status": "success", "slug": reporter_slug}
    except Exception as e:
        logger.error(f"Erro ao registrar publicação: {e}")
        raise self.retry(exc=e)
