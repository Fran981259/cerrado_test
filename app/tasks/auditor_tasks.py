"""
Tarefas de Auditoria — Portal Cerrado
Agente HORUS + Evolução de Personalidade
"""

import logging

from app.auditor import HorusAuditor
from app.celery_app import celery_app
from app.personality import PersonalityEvolution

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.auditor_tasks.full_audit", bind=True, max_retries=3)
def full_audit(self):
    """
    Executa auditoria completa do sistema (HORUS).
    Roda a cada hora.
    """
    try:
        logger.info("👁️ HORUS: Iniciando auditoria completa")
        auditor = HorusAuditor()
        report = auditor.audit_all()

        logger.info(f"👁️ HORUS: Status = {report['overall_status']}")
        logger.info(f"👁️ HORUS: {len(report['alerts'])} alertas")

        return report

    except Exception as e:
        logger.error(f"👁️ HORUS: Erro na auditoria: {e}")
        raise self.retry(exc=e)


@celery_app.task(name="app.tasks.auditor_tasks.evolve_reporters", bind=True, max_retries=3)
def evolve_reporters(self):
    """
    Atualiza evolução de personalidade dos repórteres.
    Roda 1x ao dia.
    """
    try:
        logger.info("📈 Sistema de Evolução: Atualizando repórteres")
        evolution = PersonalityEvolution()

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
