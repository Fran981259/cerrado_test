# Frontend — Portal Cerrado (Next.js)
FROM node:20-alpine AS base

WORKDIR /app
ARG NEXT_PUBLIC_API_URL=http://portal_cerrado:8000
ARG NEXT_PUBLIC_SITE_URL=https://www.portalcerrado.com.br
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_SITE_URL=${NEXT_PUBLIC_SITE_URL}

COPY package.json package-lock.json* ./
RUN npm ci --include=dev

COPY . .
RUN npm run build
RUN npm prune --omit=dev

# Configuração de non-root user
RUN chown -R node:node /app
USER node

EXPOSE 3000

CMD ["npm", "start"]
