#!/usr/bin/env bash
# Build the MkDocs site image, push it to Harbor, and deploy it to Kubernetes.
# Usage: ./k8s/deploy.sh [tag]
# Prerequisites: docker login harbor.fullcheck.app, a working kubectl context,
# and harbor-cred in the dijitalbelge namespace.
set -euo pipefail

REGISTRY=harbor.fullcheck.app/dijitalbelge
IMAGE="$REGISTRY/dijitalbelge-docs"
TAG="${1:-$(date +%Y%m%d-%H%M)}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
K8S="$ROOT/k8s"

printf '==> Building %s:%s\n' "$IMAGE" "$TAG"
docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" "$ROOT"

printf "==> Pushing images to Harbor\n"
docker push "$IMAGE:$TAG"
docker push "$IMAGE:latest"

printf '==> Applying Kubernetes manifests\n'
sed -i "s|newTag:.*|newTag: $TAG|" "$K8S/kustomization.yaml"
kubectl apply -k "$K8S"
kubectl -n dijitalbelge rollout status deployment/dijitalbelge-docs --timeout=5m

printf '==> Deployed: https://dokuman.dijitalbelge.com\n'