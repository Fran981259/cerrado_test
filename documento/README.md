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
- `MEMORIA.md` - fatos canonicos do projeto.
- `OPERACAO.md` - status operacional consolidado.
- `SPEC.md` - especificacao tecnica resumida.

## Regra
- Este repositorio deve tratar os documentos em `documento/` como fonte ativa.
