FROM squidfunk/mkdocs-material:9
WORKDIR /docs
COPY . /docs
EXPOSE 8000
RUN mkdocs build --clean

CMD ["sh", "-c", "python3 -m http.server 8000 --directory site"]
