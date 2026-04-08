# Docker Build Fixes Applied

## Issues Fixed

### 1. **Dockerfile Syntax Errors**
**Issue**: Dockerfile had lowercase `from` and `as` keywords
- Line 2: `FROM python:3.13-slim as base` 
- Line 21: `FROM base as builder`

**Fix**: Changed to uppercase keywords
- `FROM python:3.13-slim AS base`
- `FROM base AS builder`

**Reason**: Docker buildx expects uppercase `FROM` and `AS` keywords. Lowercase syntax generates warnings and may not work correctly across all Docker versions.

---

### 2. **Build Context Missing Files**
**Issue**: Docker build failed with error `"/pyproject.toml": not found`

**Root Cause**: The `.dockerignore` file was excluding `pyproject.toml` at the end, which prevented it from being included in the build context.

**Fix**: Removed the following exclusions from `.dockerignore`:
```
# Removed from .dockerignore:
pyproject.toml
uv.lock
```

**Reason**: 
- `pyproject.toml` is critical for building dependencies
- `uv.lock` ensures deterministic dependency installation
- These files must be included in the Docker build context

---

### 3. **Environment Variable Syntax Error**
**Issue**: Dockerfile used bash-style default syntax which doesn't work in Docker
```dockerfile
ATLAS_SERVER_HOST=${ATLAS_SERVER_HOST:-localhost}
ATLAS_SERVER_PORT=${ATLAS_SERVER_PORT:-21000}
```

**Fix**: Changed to simple assignment (can be overridden at runtime via docker run -e)
```dockerfile
ATLAS_SERVER_HOST=localhost
ATLAS_SERVER_PORT=21000
```

**Reason**: Docker ENV doesn't support bash parameter expansion. Runtime defaults can be overridden with `-e` flag or Kubernetes ConfigMap.

---

### 4. **Virtual Environment Not Used by uv sync**
**Issue**: Dependencies were not being installed to `/opt/venv`

**Root Cause**: `uv sync --frozen` was creating its own `.venv` directory instead of using the pre-created `/opt/venv`

**Fix**: Changed builder stage to:
1. Create venv explicitly: `uv venv /opt/venv --python python3.13`
2. Compile requirements: `uv pip compile pyproject.toml > /tmp/requirements.txt`
3. Install to venv: `uv pip install --python /opt/venv/bin/python -r /tmp/requirements.txt`

**Reason**: Ensures dependencies are installed into the correct virtual environment that gets copied to the runtime stage

---

### 5. **Process Substitution Not Supported in Docker**
**Issue**: Initial fix tried to use bash process substitution `<()` which doesn't work in Docker's `/bin/sh`

**Fix**: Used temporary file instead for requirements compilation

**Reason**: Docker containers use `/bin/sh` by default, which doesn't support bash-specific features like process substitution

---

## Build Command

The Dockerfile now builds successfully with:
```bash
cd docker-k8s
eval $(minikube docker-env)
docker build -t scb-ingestion:latest .
```

## Verification

✅ Docker image successfully built:
```
scb-ingestion    latest    07f6ad6313de    143MB
```

✅ Container CLI works:
```bash
docker run --rm scb-ingestion:latest --help
usage: scb_dp_cli.py ingest [-h] [--dry-run] [--strict] workbook
```

✅ All dependencies available:
```bash
docker run --rm scb-ingestion:latest bash -c \
  "/opt/venv/bin/python -c 'import apache_atlas; print(apache_atlas.__file__)'"
/opt/venv/lib/python3.13/site-packages/apache_atlas/__init__.py
```

## Files Modified

1. `/Users/vishal/IdeaProjects/scb-data-product/docker-k8s/Dockerfile` - Fixed syntax, builder stage, and dependency installation
2. `/Users/vishal/IdeaProjects/scb-data-product/docker-k8s/.dockerignore` - Removed pyproject.toml and uv.lock exclusions

## Next Steps

1. ✅ Docker container builds successfully
2. ✅ CLI executes within container
3. ✅ All dependencies installed
4. → Test with Kubernetes deployment
5. → Test volume mounts for Excel files
6. → Test with actual Atlas connection


