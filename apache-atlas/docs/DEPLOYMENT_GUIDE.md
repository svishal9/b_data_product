# Atlas + Istio Deployment Guide

This directory contains Kubernetes manifests for deploying Apache Atlas with Istio service mesh integration.

## Prerequisites

- Kubernetes cluster (tested on Minikube)
- `kubectl` configured to access your cluster
- `istioctl` installed (for Istio deployment)

### Install istioctl

```bash
# Download and install Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*/bin
export PATH=$PATH:$(pwd)

# Verify installation
istioctl version
```

## Deployment Methods

### Option 1: Automated Deployment (Recommended)

Run the automated deployment script that handles all setup steps:

```bash
./deploy.sh
```

This script will:
1. Verify `istioctl` is installed
2. Create the `istio-system` namespace
3. Install Istio with the demo profile
4. Enable sidecar injection on the default namespace
5. Deploy all Atlas resources in the correct order
6. Wait for services to be ready

### Option 2: Manual Deployment

If you prefer to deploy manually, follow these steps:

#### Step 1: Install Istio

```bash
istioctl install --set profile=demo -y
```

#### Step 2: Create and label namespace

```bash
kubectl create namespace istio-system 2>/dev/null || true
kubectl label namespace default istio-injection=enabled --overwrite
```

#### Step 3: Deploy Atlas resources (in this order)

```bash
# Deploy persistent volumes first
kubectl apply -f atlas-claim0-persistentvolumeclaim.yaml
kubectl apply -f atlas-claim1-persistentvolumeclaim.yaml

# Deploy Atlas service and deployment
kubectl apply -f atlas-service.yaml
kubectl apply -f atlas-deployment.yaml

# Finally, deploy Istio routing rules
kubectl apply -f atlas-istio-ingress.yaml
```

#### Step 4: Using Kustomize (Alternative)

```bash
# Deploy base resources
kubectl apply -k .

# Then deploy Istio resources separately
kubectl apply -f atlas-istio-ingress.yaml
```

## Access Atlas

### Using Port Forwarding (Easy)

```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000
```

Then access Atlas at: **http://localhost:23000**

### Using Minikube Service

```bash
minikube service istio-ingressgateway-atlas -n istio-system
```

## File Descriptions

### Core Resources

- **atlas-claim0-persistentvolumeclaim.yaml**: PVC for Atlas data
- **atlas-claim1-persistentvolumeclaim.yaml**: PVC for Atlas logs
- **atlas-service.yaml**: ClusterIP service for Atlas (port 23000 → 21000)
- **atlas-deployment.yaml**: Atlas application deployment with sidecar injection

### Istio Resources

- **atlas-istio-ingress.yaml**: Contains:
  - Gateway: Configures Istio ingress gateway to listen on port 23000
  - VirtualService: Routes traffic from gateway to Atlas service
  - Service: Exposes port 23000 on the IngressGateway (LoadBalancer)

### Deployment Automation

- **deploy.sh**: Automated deployment script
- **kustomization.yaml**: Kustomize configuration for ordered resource deployment

## Verification

### Check Istio Installation

```bash
kubectl get pods -n istio-system
```

Expected output should show `istiod`, `istio-ingressgateway`, and `istio-egressgateway` pods running.

### Check Atlas Deployment

```bash
kubectl get pods -n default
```

Should show 1 pod running with 2/2 containers (atlas-server + istio-proxy sidecar).

### Verify Sidecar Injection

```bash
kubectl get pod <atlas-pod-name> -o jsonpath='{.spec.containers[*].name}'
```

Should output: `atlas-server istio-proxy`

### Check Gateway and VirtualService

```bash
kubectl get gateway
kubectl get virtualservice
kubectl get svc -n istio-system | grep istio-ingressgateway-atlas
```

### Test Connectivity

```bash
# With port forwarding running:
curl http://localhost:23000

# Should return 401 Unauthorized (expected for root path without auth)
```

## Troubleshooting

### CRDs Not Found

**Error**: "no matches for kind Gateway"

**Solution**: Ensure Istio is installed by running `istioctl install --set profile=demo -y`

### Namespace Not Found

**Error**: "namespaces istio-system not found"

**Solution**: Create the namespace with `kubectl create namespace istio-system`

### Pod Not Getting Sidecar

**Issue**: Pod shows 1/1 instead of 2/2 containers

**Solution**: 
1. Ensure namespace has `istio-injection=enabled` label
2. Delete the pod so it's recreated: `kubectl delete pod <pod-name>`

### Can't Access Atlas

**Issue**: Connection refused on localhost:23000

**Solution**: Ensure port-forwarding is running:
```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000
```

## Architecture

```
External Request (localhost:23000)
    ↓
Port Forward
    ↓
istio-ingressgateway-atlas Service (istio-system)
    ↓
Istio IngressGateway Pod (port 8080)
    ↓
Gateway Route Rule (port 23000)
    ↓
VirtualService Route Rule
    ↓
Atlas Service (default namespace, port 23000)
    ↓
Atlas Pod + Envoy Sidecar (port 21000 internal)
    ↓
Apache Atlas Application
```

## Port Mapping Summary

| Endpoint | Service | Port | Container | Target |
|----------|---------|------|-----------|--------|
| localhost:23000 | istio-ingressgateway-atlas | 23000 | N/A (LoadBalancer) | IngressGateway:8080 |
| Cluster:23000 | atlas | 23000 | atlas-server | 21000 (Atlas) |
| Pod | atlas-server | 21000 | N/A | Atlas application |

## Notes

- The `atlas-deployment.yaml` has the annotation `sidecar.istio.io/inject: "true"` which enables automatic sidecar injection
- Communication to Atlas is HTTP (not HTTPS) on port 23000 in the current setup
- Istio demo profile includes ingress and egress gateways suitable for development
- For production, consider using the `production` or `minimal` Istio profile

## Next Steps

1. Access the Atlas UI at http://localhost:23000
2. Log in with default credentials
3. Verify metadata ingestion is working
4. Monitor sidecar logs: `kubectl logs <pod-name> -c istio-proxy`

