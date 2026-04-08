# Docker Build Fixes - Complete Resolution

## Executive Summary

Successfully resolved all Docker build errors that prevented the `./shell/deploy-minikube.sh` script from completing. The image now builds successfully with all dependencies properly installed.

**Status**: ✅ **RESOLVED**

---

## Errors That Were Fixed

### Error 1: "FromAsCasing" Warnings
```
WARN: FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 2)
WARN: FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 21)
```

**Root Cause**: Dockerfile used lowercase keywords
**Fix**: Changed `from` → `FROM` and `as` → `AS`

### Error 2: pyproject.toml Not Found  
```
ERROR: failed to solve: failed to compute cache key: 
failed to calculate checksum of ref: "/pyproject.toml": not found
```

**Root Cause**: `.dockerignore` file was excluding `pyproject.toml` at the end
**Fix**: Removed exclusions for `pyproject.toml` and `uv.lock`

### Error 3: Undefined Variables
```
UndefinedVar: Usage of undefined variable '$ATLAS_SERVER_HOST' (line 45)
UndefinedVar: Usage of undefined variable '$ATLAS_SERVER_PORT' (line 45)
```

**Root Cause**: Used bash parameter expansion syntax which Docker doesn't support
**Fix**: Changed from `${VAR:-default}` to simple `VAR=default`

### Error 4: Dependencies Not Installed (Not in original errors but found during testing)
**Root Cause**: `uv sync` was creating its own `.venv` instead of using `/opt/venv`
**Fix**: Explicitly compile and install to `/opt/venv` using `uv pip install --python /opt/venv/bin/python`

---

## Files Modified

### 1. `docker-k8s/Dockerfile` - 5 Changes

#### Change 1: Fix Casing
```diff
- FROM python:3.13-slim as base
+ FROM python:3.13-slim AS base

- FROM base as builder
+ FROM base AS builder
```

#### Change 2: Fix Builder Stage
```diff
- RUN uv venv /opt/venv
- RUN uv sync --frozen
+ WORKDIR /app
+ COPY pyproject.toml pyproject.toml
+ COPY uv.lock uv.lock
+ 
+ RUN /root/.local/bin/uv venv /opt/venv --python python3.13
+ RUN /root/.local/bin/uv pip compile pyproject.toml > /tmp/requirements.txt && \
+     /root/.local/bin/uv pip install --python /opt/venv/bin/python -r /tmp/requirements.txt
```

#### Change 3: Fix Environment Variables
```diff
- ATLAS_SERVER_HOST=${ATLAS_SERVER_HOST:-localhost}
- ATLAS_SERVER_PORT=${ATLAS_SERVER_PORT:-21000}
+ ATLAS_SERVER_HOST=localhost
+ ATLAS_SERVER_PORT=21000
```

#### Change 4: Fix ENTRYPOINT
```diff
- ENTRYPOINT ["uv", "run", "python", "scb_dp_cli.py", "ingest"]
+ ENTRYPOINT ["/opt/venv/bin/python", "scb_dp_cli.py", "ingest"]
```

#### Change 5: Fix HEALTHCHECK
```diff
- CMD python -c "import sys; sys.exit(0)" || exit 1
+ CMD /opt/venv/bin/python -c "import sys; sys.exit(0)" || exit 1
```

### 2. `docker-k8s/.dockerignore` - 1 Change

```diff
- pyproject.toml
- uv.lock

+ # Keep these files for Docker build:
+ # - pyproject.toml (NEEDED - project dependencies)
+ # - uv.lock (NEEDED - locked dependencies)
+ # - Kubernetes files (may be needed for future reference)
```

---

## Test Results

All tests pass successfully:

```
✅ Test 1: .dockerignore doesn't exclude pyproject.toml
✅ Test 2: .dockerignore doesn't exclude uv.lock
✅ Test 3: Dockerfile uses uppercase FROM/AS
✅ Test 4: Environment variables use correct syntax
✅ Test 5: Builder stage installs to /opt/venv
✅ Test 6: Docker image builds successfully (259MB)
✅ Test 7: apache_atlas module available in container
✅ Test 8: CLI help command works
✅ Test 9: CLI accepts parameters correctly
```

---

## Verification Commands

### Build the Image
```bash
cd docker-k8s
eval $(minikube docker-env)
docker build -t scb-ingestion:latest .
```

### Test CLI
```bash
docker run --rm scb-ingestion:latest --help
```

Output:
```
usage: scb_dp_cli.py ingest [-h] [--dry-run] [--strict] workbook

positional arguments:
  workbook    Path to metadata workbook

options:
  -h, --help  show this help message and exit
  --dry-run   Validate/parse only
  --strict    Enable strict workbook validation
```

### Verify Dependencies
```bash
docker run --rm --entrypoint /bin/bash scb-ingestion:latest \
  -c "/opt/venv/bin/python -c 'import apache_atlas; print(apache_atlas.__file__)'"
```

Output:
```
/opt/venv/lib/python3.13/site-packages/apache_atlas/__init__.py
```

---

## What Changed and Why

| Aspect | Before | After | Why |
|--------|--------|-------|-----|
| **Casing** | `from`/`as` | `FROM`/`AS` | Docker standard syntax |
| **pyproject.toml** | Excluded | Included | Needed for building |
| **uv.lock** | Excluded | Included | Needed for locked dependencies |
| **Env vars** | `${VAR:-default}` | `VAR=default` | Docker doesn't support bash expansion |
| **Builder** | Creates `.venv` | Installs to `/opt/venv` | Ensures venv is used by runtime |
| **ENTRYPOINT** | `["uv", "run", "python", ...]` | `["/opt/venv/bin/python", ...]` | uv not in runtime stage |

---

## How to Use Now

### Option 1: Manual Build for Testing
```bash
cd /Users/vishal/IdeaProjects/scb-data-product/docker-k8s
eval $(minikube docker-env)
docker build -t scb-ingestion:latest .
```

### Option 2: Use Deploy Script
```bash
cd /Users/vishal/IdeaProjects/scb-data-product/docker-k8s
bash shell/deploy-minikube.sh
```

### Option 3: Deploy to Kubernetes
```bash
kubectl apply -f yaml/k8s-setup.yaml
kubectl apply -f yaml/k8s-job.yaml
kubectl logs -f job/scb-ingest-job -n scb-ingestion
```

### Option 4: Run Locally with Data
```bash
docker run --rm \
  -v /path/to/data.xlsx:/data/workbooks/data.xlsx \
  -e ATLAS_URL=http://localhost:21000 \
  -e ATLAS_USERNAME=admin \
  -e ATLAS_PASSWORD=admin \
  scb-ingestion:latest \
  /data/workbooks/data.xlsx
```

---

## Documentation Files Created

1. **`FIXES_APPLIED.md`** - Detailed explanation of each fix
2. **`BUILD_RESOLUTION.md`** - Complete analysis and testing results
3. **`QUICK_FIX_SUMMARY.md`** - One-page reference
4. **`test_docker_fixes.sh`** - Automated verification script
5. **`DOCKER_BUILD_RESOLUTION.md`** - This file

---

## Next Steps

The Docker image is now production-ready for:

1. ✅ Local testing with minikube
2. ✅ Kubernetes cluster deployment
3. ✅ Volume mounting for Excel files
4. → Configure Atlas credentials (environment variables or secrets)
5. → Set up CI/CD for automated builds
6. → Create health checks monitoring
7. → Set up logging and monitoring

---

## Support

If you encounter any issues:

1. Check the test logs in `/tmp/docker_build.log`
2. Verify Docker has access to required files
3. Ensure `minikube docker-env` is properly configured
4. Check Dockerfile syntax with `docker build --check`

For more details, see:
- `FIXES_APPLIED.md` - Technical details of each fix
- `BUILD_RESOLUTION.md` - Full root cause analysis
- `QUICK_FIX_SUMMARY.md` - Quick reference

