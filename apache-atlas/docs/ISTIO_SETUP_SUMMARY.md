# ✅ Atlas + Istio Service Mesh - Setup Complete

## Overview

**Atlas is now configured to be exposed via Istio Gateway on port 23000.**

The deployment uses:
- ✅ **Istio Gateway** - Listens on port 23000 (HTTP)
- ✅ **VirtualService** - Routes traffic to Atlas ClusterIP service
- ✅ **Envoy Sidecar** - Auto-injected into Atlas pod for mesh networking
- ✅ **LoadBalancer Service** - Exposes Istio IngressGateway externally

---

## Configuration Summary

### Atlas Service
```yaml
type: ClusterIP
ports:
  - port: 23000
    targetPort: 21000
```
**Internal only** — Istio Gateway handles external exposure

### Sidecar Injection
```yaml
sidecar.istio.io/inject: "true"
```
**Enabled** — Envoy proxy automatically injected into Atlas pod

### Istio Gateway
```yaml
selector:
  istio: ingressgateway
servers:
  - port:
      number: 23000
      protocol: HTTP
```
**Listens on port 23000** for incoming traffic

### VirtualService
```yaml
destination:
  host: atlas.default.svc.cluster.local
  port:
    number: 23000
```
**Routes** incoming traffic to Atlas service

---

## Deploy in 2 Steps

### Step 1: Install Istio
```bash
istioctl install --set profile=demo -y
```

### Step 2: Run Deploy Script
```bash
cd apache-atlas
./deploy.sh
```

The script automates:
1. ✅ Istio installation verification
2. ✅ Istio namespace setup
3. ✅ Sidecar injection enable
4. ✅ Atlas deployment
5. ✅ Istio Gateway configuration

---

## Access Atlas

### Port Forward
```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway 23000:23000
```

### Access
```
http://localhost:23000
```

---

## Verify Setup

```bash
# 1. Check Gateway is active
kubectl get gateway
# Expected: atlas-gateway

# 2. Check VirtualService
kubectl get virtualservice  
# Expected: atlas-virtualservice

# 3. Check Pod has sidecar (2/2)
kubectl get pods
# Expected: atlas pod with 2/2 Running (app + sidecar)

# 4. Test connection
curl http://localhost:23000
# Expected: HTTP 401 (auth required)
```

---

## Traffic Flow

```
Browser (http://localhost:23000)
    ↓
Port Forward
    ↓
Istio IngressGateway (port 8080)
    ↓
Gateway (port 23000)
    ↓
VirtualService (routes to atlas)
    ↓
Atlas Service ClusterIP (port 23000)
    ↓
Atlas Pod (port 21000)
    ├─ atlas-server container
    └─ istio-proxy sidecar (Envoy)
```

---

## Files

| File | Purpose | Status |
|------|---------|--------|
| `atlas-service.yaml` | ClusterIP (internal) | ✅ Updated |
| `atlas-deployment.yaml` | Sidecar injection enabled | ✅ Ready |
| `deploy.sh` | One-command deployment | ✅ Updated |
| `istio/atlas-istio-ingress.yaml` | Gateway + VirtualService | ✅ Ready |
| `ISTIO_DEPLOYMENT.md` | Complete guide | ✅ Created |

---

## Troubleshooting

### Can't connect to port 23000?
```bash
# Start port-forward
kubectl port-forward -n istio-system svc/istio-ingressgateway 23000:23000
```

### Pod shows 1/1 instead of 2/2?
```bash
# Verify sidecar injection is enabled
kubectl get ns default --show-labels

# If missing istio-injection label, add it
kubectl label namespace default istio-injection=enabled --overwrite

# Restart pod
kubectl delete pod <atlas-pod>
```

### Gateway not working?
```bash
# Check Gateway status
kubectl get gateway -o yaml

# Check VirtualService routing
kubectl get vs -o yaml
```

---

## Ready to Deploy?

```bash
cd apache-atlas && ./deploy.sh
```

Then access: **http://localhost:23000**

---

**Status**: ✅ Complete - Atlas exposed via Istio Gateway on port 23000

