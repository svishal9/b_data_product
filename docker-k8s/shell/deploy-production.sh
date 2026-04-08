#!/bin/bash
# Deploy script for SCB Ingestion on Production Kubernetes Cluster
# This script handles deploying to a production-like Kubernetes cluster

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BASE_DIR="$(dirname "$SCRIPT_DIR")"
YAML_DIR="$BASE_DIR/yaml"
IMAGE_NAME="${IMAGE_NAME:-scb-ingestion}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
REGISTRY="${REGISTRY:-}"
NAMESPACE="scb-ingestion"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}SCB Data Product Ingestion - Production Kubernetes Deployment${NC}"

check_atlas_secret_placeholders() {
    local setup_file="$YAML_DIR/k8s-setup.yaml"
    local encoded_placeholder

    # Fail fast if setup manifest still contains placeholder credentials.
    if grep -q 'ATLAS_USERNAME: "REPLACE_ME"' "$setup_file" || grep -q 'ATLAS_PASSWORD: "REPLACE_ME"' "$setup_file"; then
        echo -e "${RED}✗ Placeholder Atlas credentials found in k8s-setup.yaml${NC}"
        echo "  Update Secret/scb-atlas-credentials values before production deploy."
        exit 1
    fi

    encoded_placeholder=$(printf 'REPLACE_ME' | base64)

    # If Secret already exists in the cluster, block deploy when placeholder values are still set.
    if kubectl get secret scb-atlas-credentials -n "$NAMESPACE" &> /dev/null; then
        local current_user
        local current_pass
        current_user=$(kubectl get secret scb-atlas-credentials -n "$NAMESPACE" -o jsonpath='{.data.ATLAS_USERNAME}' 2>/dev/null || true)
        current_pass=$(kubectl get secret scb-atlas-credentials -n "$NAMESPACE" -o jsonpath='{.data.ATLAS_PASSWORD}' 2>/dev/null || true)

        if [ "$current_user" = "$encoded_placeholder" ] || [ "$current_pass" = "$encoded_placeholder" ]; then
            echo -e "${RED}✗ Secret/scb-atlas-credentials still contains placeholder values in cluster${NC}"
            echo "  Rotate credentials before production deploy."
            exit 1
        fi
    fi
}

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}kubectl is not installed. Please install kubectl to continue.${NC}"
    exit 1
fi

# Check cluster connectivity
echo -e "${YELLOW}Checking cluster connectivity...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Cannot connect to Kubernetes cluster.${NC}"
    exit 1
fi

CLUSTER_NAME=$(kubectl config current-context)
echo -e "${GREEN}✓ Connected to cluster: $CLUSTER_NAME${NC}"

echo -e "${YELLOW}Running secret safety checks...${NC}"
check_atlas_secret_placeholders
echo -e "${GREEN}✓ Atlas credential checks passed${NC}"

# Apply setup resources
echo -e "${YELLOW}Applying Kubernetes namespace and resources...${NC}"
kubectl apply -f "$YAML_DIR/k8s-setup.yaml"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Kubernetes setup resources applied${NC}"
else
    echo -e "${RED}✗ Failed to apply Kubernetes resources${NC}"
    exit 1
fi

# Wait for namespace to be ready
echo -e "${YELLOW}Waiting for namespace to be ready...${NC}"
kubectl wait --for=condition=active namespace/$NAMESPACE --timeout=30s 2>/dev/null || true

echo ""
echo -e "${YELLOW}Deployment Summary:${NC}"
echo -e "  Cluster: ${GREEN}$CLUSTER_NAME${NC}"
echo -e "  Namespace: ${GREEN}$NAMESPACE${NC}"
echo -e "  Image: ${GREEN}${REGISTRY}${IMAGE_NAME}:${IMAGE_TAG}${NC}"
echo -e "  Status: ${GREEN}Resources applied${NC}"

echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Push Docker image to registry:"
echo "     docker push ${REGISTRY}${IMAGE_NAME}:${IMAGE_TAG}"
echo ""
echo "  2. Update image in yaml/k8s-job.yaml if using custom registry"
echo ""
echo "  3. Deploy the ingestion job:"
echo "     kubectl apply -f $YAML_DIR/k8s-job.yaml"
echo ""
echo "  4. Monitor the job:"
echo "     kubectl logs -n $NAMESPACE -f job/scb-ingest-job"
echo ""
echo "  5. Check job status:"
echo "     kubectl describe job scb-ingest-job -n $NAMESPACE"

# Show current namespace status
echo ""
echo -e "${YELLOW}Current Namespace Resources:${NC}"
kubectl get all -n $NAMESPACE

