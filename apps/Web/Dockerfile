# Build React/Vite app, then serve with nginx + API reverse proxy
FROM node:22-bookworm-slim AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY index.html vite.config.js ./
COPY src ./src

ARG VITE_API_URL=same
ARG VITE_API_KEY=
ARG VITE_REQUIRE_LOGIN=true

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_KEY=$VITE_API_KEY
ENV VITE_REQUIRE_LOGIN=$VITE_REQUIRE_LOGIN

RUN npm run build

FROM nginx:1.27-alpine AS runner

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
