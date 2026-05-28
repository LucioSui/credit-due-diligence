FROM node:20-alpine AS builder
WORKDIR /app
# Context is ./nginx, so frontend is at ../frontend
COPY ../frontend/package.json ../frontend/package-lock.json* ./
RUN npm ci
COPY ../frontend .
RUN npm run build

FROM nginx:alpine
COPY default.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
