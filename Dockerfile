FROM squidfunk/mkdocs-material:9
WORKDIR /docs
COPY . /docs
EXPOSE 8000
CMD ["serve", "--dev-addr=0.0.0.0:8000"]
