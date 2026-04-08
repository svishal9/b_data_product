# Atlas + Istio Quick Reference

## TL;DR - Deploy in 2 Commands

```bash
cd apache-atlas
./deploy.sh
```

That's it! The script handles everything.

## What Was Fixed

| Issue | Fix |
|-------|-----|
| CRDs not found | Install Istio with `istioctl install --set profile=demo -y` |
| istio-system namespace missing | Created namespace in deploy.sh |
| Missing sidecar injection | Added label to default namespace and annotation to deployment |
| API version incompatibility | Updated from v1alpha3 to v1beta1 in yaml files |
| Missing namespaces in resources | Added explicit `namespace: default` and `namespace: istio-system` |

## File Changes Summary

### New Files Created
- `deploy.sh` - Automated deployment script
- `kustomization.yaml` - Kustomize configuration
- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `ISTIO_INTEGRATION_FIX.md` - Detailed issue explanation
- `QUICK_REFERENCE.md` - This file

### Modified Files
- `atlas-istio-ingress.yaml`:
  - API version: v1alpha3 → v1beta1
  - Added explicit namespaces to Gateway and VirtualService
  - Updated destination host to FQDN
  
- `atlas-deployment.yaml`:
  - Added sidecar injection annotation

## Access Atlas

### Method 1: Port Forwarding (Easy)
```bash
# Terminal 1: Start port forwarding
kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000

# Terminal 2: Access in browser
open http://localhost:23000
```

### Method 2: Minikube Service
```bash
minikube service istio-ingressgateway-atlas -n istio-system
```

### Method 3: Get LoadBalancer IP (Cloud deployments)
```bash
kubectl get svc -n istio-system istio-ingressgateway-atlas -o wide
```

## Check Deployment Status

```bash
# All pods running?
kubectl get pods

# Sidecar injected?
kubectl get pods -n default -o wide
# Should see "2/2 Running" = app + sidecar

# Can reach Atlas?
curl http://localhost:23000
# Should get HTTP 401 (expected - auth required)
```

## Troubleshooting Commands

```bash
# View sidecar logs
kubectl logs <pod-name> -c istio-proxy

# Check Gateway configuration
kubectl get gateway -o yaml

# Check VirtualService routing
kubectl get virtualservice -o yaml

# Verify port forwarding
kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000 &
lsof -i :23000

# Delete everything and start over
kubectl delete all --all
./deploy.sh
```

## Architecture at a Glance

```
Browser (http://localhost:23000)
    ↓
Port Forward
    ↓
LoadBalancer Service (istio-ingressgateway-atlas)
    ↓
Istio IngressGateway Pod
    ↓
Gateway Route → VirtualService Route
    ↓
Atlas Service (ClusterIP, port 23000)
    ↓
Atlas Pod + Envoy Sidecar
```

## Key Ports

- **23000**: External access port (through Istio gateway)
- **21000**: Atlas internal port (inside pod)
- **8080**: Istio proxy port (inside pod)
- **15000**: Envoy admin port

## Istio Concepts Used

- **Gateway**: Defines how traffic enters the cluster (port 23000)
- **VirtualService**: Defines routing rules for traffic
- **Sidecar Injection**: Automatic Envoy proxy injection via annotation
- **IngressGateway**: Entry point for external traffic

## Default Credentials

Check with your Atlas deployment team for default login credentials.
Typically: admin / admin (but varies by deployment)

## Next Steps After Deployment

1. Log in to Atlas UI
2. Verify metadata ingestion
3. Configure Atlas policies
4. Monitor sidecar performance: `kubectl logs <pod> -c istio-proxy`

## Need Help?

- See `DEPLOYMENT_GUIDE.md` for detailed instructions
- See `ISTIO_INTEGRATION_FIX.md` for technical details
- Check pod logs: `kubectl logs <pod-name>`
- Describe pod: `kubectl describe pod <pod-name>`

