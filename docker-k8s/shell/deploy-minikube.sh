#!/bin/bash
# Deploy script for SCB Ingestion on Minikube
# This script handles building the Docker image and deploying to minikube

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$BASE_DIR")"
YAML_DIR="$BASE_DIR/yaml"
IMAGE_NAME="scb-ingestion"
IMAGE_TAG="latest"
NAMESPACE="scb-ingestion"
SETUP_ONLY=false
BUILD_DIR=""

cleanup_build_dir() {
    if [ -n "$BUILD_DIR" ] && [ -d "$BUILD_DIR" ]; then
        rm -rf "$BUILD_DIR"
    fi
}

trap cleanup_build_dir EXIT

if [ "$1" = "--setup-only" ]; then
    SETUP_ONLY=true
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}SCB Data Product Ingestion - Minikube Deployment${NC}"

check_atlas_secret_placeholders() {
    local setup_file="$YAML_DIR/k8s-setup.yaml"
    local encoded_placeholder

    # Fail fast if setup manifest still contains placeholder credentials.
    if grep -q 'ATLAS_USERNAME: "REPLACE_ME"' "$setup_file" || grep -q 'ATLAS_PASSWORD: "REPLACE_ME"' "$setup_file"; then
        echo -e "${RED}✗ Placeholder Atlas credentials found in k8s-setup.yaml${NC}"
        echo "  Update Secret/scb-atlas-credentials values before deploying."
        exit 1
    fi

    encoded_placeholder=$(printf 'REPLACE_ME' | base64)

    # If Secret already exists in cluster, block deploy when placeholder values are still set.
    if kubectl get secret scb-atlas-credentials -n "$NAMESPACE" &> /dev/null; then
        local current_user
        local current_pass
        current_user=$(kubectl get secret scb-atlas-credentials -n "$NAMESPACE" -o jsonpath='{.data.ATLAS_USERNAME}' 2>/dev/null || true)
        current_pass=$(kubectl get secret scb-atlas-credentials -n "$NAMESPACE" -o jsonpath='{.data.ATLAS_PASSWORD}' 2>/dev/null || true)

        if [ "$current_user" = "$encoded_placeholder" ] || [ "$current_pass" = "$encoded_placeholder" ]; then
            echo -e "${RED}✗ Secret/scb-atlas-credentials still contains placeholder values in cluster${NC}"
            echo "  Rotate credentials before deploying."
            exit 1
        fi
    fi
}

# Check if minikube is running
if ! minikube status &> /dev/null; then
    echo -e "${RED}Minikube is not running. Please start it with: minikube start${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Minikube is running${NC}"

echo -e "${YELLOW}Running secret safety checks...${NC}"
check_atlas_secret_placeholders
echo -e "${GREEN}✓ Atlas credential checks passed${NC}"

# Configure Docker to use minikube's Docker daemon
echo -e "${YELLOW}Configuring Docker to use minikube...${NC}"
eval $(minikube docker-env)

# Build isolated Docker context to avoid creating duplicate source files in repo.
echo -e "${YELLOW}Preparing temporary Docker build context...${NC}"
BUILD_DIR=$(mktemp -d)
mkdir -p "$BUILD_DIR/python"
cp "$BASE_DIR/Dockerfile" "$BUILD_DIR/"
cp "$PROJECT_ROOT/pyproject.toml" "$BUILD_DIR/"
cp "$PROJECT_ROOT/uv.lock" "$BUILD_DIR/"
cp "$PROJECT_ROOT/scb_dp_cli.py" "$BUILD_DIR/python/"
cp "$PROJECT_ROOT/scb_types.py" "$BUILD_DIR/python/"
cp "$PROJECT_ROOT/scb_enums.py" "$BUILD_DIR/python/"
cp "$PROJECT_ROOT/recreate_data_products_from_workbook.py" "$BUILD_DIR/python/"
cp "$PROJECT_ROOT/create_entities_with_pydantic.py" "$BUILD_DIR/python/"
cp "$PROJECT_ROOT/ingest_workbook_to_atlas.py" "$BUILD_DIR/python/"
cp "$PROJECT_ROOT/clean_up_atlas.py" "$BUILD_DIR/python/"
cp -r "$PROJECT_ROOT/scb_atlas" "$BUILD_DIR/python/"

echo -e "${GREEN}✓ Project files copied${NC}"

# Build Docker image
echo -e "${YELLOW}Building Docker image: $IMAGE_NAME:$IMAGE_TAG${NC}"
docker build -t "$IMAGE_NAME:$IMAGE_TAG" -f "$BUILD_DIR/Dockerfile" "$BUILD_DIR"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
else
    echo -e "${RED}✗ Failed to build Docker image${NC}"
    exit 1
fi

# Create namespace and resources
echo -e "${YELLOW}Creating Kubernetes namespace and resources...${NC}"
kubectl apply -f "$YAML_DIR/k8s-setup.yaml"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Kubernetes setup resources created${NC}"
else
    echo -e "${RED}✗ Failed to create Kubernetes resources${NC}"
    exit 1
fi

if [ "$SETUP_ONLY" = false ]; then
    echo -e "${YELLOW}Deploying ingestion job...${NC}"
    kubectl apply -f "$YAML_DIR/k8s-job.yaml"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Ingestion job created${NC}"
    else
        echo -e "${RED}✗ Failed to create ingestion job${NC}"
        exit 1
    fi
fi

# Display deployment status
echo -e "${YELLOW}Deployment Summary:${NC}"
echo -e "  Namespace: ${GREEN}$NAMESPACE${NC}"
echo -e "  Image: ${GREEN}$IMAGE_NAME:$IMAGE_TAG${NC}"
if [ "$SETUP_ONLY" = true ]; then
    echo -e "  Status: ${GREEN}Setup complete (no workload created)${NC}"
else
    echo -e "  Status: ${GREEN}Job deployed${NC}"
fi

echo ""
echo -e "${YELLOW}Next steps:${NC}"
if [ "$SETUP_ONLY" = true ]; then
    echo "  1. Deploy the ingestion job:"
    echo "     kubectl apply -f $YAML_DIR/k8s-job.yaml"
    echo ""
    echo "  2. Monitor the job:"
    echo "     kubectl logs -n $NAMESPACE -f job/scb-ingest-job"
    echo ""
    echo "  3. Check job status:"
    echo "     kubectl describe job scb-ingest-job -n $NAMESPACE"
else
    echo "  1. Monitor the job:"
    echo "     kubectl logs -n $NAMESPACE -f job/scb-ingest-job"
    echo ""
    echo "  2. Check job status:"
    echo "     kubectl describe job scb-ingest-job -n $NAMESPACE"
fi

