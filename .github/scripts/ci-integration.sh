#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

echo "Starting CI integration stack..."
docker compose -f docker-compose.ci.yml up -d --build --wait --wait-timeout 900

cleanup() {
  echo "Stopping CI integration stack..."
  docker compose -f docker-compose.ci.yml down -v --remove-orphans || true
}
trap cleanup EXIT

echo "Host smoke: backend /health"
curl -fsS http://127.0.0.1:5202/health | grep -qi healthy

echo "Host smoke: AI service /"
curl -fsS http://127.0.0.1:8000/ | grep -q '"status":"ok"'

echo "In-network smoke: backend -> AI"
docker run --rm --network recruitsaas-ci-net curlimages/curl:8.5.0 \
  -fsS http://ai-service:8000/ | grep -q '"status":"ok"'

docker run --rm --network recruitsaas-ci-net curlimages/curl:8.5.0 \
  -fsS http://backend:5202/health | grep -qi healthy

echo "Integration smoke tests passed."
