# SCB Data Product Ingestion - Docker & Kubernetes Setup

## Overview

This directory contains Docker and Kubernetes configurations for running the SCB Data Product ingestion command (`uv run python scb_dp_cli.py ingest`) in containerized environments. The setup supports:

- **Local Testing**: Running on minikube for development and testing
- **Production Deployment**: Deploying to Kubernetes clusters
- **Reusable Configuration**: Same YAML files work for both environments

## Directory Structure

```
docker-k8s/
├── Dockerfile                 # Multi-stage Docker image definition
├── yaml/
│   ├── k8s-setup.yaml        # Kubernetes namespace, ConfigMap, Secret, RBAC, PVC setup
│   ├── k8s-job.yaml          # Kubernetes Job and CronJob definitions
│   └── config-template.yaml  # Configuration template
├── shell/
│   ├── deploy-minikube.sh    # Script for deploying to minikube
│   └── deploy-production.sh  # Script for deploying to production cluster
├── python/
    ├── test_deployment.py    # Unit and integration tests
    └── test_docker_build.py  # Docker build validation tests
└── README.md                 # This file
```

## Quick Start

### Prerequisites

- Docker installed and running
- kubectl installed and configured
- For local testing: minikube installed and running
- Python 3.13+ (for running tests)
- uv package manager

### For Minikube (Local Testing)

1. **Start minikube** (if not running):
```bash
minikube start --cpus=4 --memory=4096
```

2. **Deploy to minikube**:
```bash
cd docker-k8s
chmod +x shell/deploy-minikube.sh
./shell/deploy-minikube.sh
```

3. **Upload workbook** (if using persistent volume):
```bash
# Create a sample workbook or use existing one
kubectl cp <local-workbook-path> scb-ingestion/<pod-name>:/data/workbooks/
```

4. **Monitor the job**:
```bash
kubectl logs -n scb-ingestion -f job/scb-ingest-job
kubectl describe job scb-ingest-job -n scb-ingestion
```

### For Production Cluster

1. **Build and push Docker image**:
```bash
docker build -t <your-registry>/scb-ingestion:latest .
docker push <your-registry>/scb-ingestion:latest
```

2. **Update image in yaml/k8s-job.yaml** (if using custom registry):
```yaml
image: <your-registry>/scb-ingestion:latest
```

3. **Deploy to production**:
```bash
cd docker-k8s
chmod +x shell/deploy-production.sh
./shell/deploy-production.sh
```

> Note: `shell/deploy-production.sh` fails fast if `scb-atlas-credentials` still uses `REPLACE_ME` values.

4. **Deploy the job**:
```bash
kubectl apply -f yaml/k8s-job.yaml
```

## Component Details

### Dockerfile

**Features:**
- Multi-stage build for smaller final image size
- Based on `python:3.13-slim`
- Uses `uv` for fast dependency resolution and installation
- Includes health checks
- Environment variables for Atlas server configuration
- Workbook mount point at `/data/workbooks`

**Build Arguments:**
- None currently, but can be extended with custom registries

**Environment Variables:**
- `ATLAS_SERVER_HOST`: Apache Atlas server hostname (default: localhost)
- `ATLAS_SERVER_PORT`: Apache Atlas server port (default: 21000)
- `PYTHONUNBUFFERED`: Ensures Python output is not buffered

### Kubernetes Setup (yaml/k8s-setup.yaml)

Creates the following resources:

1. **Namespace**: `scb-ingestion`
   - Dedicated namespace for ingestion operations

2. **ConfigMap**: `scb-atlas-config`
   - Stores Atlas server connection configuration
   - Centralized configuration management

3. **Secret**: `scb-atlas-credentials`
   - Stores Atlas username/password
   - Credentials are not kept in ConfigMap defaults

4. **ServiceAccount**: `scb-ingestion-sa`
   - Provides identity for running jobs

5. **ClusterRole & ClusterRoleBinding**: RBAC configuration
   - Minimal permissions for job execution
   - Can list pods, configmaps, secrets, and jobs

6. **PersistentVolumeClaim**: `scb-workbooks-pvc`
   - 5Gi storage for Excel workbooks
   - Uses standard StorageClass

### Kubernetes Job (yaml/k8s-job.yaml)

Defines two types of workloads:

1. **Job** (`scb-ingest-job`)
   - One-time ingestion job
   - Automatic cleanup after 1 hour
   - 3 retry attempts on failure
   - Resource requests: 512Mi memory, 250m CPU
   - Resource limits: 2Gi memory, 1000m CPU

2. **CronJob** (`scb-ingest-scheduled`)
   - Scheduled daily ingestion at 2 AM (configurable)
   - Keeps last 3 successful and 3 failed jobs
   - Same resources as one-time job

## Configuration

### Atlas Server Connection

Edit `yaml/k8s-setup.yaml` to update Atlas server details:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: scb-atlas-config
  namespace: scb-ingestion
data:
  ATLAS_SERVER_HOST: "atlas"          # Update to your Atlas hostname
  ATLAS_SERVER_PORT: "21000"
```

Set Atlas credentials via Secret (default pattern):

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: scb-atlas-credentials
  namespace: scb-ingestion
type: Opaque
stringData:
  ATLAS_USERNAME: <atlas-username>
  ATLAS_PASSWORD: <secure-password>
```

Then reference it in the Job:
```yaml
envFrom:
- secretRef:
    name: scb-atlas-credentials
```

### Workbook Management

**Option 1: Persistent Volume**
- Workbooks stored in PVC
- Upload using `kubectl cp` or volume mount

**Option 2: ConfigMap**
- Small workbooks (<1MB) can be stored in ConfigMap
- Reference in Job volumeMounts

**Option 3: External Storage**
- Use cloud storage (S3, GCS, Azure Blob)
- Download in init container

## Testing

### Run Unit Tests

```bash
cd docker-k8s
pytest python/test_deployment.py -v
pytest python/test_docker_build.py -v
```

### Test Specific Components

```bash
# Test Dockerfile syntax only
pytest python/test_docker_build.py::TestDockerImageBuild::test_dockerfile_base_image_valid -v

# Test Kubernetes YAML structure
pytest python/test_deployment.py::TestKubernetesYAML -v

# Test deployment scripts
pytest python/test_deployment.py::TestDeploymentScripts -v
```

### Manual Testing on Minikube

```bash
# After deploying with shell/deploy-minikube.sh:

# Check if resources were created
kubectl get all -n scb-ingestion

# Verify ConfigMap and Secret
kubectl get configmap -n scb-ingestion
kubectl get secret scb-atlas-credentials -n scb-ingestion

# Check PVC status
kubectl get pvc -n scb-ingestion

# Test connectivity to Atlas (if running)
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://atlas:21000/api/atlas/v2/types/typedefs
```

## Monitoring & Debugging

### View Job Logs

```bash
# Real-time logs
kubectl logs -n scb-ingestion -f job/scb-ingest-job

# Last 100 lines
kubectl logs -n scb-ingestion --tail=100 job/scb-ingest-job

# With timestamps
kubectl logs -n scb-ingestion job/scb-ingest-job --timestamps=true
```

### Describe Resources

```bash
# Job details
kubectl describe job scb-ingest-job -n scb-ingestion

# Pod details
kubectl describe pod <pod-name> -n scb-ingestion

# Node allocation
kubectl get pod -n scb-ingestion -o wide
```

### Check Job Status

```bash
# Job completion status
kubectl get job -n scb-ingestion

# Job events
kubectl get events -n scb-ingestion

# Watch job progress
kubectl get job -n scb-ingestion -w
```

### Access Pod Interactive Shell

```bash
# For running pod
kubectl exec -it <pod-name> -n scb-ingestion -- /bin/bash

# For failed pod (if restartPolicy allows)
kubectl debug <pod-name> -n scb-ingestion -it --image=python:3.13-slim
```

## Troubleshooting

### Image Pull Errors

**Problem**: `ImagePullBackOff` error on minikube

**Solution**:
```bash
# Ensure image is built locally
eval $(minikube docker-env)
docker build -t scb-ingestion:latest .

# Update imagePullPolicy in k8s-job.yaml
imagePullPolicy: IfNotPresent
```

### Job Stays in Pending

**Problem**: Job not starting

**Solutions**:
```bash
# Check resource availability
kubectl describe nodes

# Check if image is available
docker images | grep scb-ingestion

# Verify PVC is bound
kubectl get pvc -n scb-ingestion
```

### Connection to Atlas Failed

**Problem**: `Connection refused` errors

**Solutions**:
```bash
# Check Atlas service is running
kubectl get svc atlas

# Verify network connectivity
kubectl run -it --rm debug --image=alpine --restart=Never -- \
  nc -zv atlas 21000

# Update ATLAS_SERVER_HOST in k8s-setup.yaml
# Use full DNS: atlas.atlas-system.svc.cluster.local
```

### Out of Disk Space

**Problem**: Job fails with disk space errors

**Solution**:
```bash
# Check disk usage
kubectl exec <pod-name> -n scb-ingestion -- df -h

# Increase PVC size (if supported by StorageClass)
kubectl patch pvc scb-workbooks-pvc -n scb-ingestion -p \
  '{"spec":{"resources":{"requests":{"storage":"10Gi"}}}}'
```

## Performance Tuning

### Resource Requests/Limits

Edit `k8s-job.yaml` to adjust:
- Memory request/limit
- CPU request/limit
- Timeout settings

```yaml
resources:
  requests:
    memory: "512Mi"    # Minimum required
    cpu: "250m"
  limits:
    memory: "2Gi"      # Maximum allowed
    cpu: "1000m"
```

### Job Parallelization

For processing multiple workbooks:

```yaml
spec:
  parallelism: 3       # Run 3 jobs in parallel
  completions: 10      # Total jobs to run
  backoffLimit: 3
```

### Timeout Configuration

```yaml
spec:
  template:
    spec:
      containers:
      - name: scb-ingestion
        command: ["timeout", "300", "/opt/venv/bin/python", "scb_dp_cli.py", "ingest"]
```

## Production Deployment Checklist

- [ ] Update `ATLAS_SERVER_HOST` to production Atlas endpoint
- [ ] Rotate `scb-atlas-credentials` and avoid committing real values
- [ ] Configure production image registry
- [ ] Set resource requests/limits appropriately
- [ ] Enable pod security policies
- [ ] Configure network policies if needed
- [ ] Set up monitoring and alerting
- [ ] Test rollback procedures
- [ ] Document runbook procedures
- [ ] Test scheduled job (CronJob) configuration

## Reusing Configuration for Multiple Environments

The setup is designed to be environment-agnostic:

**For different clusters**:
```bash
# Minikube
kubectl config use-context minikube
./shell/deploy-minikube.sh

# Production
kubectl config use-context production-cluster
./shell/deploy-production.sh
```

**For different workbooks**:
```bash
# Copy workbook to persistent volume
kubectl cp workbook1.xlsx scb-ingestion/pod-name:/data/workbooks/

# Or update ConfigMap with new workbook path
kubectl set env job/scb-ingest-job WORKBOOK_PATH=/data/workbooks/workbook1.xlsx
```

## Related Documentation

- [Apache Atlas Setup](../apache-atlas/ATLAS_SETUP_GUIDE.md)
- [SCB CLI Documentation](../docs/LEGACY_COMMAND_MIGRATION.md)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review pod logs: `kubectl logs -n scb-ingestion`
3. Check events: `kubectl get events -n scb-ingestion`
4. Review scb_dp_cli.py documentation

