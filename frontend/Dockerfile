# Build the Vite app, then serve the static bundle via nginx (which also reverse-proxies the
# backend API so the SPA stays same-origin — no CORS).
FROM node:20-alpine AS build
WORKDIR /app
# Production default: asset + fetch URLs live under /qualsched/. Host nginx strips
# that prefix; this container still serves at /. Local compose overrides VITE_BASE=/.
ARG VITE_BASE=/qualsched/
ENV VITE_BASE=$VITE_BASE
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
COPY 30-set-resolver.sh /docker-entrypoint.d/30-set-resolver.sh
RUN chmod +x /docker-entrypoint.d/30-set-resolver.sh
EXPOSE 80
