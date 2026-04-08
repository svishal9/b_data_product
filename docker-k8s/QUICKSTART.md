# Quick Start Guide - SCB Ingestion on Kubernetes

## 🚀 60-Second Setup for Minikube

```bash
# 1. Navigate to docker-k8s directory
cd docker-k8s

# 2. Run automated setup
./shell/deploy-minikube.sh

# 3. Watch the progress
kubectl logs -n scb-ingestion -f job/scb-ingest-job
```

## 🐳 Docker Image Build

```bash
# Build locally
docker build -t scb-ingestion:latest -f Dockerfile .

# Or use the management tool
source shell/commands.sh
build_image
```

## 📊 Common Operations

### Check Status
```bash
source shell/commands.sh
job_status
health_check
```

### View Logs
```bash
# Last 50 lines
kubectl logs -n scb-ingestion job/scb-ingest-job

# Follow in real-time
kubectl logs -n scb-ingestion -f job/scb-ingest-job

# Or use the tool
source shell/commands.sh
job_logs_follow
```

### Upload Workbook
```bash
./shell/upload-workbook-to-pvc.sh /path/to/metadata.xlsx

# Or use the tool
source shell/commands.sh
upload_workbook /path/to/metadata.xlsx
```

### Debug Pod
```bash
# Access pod shell
kubectl exec -it <pod-name> -n scb-ingestion -- /bin/bash

# Or use the tool
source shell/commands.sh
pod_shell
```

## 🔧 Configuration

### Update Atlas Server
Edit `yaml/k8s-setup.yaml`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scb-atlas-config
  namespace: scb-ingestion
data:
  ATLAS_SERVER_HOST: "your-atlas-host"
  ATLAS_SERVER_PORT: "21000"
```

Update Atlas credentials (Secret):
```bash
kubectl create secret generic scb-atlas-credentials \
  -n scb-ingestion \
  --from-literal=ATLAS_USERNAME='<atlas-username>' \
  --from-literal=ATLAS_PASSWORD='<atlas-password>' \
  --dry-run=client -o yaml | kubectl apply -f -
```

Then apply:
```bash
kubectl apply -f yaml/k8s-setup.yaml
```

### Change Job Schedule
Edit `yaml/k8s-job.yaml` CronJob section:
```yaml
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
```

Or use the tool:
```bash
source shell/commands.sh
set_atlas_host "new-host"
set_atlas_port "21000"
```

## 🧪 Testing

```bash
# Run all tests
pytest python/test_deployment.py python/test_docker_build.py -v

# Run specific tests
pytest python/test_deployment.py::TestKubernetesYAML -v
```

## 📋 Useful Commands

```bash
# List all resources
kubectl get all -n scb-ingestion

# Describe job
kubectl describe job scb-ingest-job -n scb-ingestion

# Get pod details
kubectl get pods -n scb-ingestion -o wide

# Delete job
kubectl delete job scb-ingest-job -n scb-ingestion

# Watch job progress
kubectl get job -n scb-ingestion -w

# Check PVC
kubectl get pvc -n scb-ingestion

# View events
kubectl get events -n scb-ingestion
```

## 🛠️ Management Tools

### Using manage.sh
```bash
./shell/manage.sh status        # Show job status
./shell/manage.sh logs -f       # Follow logs
./shell/manage.sh health        # Health check
./shell/manage.sh deploy        # Deploy job
./shell/manage.sh shell         # Access pod shell
./shell/manage.sh watch         # Watch progress
./shell/manage.sh restart       # Restart job
```

### Using commands.sh
```bash
source shell/commands.sh

# Available functions:
build_image              # Build Docker image
submit_job              # Submit job
job_status              # Get status
job_logs_follow         # Follow logs
list_pods               # List pods
upload_workbook <path>  # Upload workbook
show_atlas_config       # Show config
cleanup                 # Delete all
reset                   # Delete namespace
```

## 🚨 Troubleshooting

### Job Stays Pending
```bash
kubectl describe job scb-ingest-job -n scb-ingestion
kubectl describe pods -n scb-ingestion
```

### Connection Failed
```bash
# Check ConfigMap
kubectl get configmap scb-atlas-config -n scb-ingestion -o yaml

# Check Secret keys (metadata only)
kubectl get secret scb-atlas-credentials -n scb-ingestion

# Test connectivity
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://atlas:21000/api/atlas/v2/types/typedefs
```

### Pod Failing
```bash
# Get pod events
kubectl describe pod <pod-name> -n scb-ingestion

# Check previous logs
kubectl logs <pod-name> -n scb-ingestion --previous

# Access pod for debugging
kubectl exec -it <pod-name> -n scb-ingestion -- /bin/bash
```

### Out of Memory
```bash
# Check resource usage
kubectl top pod -n scb-ingestion

# Increase limits in yaml/k8s-job.yaml
resources:
  limits:
    memory: "4Gi"  # Increase from 2Gi
```

## 📚 Documentation

- **README.md** - Comprehensive guide (500+ lines)
- **IMPLEMENTATION_SUMMARY.md** - Complete overview
- **yaml/config-template.yaml** - Configuration reference
- **python/test_deployment.py** - Test documentation

## 🎯 Production Deployment

```bash
# 1. Build and push to registry
docker build -t your-registry/scb-ingestion:v1.0 .
docker push your-registry/scb-ingestion:v1.0

# 2. Update image in yaml/k8s-job.yaml
# Change: image: scb-ingestion:latest
# To: image: your-registry/scb-ingestion:v1.0

# 3. Deploy setup
./shell/deploy-production.sh

# 4. Apply advanced security
./shell/setup-advanced.sh

# 5. Deploy job
kubectl apply -f yaml/k8s-job.yaml
```

## 📊 File Reference

| File | Purpose |
|------|---------|
| Dockerfile | Multi-stage Docker image |
| yaml/k8s-setup.yaml | Namespace, ConfigMap, RBAC, PVC |
| yaml/k8s-job.yaml | Job and CronJob definitions |
| shell/deploy-minikube.sh | Minikube deployment script |
| shell/deploy-production.sh | Production deployment script |
| shell/manage.sh | Operational management tool |
| shell/commands.sh | Quick reference functions |
| shell/upload-workbook-to-pvc.sh | Upload workbook into PVC |
| shell/setup-advanced.sh | Security hardening setup |
| python/test_deployment.py | Deployment tests |
| python/test_docker_build.py | Docker validation tests |

## ✅ Pre-Flight Checklist

Before running in production:

- [ ] Update Atlas server hostname in yaml/k8s-setup.yaml
- [ ] Set up Kubernetes Secrets for credentials
- [ ] Configure resource limits appropriately
- [ ] Enable Network Policies (shell/setup-advanced.sh)
- [ ] Set up monitoring (if available)
- [ ] Test on minikube first
- [ ] Review logs for errors
- [ ] Verify workbook mounts
- [ ] Check RBAC permissions
- [ ] Plan backup strategy

## 🆘 Getting Help

1. Check README.md for detailed troubleshooting
2. Run `./shell/manage.sh health` for diagnostics
3. Check pod logs: `kubectl logs -f job/scb-ingest-job -n scb-ingestion`
4. Review events: `kubectl get events -n scb-ingestion`
5. Access pod shell for debugging: `./shell/manage.sh shell`

## 📞 Quick Links

- Kubernetes Docs: https://kubernetes.io/docs/
- Docker Docs: https://docs.docker.com/
- Apache Atlas: http://atlas.apache.org/

---

**Last Updated**: April 2026  
**Status**: ✅ Production Ready  
**Version**: 1.0

