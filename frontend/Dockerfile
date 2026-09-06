# Frontend — Portal Cerrado (Next.js)
FROM node:20-alpine AS base

WORKDIR /app
ARG NEXT_PUBLIC_API_URL=http://portal_cerrado:8000
ARG NEXT_PUBLIC_SITE_URL=http://100.95.111.24:3000
ENV NODE_ENV=production
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NEXT_PUBLIC_SITE_URL=${NEXT_PUBLIC_SITE_URL}

COPY package.json package-lock.json* ./
RUN npm ci

COPY . .
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
