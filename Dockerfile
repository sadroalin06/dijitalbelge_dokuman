# 1️⃣ Build stage
FROM squidfunk/mkdocs-material:9 AS build
WORKDIR /docs
COPY . .
RUN mkdocs build --clean

# 2️⃣ Runtime stage
FROM nginx:alpine

# default nginx config'i kaldır
RUN rm /etc/nginx/conf.d/default.conf

# custom config ekle
COPY nginx.conf /etc/nginx/conf.d/default.conf

# static site kopyala
COPY --from=build /docs/site /usr/share/nginx/html
