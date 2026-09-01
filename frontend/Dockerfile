# Frontend — Portal Cerrado (Next.js)
FROM node:20-alpine AS base

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_SITE_URL=https://portalcerrado.com.br

CMD ["npm", "start"]
