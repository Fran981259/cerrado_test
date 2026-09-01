"""
Entry point principal — Portal Cerrado
Orquestra todos os agentes e gerencia o ciclo diário.
"""

import logging
import time
import schedule
import threading
from datetime import datetime
from typing import Dict, List
import yaml

from app.scanner import scan_all_portals
from app.rewriter import load_reporters_config, rewrite_for_category
from app.publisher import ArticlePublisher


def load_config(path: str = "config/orchestrator.yaml") -> dict:
    """Carrega a configuração do orquestrador."""
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/atualiza_brasil.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('atualiza_brasil')


def setup_logging():
    """Configura o logging para produção."""
    pass  # Já configurado acima


def daily_job():
    """Trabalho diário que roda a cada hora."""
    logger.info(f"=== Iniciando ciclo de coleta - {datetime.utcnow().isoformat()} ===")
    
    # 1. Carregar configurações
    try:
        config = load_config()
        reporters = load_reporters_config()
        logger.info(f"Carregadas {len(reporters)} configurações de repórteres")
    except Exception as e:
        logger.error(f"Erro ao carregar configurações: {e}")
        return
    
    # 2. Escanear portais
    try:
        scan_results = scan_all_portals()
        logger.info(f"Escaneamento concluído: {scan_results['summary']}")
    except Exception as e:
        logger.error(f"Erro no escaneamento: {e}")
        return
    
    # 3. Processar por categoria (conforme cronograma)
    for category in ['technology', 'sports', 'security', 'politics', 'health', 'education', 'agriculture', 'culture', 'economy']:
        logger.info(f"Processando categoria: {category}")
        
        # Filtrar artigos relevantes para a categoria
        relevant_articles = _filter_articles_for_category(scan_results, category)
        
        for article in relevant_articles:
            try:
                # Reescrever com a voz do repórter
                rewritten = rewrite_for_category(category, article)
                if rewritten:
                    # Publicar
                    publisher = ArticlePublisher()
                    result = publisher.publish_article(rewritten)
                    logger.info(f"Artigo publicado: {result.get('slug', 'N/A')}")
                else:
                    logger.warning(f"Falha na reescrita para {category}: {article.get('title', 'N/A')}")
            except Exception as e:
                logger.error(f"Erro ao processar artigo: {e}")
                continue
    
    logger.info(f"=== Ciclo concluído - {datetime.utcnow().isoformat()} ===")


def _filter_articles_for_category(scan_results: Dict, category: str) -> List[Dict]:
    """Filtra artigos por categoria usando palavras-chave."""
    keywords = {
        'technology': ['tecnologia', 'inovação', 'app', 'software', 'startup', 'digital', 'ti'],
        'sports': ['futebol', 'esporte', 'campeonato', 'time', 'jogador', 'partida', 'torneio'],
        'security': ['segurança', 'polícia', 'crime', 'investigação', 'suspeito', 'flagrante'],
        'politics': ['governo', 'política', 'lei', 'decreto', 'parlamento', 'eleição', 'prefeito'],
        'health': ['saúde', 'hospitalar', 'doença', 'tratamento', 'prevenção', 'vacina', 'medico'],
        'education': ['educação', 'universidade', 'estudante', 'curso', 'concurso', 'escola', 'professor'],
        'agriculture': ['agronegócio', 'safra', 'produtor', 'exportação', 'agro', 'campo', 'plantio'],
        'culture': ['cultura', 'evento', 'show', 'arte', 'festival', 'música', 'teatro', 'cinema'],
        'economy': ['economia', 'mercado', 'emprego', 'bolsa', 'investimento', 'crédito', 'inflação']
    }
    
    category_keywords = keywords.get(category, [])
    filtered = []
    
    for portal_url, result in scan_results.get('scan_results', {}).items():
        if result['status'] != 'success':
            continue
            
        for headline in result.get('headlines', []):
            title = headline.get('title', '').lower()
            if any(kw in title for kw in category_keywords):
                filtered.append(headline)
    
    return filtered


def run_scheduler():
    """Executa o agendador em background."""
    # Trabalho a cada 30 minutos
    schedule.every(30).minutes.do(daily_job)
    
    # Trabalho imediato ao iniciar
    daily_job()
    
    while True:
        schedule.run_pending()
        time.sleep(60)


def main():
    """Função principal."""
    logger.info("=== Portal Cerrado Iniciado ===")
    logger.info(f"Versão: 1.0.0")
    logger.info(f"Iniciado em: {datetime.utcnow().isoformat()}")
    
    # Iniciar agendador em thread separada
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    # Manter thread principal viva
    try:
        while True:
            time.sleep(3600)  # Dorme por 1 hora
    except KeyboardInterrupt:
        logger.info("Recebido sinal de interrupção. Finalizando...")
    except Exception as e:
        logger.error(f"Erro crítico: {e}")
    finally:
        logger.info("Portal Cerrado finalizado.")


if __name__ == "__main__":
    main()