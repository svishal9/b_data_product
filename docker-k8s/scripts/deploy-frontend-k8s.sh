#!/bin/bash
set -e

echo "================================"
echo "SCB Frontend + Catalog API - Kubernetes Deployment"
echo "================================"
echo ""

# Check kubectl connection
if ! kubectl cluster-info >/dev/null 2>&1; then
    echo "❌ Cannot connect to Kubernetes cluster"
    echo "Configure kubectl with: kubectl config use-context <context-name>"
    exit 1
fi

CLUSTER_NAME=$(kubectl config current-context)
echo "✓ Connected to cluster: $CLUSTER_NAME"
echo ""

# Optional: Build and push to registry
if [ "$1" = "--build" ]; then
    echo "Building and pushing frontend and catalog API images..."
    BUILD_SCRIPT="docker-k8s/scripts/build-push-images.sh"
    if [ ! -f "$BUILD_SCRIPT" ]; then
        echo "❌ Build script not found: $BUILD_SCRIPT"
        exit 1
    fi
    # Default pushes to Docker Hub namespace svishal9 for Kubernetes deployments.
    : "${REGISTRY:=docker.io}"
    : "${IMAGE_NAME:=svishal9/frontend}"
    : "${BACKEND_IMAGE_NAME:=svishal9/catalog-api}"
    bash "$BUILD_SCRIPT" --build-push
else
    echo "Skipping image build. Use --build flag to build and push image."
    echo "Image names in deployment yamls: scb-frontend:latest, scb-catalog-api:latest"
    echo ""
fi

# Create namespace
echo "Creating namespace..."
kubectl create namespace scb-frontend --dry-run=client -o yaml | kubectl apply -f -

# Label namespace for Istio injection (if available)
kubectl label namespace scb-frontend istio-injection=enabled istio.io=default --overwrite 2>/dev/null || true

echo "✓ Namespace created and labeled"
echo ""

# Deploy
echo "Deploying frontend and catalog API..."
kubectl apply -f docker-k8s/yaml/frontend-deployment.yaml
kubectl apply -f docker-k8s/yaml/catalog-api-deployment.yaml

# Wait for deployment
echo "Waiting for frontend deployment to be ready..."
kubectl rollout status deployment/scb-frontend -n scb-frontend --timeout=600s

echo "Waiting for catalog API deployment to be ready..."
kubectl rollout status deployment/catalog-api -n scb-frontend --timeout=600s

echo "✓ Deployment ready"
echo ""

# Try to deploy Istio resources
echo "Attempting to deploy Istio resources..."
if kubectl api-resources | grep -q gateway.networking.istio.io; then
    kubectl apply -f docker-k8s/yaml/frontend-istio.yaml
    echo "✓ Istio resources deployed"
else
    echo "⚠️  Istio not available, skipping Gateway/VirtualService"
fi
echo ""

# Try to deploy APIRule for Kyma
if kubectl api-resources | grep -q apirule.gateway.kyma-project.io; then
    kubectl apply -f docker-k8s/yaml/frontend-apirule.yaml
    echo "✓ Kyma APIRule deployed"
    echo ""
fi

# Show deployment info
echo "================================"
echo "Frontend + Catalog API Deployment Complete!"
echo "================================"
echo ""

echo "Deployment Status:"
kubectl get deployment scb-frontend -n scb-frontend
kubectl get deployment catalog-api -n scb-frontend
echo ""

echo "Pod Status:"
kubectl get pods -n scb-frontend
echo ""

echo "Service:"
kubectl get svc -n scb-frontend
echo ""

# Show how to access
echo "Access Frontend:"
echo "  Cluster IP (internal): http://scb-frontend.scb-frontend.svc.cluster.local"
echo "  Catalog API (internal): http://catalog-api.scb-frontend.svc.cluster.local:8000/api/catalog/health"
echo ""

if kubectl get gateway scb-frontend-gateway -n scb-frontend >/dev/null 2>&1; then
    echo "  Via Istio Gateway: Check ingress gateway external IP"
    echo "    kubectl get svc -n istio-system istio-ingressgateway"
    echo ""
fi

if kubectl api-resources | grep -q apirule.gateway.kyma-project.io; then
    echo "  Via Kyma APIRule:"
    echo "    https://scb-frontend.<cluster-domain>"
    echo ""
fi

echo "Useful Commands:"
echo "  View logs:        kubectl logs -n scb-frontend -f deployment/scb-frontend"
echo "  View API logs:    kubectl logs -n scb-frontend -f deployment/catalog-api"
echo "  Port forward:     kubectl port-forward -n scb-frontend svc/scb-frontend 3000:80"
echo "  Scale replicas:   kubectl scale deployment scb-frontend -n scb-frontend --replicas=3"
echo "  Delete:           kubectl delete namespace scb-frontend"
echo ""

