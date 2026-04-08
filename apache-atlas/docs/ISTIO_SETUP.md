# Apache Atlas + Istio Ingress Setup

This guide walks through exposing Apache Atlas via Istio ingress on port 23000.

## Prerequisites

- Kubernetes cluster (1.20+)
- `kubectl` installed and configured
- `istioctl` CLI tool

## Installation Steps

### 1. Install Istio

If `istioctl` is not installed:

```bash
# macOS
brew install istioctl

# Linux
curl -L https://istio.io/downloadIstio | sh -
```

Install Istio into your cluster:

```bash
istioctl install -y --set profile=demo
```

Enable sidecar injection for your namespace:

```bash
kubectl label namespace default istio-injection=enabled --overwrite
```

Verify Istio installation:

```bash
kubectl get namespace istio-system
kubectl get deployment -n istio-system
```

### 2. Deploy Atlas with Istio Exposure

```bash
cd /Users/vishal/IdeaProjects/scb-data-product/apache-atlas

# Apply Atlas infrastructure (PVCs)
kubectl apply -f atlas-claim0-persistentvolumeclaim.yaml
kubectl apply -f atlas-claim1-persistentvolumeclaim.yaml

# Apply Atlas service (now ClusterIP for internal-only routing)
kubectl apply -f atlas-service.yaml

# Apply Istio Gateway + VirtualService
kubectl apply -f atlas-istio-ingress.yaml

# Deploy Atlas pod
kubectl apply -f atlas-deployment.yaml
```

### 3. (minikube only) Start Minikube Tunnel

If you're running on **minikube**, you need to start the tunnel to assign external IPs to LoadBalancer services:

```bash
# Terminal 1: Start and keep minikube tunnel running
minikube tunnel
```

This allows the Istio IngressGateway LoadBalancer to get an external IP (usually `127.0.0.1` on minikube).

**Without this**, the IngressGateway will show `EXTERNAL-IP: <pending>` and won't be accessible externally.

If you don't want to use `minikube tunnel`, you can instead use `kubectl port-forward` (see "Access Atlas via Port-Forward" below).

## Verification

### Verify Istio CRDs are installed

```bash
kubectl api-resources | grep -E "virtualservices|gateways"
```

Expected output:
```
gateways                                          networking.istio.io/v1alpha3     true         Gateway
virtualservices                       vs          networking.istio.io/v1alpha3     true         VirtualService
```

### Check Atlas resources

```bash
# Verify service
kubectl get svc atlas
# Expected: ClusterIP 10.x.x.x <none> 23000/21000

# Verify deployment
kubectl get deployment atlas

# Verify pods
kubectl get pod -l io.kompose.service=atlas
```

### Check Istio resources

```bash
# Verify Gateway
kubectl get gateway atlas-gateway
kubectl describe gateway atlas-gateway

# Verify VirtualService
kubectl get virtualservice atlas-virtualservice
kubectl describe virtualservice atlas-virtualservice
```

### Find Istio Ingress External IP

```bash
kubectl get svc -n istio-system istio-ingressgateway
```

Example output:
```
NAME                   TYPE           CLUSTER-IP     EXTERNAL-IP   PORT(S)
istio-ingressgateway   LoadBalancer   10.0.0.1       192.168.x.x   23000:31234/TCP
```

If `EXTERNAL-IP` is `<pending>`, the cluster may not support LoadBalancer (e.g., Docker Desktop).

### Test Atlas Access

Once Atlas pod is running and Istio is configured:

```bash
# Get Istio Ingress endpoint
INGRESS_IP=$(kubectl get svc istio-ingressgateway -n istio-system \
  -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

# Curl Atlas UI
curl -v http://$INGRESS_IP:23000/login.jsp

# Or use port-forward if no external IP
kubectl port-forward svc/istio-ingressgateway -n istio-system 23000:23000 &
curl -v http://localhost:23000/login.jsp
```

Expected: HTTP 200 with HTML content from Atlas login page.

## Troubleshooting

### Issue: CRDs not found

**Error:**
```
resource mapping not found for name: "atlas-gateway" namespace: "" from "atlas-istio-ingress.yaml": no matches for kind "Gateway" in version "networking.istio.io/v1alpha3"
```

**Solution:** Istio CRDs not installed. Run:
```bash
istioctl install -y
kubectl rollout status deployment/istiod -n istio-system
```

### Issue: Gateway shows no address

```bash
kubectl get gateway atlas-gateway
# STATUS: Accepted but loadBalancer address is empty
```

**Solution:** Check if your ingress gateway is running:
```bash
kubectl get pod -n istio-system -l app=istio-ingressgateway
```

If pods aren't starting, check logs:
```bash
kubectl logs -n istio-system -l app=istio-ingressgateway
```

### Issue: Cannot reach Atlas from external IP

**Step 1:** Verify service routing works internally:
```bash
kubectl exec -it <atlas-pod> -- curl localhost:21000/login.jsp
```

**Step 2:** Verify Istio VirtualService is correct:
```bash
kubectl describe vs atlas-virtualservice
```

Check that:
- `Hosts:` includes `*`
- `Gateways:` includes `atlas-gateway`
- `Destination Host:` is `atlas`
- `Port:` is `23000`

**Step 3:** Check Istio proxy logs:
```bash
kubectl logs <atlas-pod> -c istio-proxy
```

### Issue: Port already in use

If port 23000 is already exposed by another service:

```bash
# Check what's using port 23000
kubectl get svc --all-namespaces | grep 23000

# If conflict, modify `atlas-istio-ingress.yaml`:
# Change port: 23000 to an unused port (e.g., 8080, 9000)
```

## Architecture Diagram

```
Client (external)
    ↓ :23000
┌─────────────────────────────────────┐
│  Istio IngressGateway (LoadBalancer)│
│  (istio-system namespace)           │
└─────────────────────────────────────┘
    ↓ :23000
┌─────────────────────────────────────┐
│  Gateway: atlas-gateway             │
│  VirtualService: atlas-virtualservice│
│  (default namespace)                │
└─────────────────────────────────────┘
    ↓ :23000 (service port)
┌─────────────────────────────────────┐
│  Service: atlas (ClusterIP)         │
│  Port: 23000 → TargetPort: 21000   │
│  (default namespace)                │
└─────────────────────────────────────┘
    ↓ :21000 (container port)
┌─────────────────────────────────────┐
│  Pod: atlas-server                  │
│  Container Port: 21000              │
│  (default namespace)                │
└─────────────────────────────────────┘
```

## Rollback (Remove Istio)

If you need to revert to direct LoadBalancer access:

```bash
# Delete Istio resources
kubectl delete gateway atlas-gateway
kubectl delete virtualservice atlas-virtualservice

# Change service type back to LoadBalancer
kubectl patch svc atlas -p '{"spec":{"type":"LoadBalancer"}}'

# Verify
kubectl get svc atlas
```

## Next Steps

- Configure TLS/HTTPS for Istio Gateway (use `DestinationRule`, `Certificate`)
- Add request routing policies (e.g., rate limits, retries)
- Set up monitoring (Kiali, Prometheus integration)
- Configure network policies for Atlas namespace

For more details, see [Istio documentation](https://istio.io/latest/docs/).
