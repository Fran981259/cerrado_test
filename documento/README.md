# Portal Cerrado

Portal de noticias automatizado com backend FastAPI, fila Celery, banco PostgreSQL e frontend Next.js.

## Status Atual
- Backend real em operacao.
- Frontend real em operacao e dependente da API.
- O runtime principal nao usa mais JSON local como fonte de noticias.
- O plano de acao e a memoria canônica estao separados neste mesmo diretorio.

## Stack
- FastAPI
- Celery + Redis
- PostgreSQL
- Next.js + Tailwind
- Scraping, classificacao, reescrita e publicacao por pipeline

## Documentos Principais
- `PLANO_ACAO.md` - plano unico e travado por escopo.
- `PLANO_ML.md` - arquitetura e roteiro do modulo de machine learning.
- `PLANO_ML_ACAO.md` - plano de acao do modulo de machine learning por fases.
- `CRONOGRAMA_ML_EXECUTIVO.md` - cronograma executivo do modulo de machine learning.
- `REFERENCIA_ML_NOTICIAS_CURTAS_PTB.md` - leitura comparativa de um projeto externo de classificacao de noticias.
- `MEMORIA.md` - fatos canonicos do projeto.
- `OPERACAO.md` - status operacional consolidado.
- `SPEC.md` - especificacao tecnica resumida.

## Regra
- Este repositorio deve tratar os documentos em `documento/` como fonte ativa.
