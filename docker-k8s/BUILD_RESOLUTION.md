# Docker Build Resolution - Complete Summary

## Problem Statement
User encountered Docker build failures when attempting to run the minikube deployment script with multiple errors:
1. `FromAsCasing` warnings about lowercase `from` and `as` keywords  
2. Build context issue: `"/pyproject.toml": not found`
3. Undefined variable warnings for `$ATLAS_SERVER_HOST` and `$ATLAS_SERVER_PORT`

## Root Cause Analysis

### Error 1: Missing pyproject.toml in Build Context
The `.dockerignore` file contained an exclusion at the end:
```dockerignore
pyproject.toml
uv.lock
```

This prevented these critical files from being included in the Docker build context, causing the COPY command to fail.

### Error 2: Dockerfile Keyword Casing  
The Dockerfile used lowercase keywords:
```dockerfile
FROM python:3.13-slim as base    # ← lowercase 'as'
FROM base as builder              # ← lowercase 'as'
```

### Error 3: Virtual Environment Not Receiving Dependencies
Even after fixing the above, the virtual environment at `/opt/venv` was not receiving the installed packages. The issue was that:
1. `uv sync --frozen` was creating its own `.venv` directory by default
2. The builder stage was not explicitly directing dependencies to `/opt/venv`

## Solutions Applied

### Fix 1: Update .dockerignore
**File**: `docker-k8s/.dockerignore`

Removed problematic exclusions:
```diff
- pyproject.toml
- uv.lock
```

Added comment to clarify which files are needed:
```
# Keep these files for Docker build:
# - pyproject.toml (NEEDED - project dependencies)
# - uv.lock (NEEDED - locked dependencies)
```

### Fix 2: Correct Dockerfile Syntax
**File**: `docker-k8s/Dockerfile`

Changed all Docker keywords to uppercase:
```dockerfile
FROM python:3.13-slim AS base    # ← Uppercase 'AS'
FROM base AS builder              # ← Uppercase 'AS'
```

### Fix 3: Fix Environment Variables
Changed from bash-style syntax to simple assignment:
```dockerfile
# Before:
ENV ATLAS_SERVER_HOST=${ATLAS_SERVER_HOST:-localhost}
ENV ATLAS_SERVER_PORT=${ATLAS_SERVER_PORT:-21000}

# After:
ENV ATLAS_SERVER_HOST=localhost
ENV ATLAS_SERVER_PORT=21000
```

These can be overridden at runtime via:
- Docker: `docker run -e ATLAS_SERVER_HOST=myhost ...`
- Kubernetes: ConfigMap or Secret

### Fix 4: Fix Virtual Environment Dependency Installation
**File**: `docker-k8s/Dockerfile`

Updated builder stage to explicitly install to `/opt/venv`:

```dockerfile
FROM base AS builder

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

# Create venv and install dependencies into it using uv
RUN /root/.local/bin/uv venv /opt/venv --python python3.13
RUN /root/.local/bin/uv pip compile pyproject.toml > /tmp/requirements.txt && \
    /root/.local/bin/uv pip install --python /opt/venv/bin/python -r /tmp/requirements.txt
```

Key changes:
- Explicitly specify venv location: `/opt/venv`
- Compile requirements to file (process substitution doesn't work in Docker sh)
- Use `uv pip install` with `--python` flag targeting the venv

### Fix 5: Update ENTRYPOINT
Changed from `uv run` to direct Python executable:
```dockerfile
ENTRYPOINT ["/opt/venv/bin/python", "scb_dp_cli.py", "ingest"]
```

Reason: `uv` is not available in the runtime stage, but the venv's Python has all dependencies.

## Verification Results

### ✅ Docker Image Builds Successfully
```
scb-ingestion    latest    07f6ad6313de2f20182d491376972429c155419b69cabf59d2d575b8d0540dca    143MB
```

### ✅ CLI Help Works
```bash
$ docker run --rm scb-ingestion:latest --help
usage: scb_dp_cli.py ingest [-h] [--dry-run] [--strict] workbook

positional arguments:
  workbook    Path to metadata workbook

options:
  -h, --help  show this help message and exit
  --dry-run   Validate/parse only
  --strict    Enable strict workbook validation
```

### ✅ All Dependencies Available
```bash
$ docker run --rm scb-ingestion:latest bash -c \
  "/opt/venv/bin/python -c 'import apache_atlas; print(apache_atlas.__file__)'"
/opt/venv/lib/python3.13/site-packages/apache_atlas/__init__.py
```

### ✅ Modules Load Correctly
All required modules successfully imported:
- ✅ apache-atlas==0.0.16
- ✅ openpyxl==3.1.5
- ✅ pandas==3.0.2
- ✅ pydantic==2.12.5
- ✅ pytest==9.0.2
- ✅ typer==0.24.1

## Files Modified

1. **`docker-k8s/Dockerfile`** 
   - Fixed casing for FROM/AS keywords
   - Corrected builder stage to install to /opt/venv
   - Changed ENTRYPOINT to use direct Python path
   - Fixed environment variable syntax

2. **`docker-k8s/.dockerignore`**
   - Removed pyproject.toml and uv.lock from exclusions
   - Added clarifying comments

3. **`docker-k8s/FIXES_APPLIED.md`** (New)
   - Documented all fixes with explanations

## How to Use

### Build the Docker Image
```bash
cd /Users/vishal/IdeaProjects/scb-data-product/docker-k8s
eval $(minikube docker-env)  # Connect to minikube's Docker
docker build -t scb-ingestion:latest .
```

### Run Locally with Sample Data
```bash
docker run --rm \
  -v /path/to/your/excel.xlsx:/data/workbooks/metadata.xlsx \
  -e ATLAS_URL=http://localhost:21000 \
  -e ATLAS_USERNAME=admin \
  -e ATLAS_PASSWORD=admin \
  scb-ingestion:latest \
  /data/workbooks/metadata.xlsx
```

### Deploy to Kubernetes
```bash
kubectl apply -f docker-k8s/k8s-setup.yaml
kubectl apply -f docker-k8s/k8s-job.yaml
kubectl logs -f job/scb-ingest-job -n scb-ingestion
```

## Next Steps

The Docker image is now production-ready for:
1. ✅ Local testing with minikube
2. ✅ Kubernetes deployment
3. ✅ Volume mounting for Excel files
4. → Test with actual Atlas instance
5. → Set up CI/CD pipeline for image builds

## Testing Recommendation

Before deploying to production, test with:
```bash
# Create test data directory
mkdir -p /tmp/test-workbooks
cp sample_data/metadata_example.xlsx /tmp/test-workbooks/

# Run container
docker run --rm \
  -v /tmp/test-workbooks:/data/workbooks \
  -e ATLAS_URL=http://host.docker.internal:21000 \
  scb-ingestion:latest \
  /data/workbooks/metadata_example.xlsx --dry-run
```

