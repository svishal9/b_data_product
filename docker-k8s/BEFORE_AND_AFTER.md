# Docker Build Fixes - Before and After

## Issue 1: Dockerfile Casing

### ❌ BEFORE (Had warnings)
```dockerfile
FROM python:3.13-slim as base
FROM base as builder
```

**Error Output**:
```
WARN: FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 2)
WARN: FromAsCasing: 'as' and 'FROM' keywords' casing do not match (line 21)
```

### ✅ AFTER (Correct)
```dockerfile
FROM python:3.13-slim AS base
FROM base AS builder
```

**Result**: No warnings ✓

---

## Issue 2: pyproject.toml Excluded from Build Context

### ❌ BEFORE (.dockerignore)
```
pyproject.toml
uv.lock
```

**Error Output**:
```
ERROR: failed to solve: failed to compute cache key: 
failed to calculate checksum of ref: "/pyproject.toml": not found
```

### ✅ AFTER (.dockerignore)
Removed exclusions and added comments:
```
# Keep these files for Docker build:
# - pyproject.toml (NEEDED - project dependencies)
# - uv.lock (NEEDED - locked dependencies)
```

**Result**: Build context includes necessary files ✓

---

## Issue 3: Environment Variable Syntax

### ❌ BEFORE (Dockerfile)
```dockerfile
ATLAS_SERVER_HOST=${ATLAS_SERVER_HOST:-localhost}
ATLAS_SERVER_PORT=${ATLAS_SERVER_PORT:-21000}
```

**Error Output**:
```
UndefinedVar: Usage of undefined variable '$ATLAS_SERVER_HOST' (line 45)
UndefinedVar: Usage of undefined variable '$ATLAS_SERVER_PORT' (line 45)
```

### ✅ AFTER (Dockerfile)
```dockerfile
ATLAS_SERVER_HOST=localhost
ATLAS_SERVER_PORT=21000
```

**Result**: No undefined variable warnings ✓

---

## Issue 4: Virtual Environment Not Receiving Dependencies

### ❌ BEFORE (Builder Stage)
```dockerfile
FROM base AS builder
RUN uv venv /opt/venv
RUN uv sync --frozen
```

**Problem**: uv sync creates .venv instead of using /opt/venv

**Result**:
```
ModuleNotFoundError: No module named 'apache_atlas'
```

### ✅ AFTER (Builder Stage)
```dockerfile
FROM base AS builder
WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN /root/.local/bin/uv venv /opt/venv --python python3.13
RUN /root/.local/bin/uv pip compile pyproject.toml > /tmp/requirements.txt && \
    /root/.local/bin/uv pip install --python /opt/venv/bin/python -r /tmp/requirements.txt
```

**Result**: All modules available in venv ✓

---

## Issue 5: ENTRYPOINT Can't Use 'uv' in Runtime

### ❌ BEFORE (Dockerfile)
```dockerfile
ENTRYPOINT ["uv", "run", "python", "scb_dp_cli.py", "ingest"]
```

**Problem**: uv is only installed in builder stage, not in runtime

**Result**:
```
docker: Error response from daemon: 
OCI runtime create failed: exec: "uv": executable file not found in $PATH
```

### ✅ AFTER (Dockerfile)
```dockerfile
ENTRYPOINT ["/opt/venv/bin/python", "scb_dp_cli.py", "ingest"]
```

**Result**: Python from venv executes correctly ✓

---

## Complete Comparison

| Aspect | Before | After |
|--------|--------|-------|
| **Casing** | from/as (lowercase) | FROM/AS (uppercase) |
| **pyproject.toml** | Excluded | Included |
| **uv.lock** | Excluded | Included |
| **Env vars** | Bash expansion | Simple assignment |
| **Builder venv** | Creates .venv | Uses /opt/venv |
| **ENTRYPOINT** | Uses missing uv | Uses venv python |
| **Build status** | FAILS | SUCCEEDS |
| **CLI works** | No | Yes |
| **Modules loaded** | ImportError | All available |

---

## Test Results

### Before Fixes
- ❌ Docker build FAILED
- ❌ Build context missing files
- ❌ Multiple warnings/errors
- ❌ CLI not functional

### After Fixes
- ✅ Docker build SUCCESSFUL
- ✅ All files included in context
- ✅ No warnings/errors
- ✅ CLI works perfectly
- ✅ All dependencies available
- ✅ Ready for Kubernetes deployment

---

## Key Changes Summary

| File | Changes |
|------|---------|
| **Dockerfile** | 1. FROM/AS uppercase, 2. Builder stage corrected, 3. Env vars fixed, 4. ENTRYPOINT updated, 5. HEALTHCHECK path fixed |
| **.dockerignore** | Removed pyproject.toml and uv.lock exclusions |

---

## How to Verify

```bash
cd docker-k8s
eval $(minikube docker-env)
docker build -t scb-ingestion:latest .
docker run --rm scb-ingestion:latest --help
```

Expected result:
```
usage: scb_dp_cli.py ingest [-h] [--dry-run] [--strict] workbook
```

---

## Key Learnings

1. Docker Keywords: Always use uppercase FROM, AS, RUN, etc.
2. .dockerignore: Be careful what you exclude
3. Multi-stage builds: Copy everything needed to each stage
4. Virtual environments: Explicitly specify paths with uv
5. Docker shell: Uses /bin/sh, not bash - no process substitution
6. Environment variables: Docker doesn't support bash parameter expansion

