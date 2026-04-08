# 📋 Atlas + Istio Setup - Final Checklist

## ✅ Configuration Complete

All files have been updated to expose Atlas via Istio Service Mesh on port 23000.

---

## 📁 File Status

### Core YAML Files (Ready)

| File | Type | Status | Details |
|------|------|--------|---------|
| `atlas-claim0-persistentvolumeclaim.yaml` | PVC | ✅ Ready | Storage for data |
| `atlas-claim1-persistentvolumeclaim.yaml` | PVC | ✅ Ready | Storage for logs |
| `atlas-service.yaml` | Service | ✅ Updated | ClusterIP (internal only) |
| `atlas-deployment.yaml` | Deployment | ✅ Ready | Sidecar injection enabled |
| `kustomization.yaml` | Kustomize | ✅ Ready | Alternative deployment |

### Istio-Specific (Ready)

| File | Type | Status | Details |
|------|------|--------|---------|
| `istio/atlas-istio-ingress.yaml` | Istio Resources | ✅ Ready | Gateway + VirtualService + LoadBalancer |
| `istio/README.md` | Documentation | ✅ Updated | Quick Istio reference |

### Deployment & Documentation (Updated)

| File | Type | Status | Details |
|------|------|--------|---------|
| `deploy.sh` | Script | ✅ Updated | Complete Istio deployment |
| `ISTIO_DEPLOYMENT.md` | Guide | ✅ Created | Full deployment guide |
| `ISTIO_SETUP_SUMMARY.md` | Reference | ✅ Created | Quick setup reference |

---

## 🚀 Deployment Steps

### Step 1: Verify Prerequisites
```bash
✅ Kubernetes cluster running
✅ kubectl configured
✅ istioctl installed
```

### Step 2: Run Deployment
```bash
cd apache-atlas
./deploy.sh
```

**What the script does:**
1. ✅ Verifies istioctl
2. ✅ Installs Istio
3. ✅ Enables sidecar injection
4. ✅ Deploys Atlas
5. ✅ Configures Gateway + VirtualService

### Step 3: Access
```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway 23000:23000
# Then: http://localhost:23000
```

---

## 📊 Current Configuration

### Service Mesh Stack
```
Istio IngressGateway
    ↓
Gateway (port 23000)
    ↓
VirtualService
    ↓
Atlas Service (ClusterIP)
    ↓
Atlas Pod + Envoy Sidecar (2/2)
```

### Port Mapping
- External: `localhost:23000`
- Istio: `port 23000 → targetPort 8080`
- Gateway: `port 23000`
- Service: `port 23000 → targetPort 21000`
- App: `port 21000`

---

## ✅ Verification Commands

```bash
# Istio running?
kubectl get pods -n istio-system | head

# Atlas with sidecar? (2/2)
kubectl get pods

# Gateway active?
kubectl get gateway

# VirtualService active?
kubectl get virtualservice

# Can connect?
curl http://localhost:23000
```

---

## 📚 Documentation Files

Read in this order:

1. **ISTIO_SETUP_SUMMARY.md** - Quick overview (2 min)
2. **ISTIO_DEPLOYMENT.md** - Full guide (10 min)
3. **istio/README.md** - Quick reference

---

## 🎯 What Changed

### atlas-service.yaml
```yaml
# BEFORE: LoadBalancer
# AFTER: ClusterIP
type: ClusterIP
```
**Why**: Istio Gateway manages external exposure

### atlas-deployment.yaml
```yaml
# ALREADY: Sidecar injection enabled
sidecar.istio.io/inject: "true"
```
**What it does**: Automatically injects Envoy proxy

### deploy.sh
```bash
# BEFORE: Optional Istio
# AFTER: Required Istio
# Deploys full mesh + routing
```
**What it does**: One-command deployment with Istio

---

## 🔄 Architecture Summary

```
External Client
    ↓
http://localhost:23000
    ↓
Kubectl Port-Forward
    ↓
Istio IngressGateway Service (LoadBalancer)
    ↓
Istio IngressGateway Pod (Envoy on :8080)
    ↓
Gateway (:23000)
    ↓
VirtualService (routes to atlas)
    ↓
Atlas Service (ClusterIP :23000→:21000)
    ↓
Atlas Pod (2 containers)
├─ atlas-server (:21000)
└─ istio-proxy (Envoy sidecar)
    ↓
Apache Atlas Application
```

---

## ✨ Benefits

✅ **Service Mesh Networking** - Automatic load balancing
✅ **Traffic Management** - Gateway + routing
✅ **Observability** - Built-in monitoring
✅ **Security** - Mutual TLS capable
✅ **Resilience** - Circuit breaking, retries
✅ **Simplified Ops** - Declarative configuration

---

## ⚡ Quick Commands

### Deploy
```bash
cd apache-atlas && ./deploy.sh
```

### Port Forward
```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway 23000:23000
```

### Access
```
http://localhost:23000
```

### Monitor
```bash
kubectl get gateway,virtualservice,pods
kubectl logs <pod> -c istio-proxy  # Sidecar logs
```

---

## 🎓 Key Concepts

| Concept | Purpose |
|---------|---------|
| **Gateway** | Defines how traffic enters cluster (port 23000) |
| **VirtualService** | Defines routing rules for traffic |
| **Sidecar Proxy** | Envoy proxy for mesh communication |
| **IngressGateway** | Entry point for external traffic |
| **Service Mesh** | Network of services + sidecars |

---

## ❓ FAQ

**Q: Do I need Istio?**
A: Yes, it's required in the current setup. The deploy script checks for `istioctl`.

**Q: Why ClusterIP instead of LoadBalancer?**
A: Istio Gateway handles external exposure. ClusterIP is internal-only and cleaner.

**Q: What's the sidecar proxy?**
A: Envoy proxy that handles mesh networking, monitoring, and traffic management.

**Q: Can I access Atlas without port-forward?**
A: On cloud platforms with LoadBalancer, yes. On Minikube, use port-forward.

**Q: How do I verify it's working?**
A: Run: `curl http://localhost:23000` → should get HTTP 401 (expected).

---

## 📞 Troubleshooting

### Pod shows 1/1 instead of 2/2?
```bash
# Sidecar wasn't injected. Check namespace label:
kubectl get ns default --show-labels
# Should include: istio-injection=enabled

# If missing, restart pod after labeling
```

### Can't connect to port 23000?
```bash
# Port forward not running
kubectl port-forward -n istio-system svc/istio-ingressgateway 23000:23000
```

### istioctl not found?
```bash
# Install Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*/bin && export PATH=$PATH:$(pwd)
```

---

## 📦 Deliverables

✅ **Updated YAML files** - Ready for deployment
✅ **Automated deploy script** - One-command setup
✅ **Complete documentation** - Guides + references
✅ **Istio configuration** - Gateway + VirtualService
✅ **Sidecar injection** - Automatic Envoy proxies

---

## 🎉 Status

**✅ COMPLETE**

Atlas is configured to be exposed via Istio Service Mesh on port 23000.

All files are ready. Run: `./deploy.sh`

---

**Location**: `/Users/vishal/IdeaProjects/scb-data-product/apache-atlas/`

**Last Updated**: March 31, 2026

**Status**: ✅ Production Ready

