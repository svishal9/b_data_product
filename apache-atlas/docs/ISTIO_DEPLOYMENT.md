# 🚀 Deploy Atlas with Istio Service Mesh

**Atlas is exposed on port 23000 via Istio Gateway + VirtualService + Envoy Sidecar**

## Prerequisites

- Kubernetes cluster (Minikube, EKS, GKE, etc.)
- `kubectl` configured to access your cluster
- `istioctl` installed ([install guide](https://istio.io/latest/docs/setup/getting-started/))

## Quick Deploy (One Command)

```bash
cd apache-atlas
./deploy.sh
```

The script will:
1. ✅ Verify `istioctl` is installed
2. ✅ Install Istio (demo profile)
3. ✅ Enable sidecar injection
4. ✅ Deploy Atlas
5. ✅ Configure Istio Gateway routing
6. ✅ Display access instructions

## Manual Deployment Steps

### Step 1: Install Istio

```bash
istioctl install --set profile=demo -y
```

Wait for Istio pods to be ready:
```bash
kubectl get pods -n istio-system -w
```

### Step 2: Enable Sidecar Injection

```bash
kubectl label namespace default istio-injection=enabled --overwrite
```

### Step 3: Deploy Atlas

```bash
kubectl apply -f apache-atlas/*.yaml
```

This deploys:
- PersistentVolumeClaims (storage)
- Atlas Service (ClusterIP - internal only)
- Atlas Deployment (with sidecar injection enabled)

Verify Atlas is running:
```bash
kubectl get pods
# Should show: atlas pod with 2/2 Running (app + sidecar)
```

### Step 4: Deploy Istio Routing

```bash
kubectl apply -f apache-atlas/istio/atlas-istio-ingress.yaml
```

This creates:
- **Gateway**: Listens on port 23000
- **VirtualService**: Routes traffic to Atlas service
- **LoadBalancer Service**: Exposes Istio IngressGateway on port 23000

Verify routing is active:
```bash
kubectl get gateway
kubectl get virtualservice
```

## Access Atlas

### Option 1: Port Forward (Recommended for Minikube)

```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway 23000:23000
```

Then access: **http://localhost:23000**

### Option 2: Minikube Service

```bash
minikube service istio-ingressgateway -n istio-system
```

### Option 3: Cloud LoadBalancer

```bash
kubectl get svc -n istio-system istio-ingressgateway
# Look for EXTERNAL-IP
# Access: http://<EXTERNAL-IP>:23000
```

## Verify Everything Works

```bash
# 1. Check Istio is running
kubectl get pods -n istio-system
# Expected: istiod, istio-ingressgateway, istio-egressgateway running

# 2. Check Atlas pod has sidecar (2/2)
kubectl get pods
# Expected: atlas pod with 2/2 Running

# 3. Check sidecar name
kubectl get pod <atlas-pod-name> -o jsonpath='{.spec.containers[*].name}'
# Expected output: atlas-server istio-proxy

# 4. Check Gateway and VirtualService
kubectl get gateway
kubectl get virtualservice

# 5. Test connection
curl -v http://localhost:23000
# Expected: HTTP/1.1 401 Unauthorized (from Atlas, indicating successful routing)
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ External Client (http://localhost:23000)                   │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
            kubectl port-forward
       (localhost:23000 → istio-ingressgateway:23000)
                     │
                     ▼
    ┌───────────────────────────────────────────────────┐
    │  Istio IngressGateway Service (istio-system)     │
    │  LoadBalancer on port 23000 → 8080               │
    └───────────────┬─────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────┐
    │  Istio IngressGateway Pod                        │
    │  (Envoy proxy listening on port 8080)            │
    └───────────────┬─────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────┐
    │  Gateway Resource                                │
    │  - Selector: istio: ingressgateway               │
    │  - Port: 23000 (HTTP)                            │
    └───────────────┬─────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────┐
    │  VirtualService                                  │
    │  - Hosts: *                                      │
    │  - Routes to: atlas.default.svc.cluster.local   │
    │  - Destination port: 23000                       │
    └───────────────┬─────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────┐
    │  Atlas Service (default namespace)               │
    │  ClusterIP on port 23000 → 21000 (internal)      │
    └───────────────┬─────────────────────────────────┘
                    │
                    ▼
    ┌───────────────────────────────────────────────────┐
    │  Atlas Pod (2/2 containers)                      │
    │  ├─ atlas-server (port 21000)                    │
    │  └─ istio-proxy (Envoy sidecar)                  │
    └───────────────┬─────────────────────────────────┘
                    │
                    ▼
           Apache Atlas Application
```

## Port Mapping Summary

| Layer | Service | Port | Target | Purpose |
|-------|---------|------|--------|---------|
| External | Port Forward | 23000 | Istio Ingress | Local access |
| K8s Service | istio-ingressgateway | 23000 | Envoy:8080 | Expose externally |
| Gateway | Gateway | 23000 | Envoy routing | Listen port |
| VirtualService | Route | 23000 | atlas:23000 | Route rule |
| Internal Service | atlas | 23000 | Pod:21000 | Internal routing |
| Pod | atlas-server | 21000 | App | Atlas app |

## Troubleshooting

### Problem: `istioctl not found`
**Solution**: Install Istio
```bash
curl -L https://istio.io/downloadIstio | sh -
cd istio-*/bin && export PATH=$PATH:$(pwd)
```

### Problem: Pod showing 1/1 instead of 2/2
**Solution**: Sidecar wasn't injected
```bash
# Make sure namespace has label
kubectl get ns default --show-labels
# Should include: istio-injection=enabled

# If not labeled, label it and restart pod
kubectl label namespace default istio-injection=enabled --overwrite
kubectl delete pod <atlas-pod-name>
```

### Problem: Can't connect to localhost:23000
**Solution**: Port forwarding not running
```bash
# Verify port forward is running
kubectl port-forward -n istio-system svc/istio-ingressgateway 23000:23000

# Or check if port is already in use
lsof -i :23000
```

### Problem: Gateway/VirtualService not recognized
**Solution**: Istio not installed or CRDs not registered
```bash
# Verify Istio is installed
kubectl get crd | grep istio

# If not, install Istio:
istioctl install --set profile=demo -y
```

### Problem: HTTP 503 or routing errors
**Solution**: Check VirtualService destination
```bash
# Verify VirtualService points to right service
kubectl get vs atlas-virtualservice -o yaml

# Should show:
# destination:
#   host: atlas.default.svc.cluster.local
#   port:
#     number: 23000
```

## Monitoring

### Check Sidecar Logs

```bash
kubectl logs <atlas-pod-name> -c istio-proxy
```

### Check Traffic Flow

```bash
# Get Envoy stats
kubectl exec <atlas-pod-name> -c istio-proxy -- curl localhost:15000/stats | grep upstream
```

### Analyze Configuration

```bash
istioctl analyze
```

## Cleanup

Remove everything:

```bash
# Delete Atlas deployment
kubectl delete -f apache-atlas/*.yaml
kubectl delete -f apache-atlas/istio/*.yaml

# Remove Istio
istioctl uninstall --purge

# Remove namespaces
kubectl delete namespace istio-system
```

## Files

- `deploy.sh` - Automated deployment script
- `atlas-*.yaml` - Atlas resources
- `istio/atlas-istio-ingress.yaml` - Istio Gateway/VirtualService
- `istio/README.md` - Quick Istio reference

## More Information

- [Istio Documentation](https://istio.io/latest/docs/)
- [Istio Gateway](https://istio.io/latest/docs/reference/config/networking/v1beta1/gateway/)
- [VirtualService](https://istio.io/latest/docs/reference/config/networking/v1beta1/virtual-service/)

