#!/bin/bash
set -e

MODE="build-push"
if [ "${1:-}" = "--build-only" ]; then
    MODE="build-only"
elif [ "${1:-}" = "--build-push" ]; then
    MODE="build-push"
elif [ -n "${1:-}" ]; then
    echo "❌ Unknown argument: $1"
    echo "Usage: $0 [--build-only|--build-push]"
    exit 1
fi

IMAGE_NAME="${IMAGE_NAME:-scb-frontend}"
BACKEND_IMAGE_NAME="${BACKEND_IMAGE_NAME:-scb-catalog-api}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

if [ "$MODE" = "build-only" ]; then
    FRONTEND_IMAGE="$IMAGE_NAME:$IMAGE_TAG"
    BACKEND_IMAGE="$BACKEND_IMAGE_NAME:$IMAGE_TAG"
else
    REGISTRY="${REGISTRY:-docker.io}"
    FRONTEND_IMAGE="$REGISTRY/$IMAGE_NAME:$IMAGE_TAG"
    BACKEND_IMAGE="$REGISTRY/$BACKEND_IMAGE_NAME:$IMAGE_TAG"
fi

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

docker build \
    -f docker-k8s/frontend/Dockerfile \
    -t "$FRONTEND_IMAGE" \
    .

docker build \
    -f docker-k8s/python/Dockerfile \
    -t "$BACKEND_IMAGE" \
    .

if [ "$MODE" = "build-only" ]; then
    echo "✓ Frontend image built: $FRONTEND_IMAGE"
    echo "✓ Backend image built: $BACKEND_IMAGE"
    echo "ℹ️  Build-only mode: skipping push and manifest updates"
    exit 0
fi

echo "Pushing image to registry..."
docker push "$FRONTEND_IMAGE"

echo "Pushing catalog API image to registry..."
docker push "$BACKEND_IMAGE"

echo "✓ Image pushed: $FRONTEND_IMAGE"
echo "✓ Backend image pushed: $BACKEND_IMAGE"
echo ""

# Update deployment images in a way that works on both macOS and Linux.
# Replaces any existing image reference (fresh or previously updated) with the new one.
python - "$FRONTEND_IMAGE" "$BACKEND_IMAGE" <<'PY'
import re
from pathlib import Path
import sys

frontend_image, backend_image = sys.argv[1], sys.argv[2]

frontend_manifest = Path("docker-k8s/yaml/frontend-deployment.yaml")
backend_manifest = Path("docker-k8s/yaml/catalog-api-deployment.yaml")

# Match "image: <anything>" lines and replace the image value.
def replace_image(text, new_image):
    return re.sub(
        r'(image:\s*)\S+',
        rf'\g<1>{new_image}',
        text,
    )

frontend_manifest.write_text(replace_image(frontend_manifest.read_text(), frontend_image))
backend_manifest.write_text(replace_image(backend_manifest.read_text(), backend_image))
PY


