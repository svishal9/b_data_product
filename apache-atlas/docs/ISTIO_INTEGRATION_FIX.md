# Atlas Istio Integration - Issue Resolution

## Problem Summary

When running `kubectl apply -f .` on a fresh cluster, the deployment failed with these errors:

```
resource mapping not found for name: "atlas-gateway" namespace: "default" 
  no matches for kind "Gateway" in version "networking.istio.io/v1beta1"
ensure CRDs are installed first

resource mapping not found for name: "atlas-virtualservice" namespace: "default"
  no matches for kind "VirtualService" in version "networking.istio.io/v1beta1"
ensure CRDs are installed first

Error from server (NotFound): error when creating "atlas-istio-ingress.yaml": 
  namespaces "istio-system" not found
```

## Root Causes

1. **Istio CRDs Not Installed**: The Kubernetes Custom Resource Definitions (CRDs) for Istio Gateway and VirtualService don't exist until Istio is properly installed.

2. **Missing istio-system Namespace**: Istio components require a dedicated namespace that wasn't created.

3. **Sidecar Injection Not Enabled**: The default namespace lacked the label to enable automatic Envoy sidecar injection.

## Solution

The issue requires a **sequential deployment approach** that cannot be solved by simply running `kubectl apply -f .`:

### Step 1: Install Istio First (Installs CRDs)
```bash
istioctl install --set profile=demo -y
```

### Step 2: Create istio-system Namespace
```bash
kubectl create namespace istio-system
```

### Step 3: Enable Sidecar Injection
```bash
kubectl label namespace default istio-injection=enabled --overwrite
```

### Step 4: Deploy Atlas Resources
```bash
kubectl apply -f atlas-claim0-persistentvolumeclaim.yaml
kubectl apply -f atlas-claim1-persistentvolumeclaim.yaml
kubectl apply -f atlas-service.yaml
kubectl apply -f atlas-deployment.yaml
kubectl apply -f atlas-istio-ingress.yaml
```

## Files Created

### 1. `deploy.sh` (Automated Deployment)
A bash script that automates all the setup steps in the correct order:
- Verifies istioctl installation
- Creates and sets up namespaces
- Installs Istio
- Deploys all resources
- Provides connection instructions

**Usage**: `./deploy.sh`

### 2. `kustomization.yaml`
Kustomize configuration for ordered resource deployment:
- Defines resource application order
- Automatically injects sidecar annotation into Atlas deployment
- Can be used with `kubectl apply -k .`

**Usage**: `kubectl apply -k .` (then apply Istio resources separately)

### 3. `DEPLOYMENT_GUIDE.md`
Comprehensive deployment guide with:
- Prerequisites and installation instructions
- Multiple deployment methods
- Verification steps
- Troubleshooting section
- Architecture diagram
- Port mapping reference

## YAML Changes Made

### atlas-istio-ingress.yaml

**API Version Update**:
- Changed from `v1alpha3` to `v1beta1` (current stable version)
- Ensures compatibility with latest Istio releases

**Namespace Additions**:
```yaml
gateway:
  metadata:
    name: atlas-gateway
    namespace: default
virtualService:
  metadata:
    name: atlas-virtualservice
    namespace: default
```

**Destination FQDN Update**:
```yaml
# Changed from just 'atlas' to full FQDN
destination:
  host: atlas.default.svc.cluster.local
```

**Service Configuration**:
- Exposes port 23000 on the IngressGateway (LoadBalancer service in istio-system)
- Properly selects Istio ingress gateway pods

### atlas-deployment.yaml

**Sidecar Injection Annotation Added**:
```yaml
metadata:
  annotations:
    sidecar.istio.io/inject: "true"
```

This ensures the Envoy proxy sidecar is automatically injected into each Atlas pod when deployed to a namespace with `istio-injection=enabled` label.

## Why Sequential Deployment is Required

Kubernetes resources must be deployed in dependency order:

```
1. Istio CRDs (via istioctl install)
   ↓
2. Namespaces (istio-system created)
   ↓
3. Sidecar Injection Labels (enable on default namespace)
   ↓
4. PersistentVolumeClaims (storage for Atlas)
   ↓
5. Service & Deployment (Atlas application)
   ↓
6. Istio Gateway/VirtualService (routing rules)
```

Attempting to apply these in random order or all at once will fail because resources depend on previous resources existing.

## Deployment Options Going Forward

### Option 1: Use Automated Script (Recommended)
```bash
cd apache-atlas
./deploy.sh
```
- **Pros**: One-command deployment, automatic error handling, clear progress
- **Cons**: None

### Option 2: Use Kustomize + Manual Istio
```bash
# Install Istio manually first
istioctl install --set profile=demo -y
kubectl label namespace default istio-injection=enabled --overwrite

# Then deploy via Kustomize
cd apache-atlas
kubectl apply -k .
kubectl apply -f atlas-istio-ingress.yaml
```
- **Pros**: More control, standard Kubernetes approach
- **Cons**: More steps, easier to make mistakes

### Option 3: Manual Step-by-Step (Not Recommended)
Follow all steps in DEPLOYMENT_GUIDE.md manually
- **Pros**: Educational, maximum control
- **Cons**: Error-prone, repetitive

## Verification Commands

After deployment, verify everything is working:

```bash
# Check Istio installation
kubectl get pods -n istio-system

# Check Atlas pod (should show 2/2 containers = app + sidecar)
kubectl get pods -n default

# Verify sidecar was injected
kubectl get pod <atlas-pod-name> -o jsonpath='{.spec.containers[*].name}'
# Expected output: atlas-server istio-proxy

# Check routing rules
kubectl get gateway
kubectl get virtualservice

# Test connectivity (with port-forwarding)
kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000
curl http://localhost:23000
```

## Summary

The issue was fundamentally about **dependency ordering and missing prerequisites**. The solution provides:

1. **Automated deployment script** for one-command setup
2. **Kustomize configuration** for GitOps-friendly deployment
3. **Comprehensive documentation** for manual troubleshooting
4. **Fixed YAML files** with correct API versions and namespaces

All resources are now properly configured for Istio integration with automatic sidecar injection and port 23000 exposed through the service mesh.

