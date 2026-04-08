#!/bin/bash

# Deploy Apache Atlas with Istio routing on port 23000.
# Usage:
#   ./deploy.sh minikube
#   ./deploy.sh cluster

set -euo pipefail

TARGET="${1:-minikube}"
if [[ "$TARGET" != "minikube" && "$TARGET" != "cluster" ]]; then
  echo "Invalid target: $TARGET"
  echo "Usage: ./deploy.sh [minikube|cluster]"
  exit 1
fi

NAMESPACE="atlas-system"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================"
echo "Atlas + Istio deploy ($TARGET)"
echo "================================"

echo "[1/6] Checking istioctl..."
if ! command -v istioctl >/dev/null 2>&1; then
  echo "istioctl not found in PATH."
  echo "Install: https://istio.io/latest/docs/setup/getting-started/"
  exit 1
fi

# --- Pre-flight: ensure the target cluster is reachable ---
if [[ "$TARGET" == "minikube" ]]; then
  echo "[pre-flight] Checking minikube..."
  if ! command -v minikube >/dev/null 2>&1; then
    echo "ERROR: minikube not found in PATH."
    echo "Install: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
  fi

  MINIKUBE_STATUS="$(minikube status --format='{{.Host}}' 2>/dev/null || echo 'Stopped')"
  if [[ "$MINIKUBE_STATUS" != "Running" ]]; then
    echo "[pre-flight] minikube is not running (status: $MINIKUBE_STATUS). Starting..."
    minikube start
  else
    echo "[pre-flight] minikube is already running."
  fi
fi

echo "[pre-flight] Verifying cluster connectivity..."
if ! kubectl cluster-info >/dev/null 2>&1; then
  echo "ERROR: kubectl cannot reach the Kubernetes API server."
  if [[ "$TARGET" == "minikube" ]]; then
    echo "Try: minikube start"
  else
    echo "Check your kubeconfig: kubectl config current-context"
  fi
  exit 1
fi
echo "[pre-flight] Cluster is reachable. ✅"

echo "[2/6] Installing/ensuring Istio..."
kubectl create namespace istio-system >/dev/null 2>&1 || true
istioctl install --set profile=demo -y
kubectl rollout status deployment/istiod -n istio-system --timeout=5m
kubectl rollout status deployment/istio-ingressgateway -n istio-system --timeout=5m

echo "[3/6] Creating namespace '$NAMESPACE' and enabling sidecar injection..."
kubectl create namespace "$NAMESPACE" >/dev/null 2>&1 || true
kubectl label namespace "$NAMESPACE" \
  istio-injection=enabled \
  istio.io/rev=default \
  --overwrite

echo "[4/6] Deploying Atlas core resources..."
kubectl apply -f atlas-claim0-persistentvolumeclaim.yaml -n "$NAMESPACE"
kubectl apply -f atlas-claim1-persistentvolumeclaim.yaml -n "$NAMESPACE"
kubectl apply -f atlas-service.yaml -n "$NAMESPACE"
kubectl apply -f atlas-deployment.yaml -n "$NAMESPACE"
# Force recreate pods after injection label/annotation changes so sidecar is injected.
kubectl rollout restart deployment/atlas -n "$NAMESPACE"
kubectl rollout status deployment/atlas -n "$NAMESPACE" --timeout=5m

echo "[5/6] Applying Istio overlay for target: $TARGET"
kubectl apply -k "istio/overlays/$TARGET"

echo "[6/6] Ensuring Atlas pod includes Istio sidecar..."
ATLAS_POD="$(kubectl get pods -n "$NAMESPACE" -l io.kompose.service=atlas -o jsonpath='{.items[0].metadata.name}')"
CONTAINERS="$(kubectl get pod "$ATLAS_POD" -n "$NAMESPACE" -o jsonpath='{.spec.containers[*].name}')"
if [[ "$CONTAINERS" != *"istio-proxy"* ]]; then
  echo "ERROR: Istio sidecar not injected. Found containers: $CONTAINERS"
  echo "Check namespace label and mutating webhook health."
  exit 1
fi
echo "✅ Sidecar verified in pod $ATLAS_POD ($CONTAINERS)"

echo ""
echo "Deployment complete."
echo ""
if [[ "$TARGET" == "minikube" ]]; then
  echo "Minikube access options:"
  echo "  kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000"
  echo "  minikube service -n istio-system istio-ingressgateway-atlas"
else
  echo "Cluster access:"
  echo "  kubectl get svc -n istio-system istio-ingressgateway-atlas"
  echo "  Use EXTERNAL-IP:23000 once assigned"
fi
echo ""
