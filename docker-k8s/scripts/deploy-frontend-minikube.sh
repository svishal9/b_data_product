#!/bin/bash
set -e

echo "================================"
echo "SCB Frontend + Catalog API - Minikube Deployment"
echo "================================"
echo ""

# Check if minikube is running
if ! minikube status >/dev/null 2>&1; then
    echo "❌ Minikube is not running"
    echo "Start minikube with: minikube start"
    exit 1
fi

echo "✓ Minikube is running"
echo ""

# Get minikube docker env
eval $(minikube docker-env)
echo "✓ Using minikube Docker daemon"
echo ""

# Navigate to project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "Building frontend and catalog API Docker images..."
BUILD_SCRIPT="docker-k8s/scripts/build-push-images.sh"
if [ ! -f "$BUILD_SCRIPT" ]; then
    echo "❌ Build script not found: $BUILD_SCRIPT"
    exit 1
fi
bash "$BUILD_SCRIPT" --build-only
echo ""

# Create namespace
echo "Creating namespace..."
kubectl create namespace scb-frontend --dry-run=client -o yaml | kubectl apply -f -

# Label namespace for Istio injection
kubectl label namespace scb-frontend istio-injection=enabled istio.io=default --overwrite

echo "✓ Namespace created and labeled"
echo ""

# Deploy
echo "Deploying frontend and catalog API..."
kubectl apply -f docker-k8s/yaml/frontend-deployment.yaml
kubectl apply -f docker-k8s/yaml/catalog-api-deployment.yaml

# Wait for deployment
echo "Waiting for frontend deployment to be ready..."
kubectl rollout status deployment/scb-frontend -n scb-frontend --timeout=300s

echo "Waiting for catalog API deployment to be ready..."
kubectl rollout status deployment/catalog-api -n scb-frontend --timeout=300s

echo "✓ Deployment ready"
echo ""

# Deploy Istio Gateway and VirtualService
echo "Deploying Istio resources..."
kubectl apply -f docker-k8s/yaml/frontend-istio.yaml

echo "✓ Istio resources deployed"
echo ""

# Get frontend URL
echo "================================"
echo "Frontend + Catalog API Deployment Complete!"
echo "================================"
echo ""

MINIKUBE_IP=$(minikube ip)
echo "Minikube IP: $MINIKUBE_IP"
echo ""

# Check if Istio is installed
if kubectl get gateway scb-frontend-gateway -n scb-frontend >/dev/null 2>&1; then
    echo "🌐 Frontend is accessible via Istio:"
    echo "   http://$MINIKUBE_IP (with Istio ingress gateway)"
    echo ""
    echo "To access via Istio gateway:"
    echo "   minikube tunnel &"
    echo "   curl http://localhost"
    echo ""
else
    # Fallback to port-forward
    echo "⚠️  Istio not available, using port-forward:"
    echo "   kubectl port-forward -n scb-frontend svc/scb-frontend 3000:80"
    echo "   Then access at: http://localhost:3000"
    echo ""
fi

echo "View logs:"
echo "   kubectl logs -n scb-frontend -f deployment/scb-frontend"
echo "   kubectl logs -n scb-frontend -f deployment/catalog-api"
echo ""

echo "View pods:"
echo "   kubectl get pods -n scb-frontend"
echo ""

echo "Delete deployment:"
echo "   kubectl delete namespace scb-frontend"

