# 🔧 Troubleshooting 503 Service Unavailable - Atlas

When you see:
```
HTTP ERROR 503 Service Unavailable
```

This guide helps you diagnose and fix it without `kubectl`.

**⚠️ If pod failed to start:** See **CONTAINER_FAILED_TO_START.md** for detailed container error diagnostics.

---

## 🎯 Quick Checks (No kubectl Required)

### 1. **Is Atlas Pod Actually Running?** (Kyma Dashboard)

**In Kyma Dashboard:**
- Go to **Workloads** → **Deployments** → find `atlas`
- Check **READY** column:
  - ✅ `1/1` = Pod is running
  - ❌ `0/1` = Pod is NOT ready or crashed
  - ⏳ `0/1` pending = Still starting

**If NOT 1/1:**
1. Click the deployment name
2. Go to **Pods** tab
3. Click the pod name
4. Check **Status**:
   - `Pending` → waiting for resources
   - `CrashLoopBackOff` → see logs (below)
   - `OOMKilled` → increase memory in deployment
   - `ImagePullBackOff` → image not available

---

### 2. **Check Pod Logs** (Kyma Dashboard)

**To see why Atlas crashed:**
1. **Workloads** → **Deployments** → `atlas`
2. Click pod name
3. **Logs** tab (or **Containers** → your pod → **Logs**)
4. Look for errors like:
   - `OutOfMemory` → increase memory limits in deployment
   - `Connection refused` → database connectivity issue
   - `Port already in use` → deployment conflict

---

### 3. **Verify Service Endpoint** (Kyma Dashboard)

**In Kyma Dashboard:**
- Go to **Services** → find `atlas`
- Check **Endpoints** section:
  - ❌ **No endpoints** = no running pods match selector
  - ✅ Shows IP addresses = service is connected

---

### 4. **Wait for Atlas to Start**

Atlas takes **5-10 minutes** on cold start (first deployment).

**Signs it's still starting:**
- Pod status is `Running` but probes not passed yet
- Logs show: `Starting Apache Atlas...`

**Wait and retry:**
```bash
# Try again after 5 minutes
sleep 300
curl http://localhost:23000/
```

---

## 🔍 Diagnostic Steps (Kyma Dashboard)

### Step 1: Check Deployment Status

**Path:** Workloads → Deployments → `atlas`

| Check | Expected | If Wrong |
|-------|----------|----------|
| Ready | 1/1 | Pod failed to start |
| Image | `sburn/apache-atlas:latest` | Wrong image |
| Port | 21000 (internal) | Port mismatch |
| Memory | 2Gi requested, 4Gi limit | OOMKilled if too low |
| Probes | Commented out | Can't fail if disabled |

---

### Step 2: Check Pod Details

**Path:** Deployments → `atlas` → Pods → click pod

| Section | Check |
|---------|-------|
| **Status** | Should be `Running` |
| **Containers** | Should show `atlas-server` + `istio-proxy` |
| **Logs** | Look for startup messages |
| **Events** | Recent warnings/errors |

---

### Step 3: Check Service Port Mapping

**Path:** Network → Services → `atlas`

| Check | Expected |
|-------|----------|
| Port | 23000 (external) |
| Target Port | 21000 (internal) |
| Protocol | TCP |
| Endpoints | At least 1 IP shown |

---

### Step 4: Check Persistent Volumes

**Path:** Storage → Persistent Volume Claims

| PVC | Status | If Wrong |
|-----|--------|----------|
| `atlas-claim0` | Bound | Pending = storage not available |
| `atlas-claim1` | Bound | Pending = storage not available |

If `Pending`:
- Storage class may not be provisioned in your Kyma environment
- Contact SAP BTP admin to enable persistent storage

---

## 🛠️ Common Causes & Fixes

### Cause 1: Atlas Not Started Yet ⏳
**Symptom:** Pod shows `Running` but 503 error persists

**Fix:**
- Wait 5-10 minutes for cold start
- Check logs for startup progress
- Retry: `curl http://localhost:23000/`

---

### Cause 2: Pod Crashed (CrashLoopBackOff) 💥

**Fix: Check Logs**
1. Deployments → `atlas` → Pods
2. Click pod → **Logs** tab
3. Look for:

**If you see `OutOfMemory`:**
- Edit deployment YAML
- Increase `resources.requests.memory` and `resources.limits.memory`
- Common fix: `4Gi` → `8Gi`

**If you see database connection error:**
- Atlas can't reach Elasticsearch/HBase backend
- Usually embedded in `sburn/apache-atlas:latest` image
- Check if pod has network access

---

### Cause 3: No Running Pods (0/1) 🚫

**Fix:**
1. Deployments → `atlas`
2. Edit YAML
3. Check:
   - `spec.replicas: 1` (should not be 0)
   - Selector matches pod labels
   - Resource requests/limits reasonable for your cluster

---

### Cause 4: Port Forwarding Not Working 🔌

**If you're using port-forward from terminal:**
```bash
# Check if port-forward is still running
# Kill and restart
kubectl port-forward svc/atlas 23000:23000 &

# Verify it's listening
lsof -i :23000
```

**For Kyma on BTP without kubectl:**
- Use APIRule + Kyma ingress instead of port-forward
- See: KYMA_DASHBOARD_TROUBLESHOOTING.md

---

### Cause 5: Service Not Exposing Pod 🔗

**In Kyma Dashboard:**
1. Services → `atlas`
2. Check **Endpoints**:
   - If empty: pod selector not matching
   - If showing IPs: service is OK

**If no endpoints:**
1. Edit service YAML
2. Check `spec.selector.io.kompose.service: atlas` matches pod labels
3. Check port `23000` → `21000` mapping is correct

---

## ✅ Verification Checklist

After troubleshooting:

- [ ] Pod status shows `Running` (1/1 ready)
- [ ] Logs show successful startup (look for "Started")
- [ ] Service shows at least 1 endpoint
- [ ] PVCs are `Bound` (not Pending)
- [ ] `curl http://localhost:23000/` returns 401 (not 503) ← **GOOD!**

---

## 🎯 Expected vs Actual Responses

### ❌ Bad Responses
```
HTTP ERROR 503 Service Unavailable
```
→ Service not ready, see above troubleshooting

### ✅ Good Responses
```
HTTP/1.1 401 Unauthorized
<html>...<title>Login Page</title>...
```
→ Atlas is running! Login works: admin/admin

### ✅ Even Better
```
HTTP/1.1 200 OK
<html>...<title>Atlas Home</title>...
```
→ Fully ready for entity creation

---

## 🚀 Next Steps After Fixing 503

Once you get **401 Unauthorized** or **200 OK**:

1. **Login to Atlas UI**
   - http://localhost:23000
   - Username: admin
   - Password: admin

2. **Create entities**
   ```bash
   uv run python create_entities_with_pydantic.py
   ```

3. **Search for entities**
   - Atlas UI → Search tab
   - Filter by type: SCB_Database, SCB_Table, etc.

---

## 📊 Dashboard View Quick Reference

| What You Need | Path | What to Look For |
|---------------|------|------------------|
| Pod Status | Workloads → Deployments → atlas | READY: 1/1 |
| Pod Logs | Deployments → atlas → Pods → [pod] → Logs | "Started" or errors |
| Service Health | Network → Services → atlas | Endpoints section |
| Storage | Storage → PVCs → atlas-claim* | Status: Bound |
| Resource Usage | Workloads → Deployments → atlas → Metrics | Memory/CPU |

---

## ❓ Still Stuck?

If 503 persists after these checks:

1. **Confirm you're on Kyma SAP BTP**
   - Check cluster name in Dashboard
   - Kyma services might have different networking setup

2. **Check if Atlas pod exists at all**
   - Workloads → Deployments
   - Search for "atlas"
   - If not found: deployment may not be applied

3. **Redeploy from scratch**
   ```bash
   # Delete old deployment
   kubectl delete deployment atlas
   
   # Reapply from YAML
   kubectl apply -f apache-atlas/atlas-deployment.yaml
   kubectl apply -f apache-atlas/atlas-service.yaml
   
   # Wait 5-10 minutes
   ```

4. **Contact cluster admin**
   - SAP BTP may have different resource limits
   - Storage classes may not be configured
   - Network policies may block traffic

---

## 📚 Related Docs

- **KYMA_DASHBOARD_TROUBLESHOOTING.md** - General Kyma diagnostics
- **CREATE_ENTITIES_QUICK_START.md** - Creating entities after fix
- **DEPLOYMENT_CHECKLIST.md** - Initial deployment steps
- **ATLAS_SETUP_GUIDE.md** - Atlas detailed setup


