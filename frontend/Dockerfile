# Build the Vite app, then serve the static bundle via nginx (which also reverse-proxies the
# backend API so the SPA stays same-origin — no CORS).
FROM node:20-alpine AS build
WORKDIR /app
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
