# Atlas + Istio Deployment Checklist

## Pre-Deployment

- [ ] Kubernetes cluster is running (Minikube, EKS, GKE, etc.)
- [ ] `kubectl` is configured and can access the cluster
- [ ] `istioctl` is installed and in PATH
- [ ] User has cluster-admin permissions

## Deployment

- [ ] Navigate to `apache-atlas` directory: `cd apache-atlas`
- [ ] Run deployment script: `./deploy.sh`
- [ ] Script completes without errors
- [ ] Note the port-forwarding command from output

## Post-Deployment Verification

### Istio Installation
- [ ] Check Istio pods: `kubectl get pods -n istio-system`
  - [ ] `istiod-*` pod is Running
  - [ ] `istio-ingressgateway-*` pod is Running
  - [ ] `istio-egressgateway-*` pod is Running
- [ ] Verify Istio version: `istioctl version`

### Namespace Configuration
- [ ] Check default namespace label: `kubectl get ns default --show-labels`
  - [ ] Should include `istio-injection=enabled`
- [ ] Check istio-system namespace exists: `kubectl get ns istio-system`

### Atlas Resources
- [ ] PVCs created: `kubectl get pvc`
  - [ ] `atlas-claim0` exists and status is Bound
  - [ ] `atlas-claim1` exists and status is Bound
- [ ] Service created: `kubectl get svc`
  - [ ] `atlas` service exists with port 23000
- [ ] Deployment created: `kubectl get deploy`
  - [ ] `atlas` deployment shows 1/1 ready

### Sidecar Injection
- [ ] Pod has 2 containers: `kubectl get pods -n default`
  - [ ] Status shows `2/2 Running` (app + sidecar)
- [ ] Verify sidecar name: `kubectl get pod <atlas-pod> -o jsonpath='{.spec.containers[*].name}'`
  - [ ] Output includes `istio-proxy`
- [ ] Check sidecar image: `kubectl describe pod <atlas-pod> | grep istio-proxy`
  - [ ] Shows `istio/proxyv2` image

### Istio Routing
- [ ] Gateway created: `kubectl get gateway`
  - [ ] `atlas-gateway` exists
  - [ ] Status shows all conditions green
- [ ] VirtualService created: `kubectl get virtualservice`
  - [ ] `atlas-virtualservice` exists
  - [ ] Status shows all conditions green
- [ ] LoadBalancer service: `kubectl get svc -n istio-system`
  - [ ] `istio-ingressgateway-atlas` exists
  - [ ] Port 23000 is listed

### Connectivity Testing

#### Step 1: Start Port Forwarding
- [ ] Run: `kubectl port-forward -n istio-system svc/istio-ingressgateway-atlas 23000:23000`
- [ ] Output shows `Forwarding from 127.0.0.1:23000 -> 8080`
- [ ] Output shows `Forwarding from [::1]:23000 -> 8080`

#### Step 2: Test Connection
- [ ] Open new terminal
- [ ] Run: `curl -v http://localhost:23000`
- [ ] Response should be:
  - [ ] HTTP/1.1 401 Unauthorized (expected - auth required)
  - [ ] Header includes `server: istio-envoy`
  - [ ] Header includes `set-cookie: ATLASSESSIONID`

#### Step 3: Verify Routing
- [ ] Connection goes through Envoy sidecar
- [ ] No "Connection refused" errors
- [ ] Response time is reasonable (< 5 seconds)

## Logs Inspection

### Atlas Pod Logs
- [ ] Check application logs: `kubectl logs -f <atlas-pod> -c atlas-server | head -20`
  - [ ] No critical errors
  - [ ] Atlas is initialized
- [ ] Check sidecar logs: `kubectl logs <atlas-pod> -c istio-proxy | head -20`
  - [ ] No initialization errors
  - [ ] Proxy is ready

### Istio Control Plane Logs
- [ ] Check Istiod: `kubectl logs -n istio-system -l app=istiod | head -20`
  - [ ] No errors related to Gateway or VirtualService
- [ ] Check IngressGateway: `kubectl logs -n istio-system -l app=istio-ingressgateway | head -20`
  - [ ] Port 23000 is configured
  - [ ] No error messages

## Performance Checks

- [ ] Pod CPU usage is reasonable: `kubectl top pod <atlas-pod>`
- [ ] Pod memory usage is within limits: `kubectl top pod <atlas-pod>`
- [ ] Pod has been running for > 1 minute without restart

## Advanced Verification

### Sidecar Configuration
```bash
# Check if sidecar received configuration
kubectl exec <atlas-pod> -c istio-proxy -- curl localhost:15000/config_dump | grep -i gateway
```
- [ ] Output includes gateway configuration
- [ ] Port 23000 is present in configuration

### Traffic Flow
```bash
# Check Envoy statistics
kubectl exec <atlas-pod> -c istio-proxy -- curl localhost:15000/stats | grep -i upstream
```
- [ ] Shows connection statistics
- [ ] No upstream_rq_timeout errors

### Mesh Status
```bash
# Analyze configuration
istioctl analyze
```
- [ ] Output shows "No validation errors found"
- [ ] Or only warnings (not errors)

## Common Issues Checklist

If deployment fails, check these in order:

### Failed to Install Istio
- [ ] istioctl is in PATH: `which istioctl`
- [ ] Istio version is compatible: `istioctl version`
- [ ] Sufficient cluster resources available
- [ ] No existing Istio installation conflicts

### Pod Not Getting Sidecar
- [ ] Namespace has correct label: `kubectl get ns -L istio-injection`
- [ ] Pod was created AFTER label applied: `kubectl describe pod <atlas-pod> | grep Created`
- [ ] If not, delete pod: `kubectl delete pod <atlas-pod>`

### Can't Connect to Port 23000
- [ ] Port forwarding is running: `lsof -i :23000`
- [ ] Service exists: `kubectl get svc -n istio-system istio-ingressgateway-atlas`
- [ ] Pod is running: `kubectl get pods -n istio-system -l app=istio-ingressgateway`

### Gateway/VirtualService Not Recognized
- [ ] Istio is installed: `kubectl get crd | grep istio`
- [ ] Wait 30 seconds for webhook to register
- [ ] Try applying again: `kubectl apply -f atlas-istio-ingress.yaml`

## Success Criteria

Your deployment is successful if ALL of the following are true:

✅ All Istio pods are Running
✅ All Atlas pods show 2/2 Running
✅ Gateway exists and shows as working
✅ VirtualService exists and shows as working  
✅ Port 23000 is listening: `curl http://localhost:23000 → 401 Unauthorized`
✅ Sidecar logs show no errors
✅ Atlas logs show application started

## Next Steps After Successful Deployment

- [ ] Access Atlas UI: http://localhost:23000
- [ ] Log in with credentials
- [ ] Test data ingestion
- [ ] Monitor sidecar: `kubectl logs -f <atlas-pod> -c istio-proxy`
- [ ] Review metrics in Istio dashboards if configured
- [ ] Document any custom configurations

## Rollback Procedure

If something goes wrong, rollback is simple:

```bash
# Delete everything
kubectl delete all --all

# Recreate fresh
cd apache-atlas
./deploy.sh
```

## Support Files

- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `QUICK_REFERENCE.md` - Quick lookup commands
- `ISTIO_INTEGRATION_FIX.md` - Technical details
- `ARCHITECTURE_FIX_SUMMARY.md` - Comprehensive summary

