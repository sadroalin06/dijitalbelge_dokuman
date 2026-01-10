# 1️⃣ Build stage
FROM squidfunk/mkdocs-material:9 AS build
WORKDIR /docs
COPY . .
RUN mkdocs build --clean

# 2️⃣ Runtime stage
FROM nginx:alpine
COPY --from=build /docs/site /usr/share/nginx/html
