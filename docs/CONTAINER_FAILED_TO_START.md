# 🔴 CONTAINER FAILED TO START - DIAGNOSTIC GUIDE

## Immediate: Find the Error Message

The container failure reason is in the Kyma Dashboard logs. Follow these steps **exactly**:

---

## 🎯 Step-by-Step Diagnosis (Kyma Dashboard)

### Step 1: Go to Pod Logs

**Path:** Workloads → Deployments → `atlas` → Pods → [pod name] → **Logs**

This is where you'll see WHY the container failed.

---

## 🔍 Common Container Failures & Fixes

Based on typical Atlas container issues, here are the most common failures:

### ❌ Failure 1: OutOfMemory (OOMKilled)

**Log shows:** `OutOfMemory` or `OOMKilled`

**Cause:** Container doesn't have enough memory. Atlas needs more than the default.

**Fix:**
1. Dashboard → Deployments → `atlas` → **Edit YAML**
2. Find `resources:` section
3. Change `limits.memory` and `requests.memory`:

**Current (likely too small):**
```yaml
resources:
  requests:
    memory: "2Gi"
    cpu: "500m"
  limits:
    memory: "4Gi"
    cpu: "2"
```

**Change to:**
```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "1"
  limits:
    memory: "8Gi"
    cpu: "2"
```

4. Click **Save/Update**
5. Pod will restart automatically
6. Wait 5-10 minutes for startup
7. Check logs again

---

### ❌ Failure 2: ImagePullBackOff

**Log shows:** `ImagePullBackOff` or `Failed to pull image`

**Cause:** Container image (`sburn/apache-atlas:latest`) can't be downloaded

**Fix:**

Option 1: Check image exists
1. Try pulling manually:
   ```bash
   docker pull sburn/apache-atlas:latest
   ```

Option 2: Use a different image tag
1. Dashboard → Deployments → `atlas` → **Edit YAML**
2. Find: `image: sburn/apache-atlas:latest`
3. Try: `image: sburn/apache-atlas:2.3.1-hadoop3`
4. Save and let pod restart

Option 3: Check network access
- Kyma cluster may need internet access to Docker Hub
- Contact SAP BTP admin if blocked

---

### ❌ Failure 3: CrashLoopBackOff

**Log shows:** `CrashLoopBackOff` or container keeps restarting

**Cause:** Container starts but crashes immediately

**Fix - Check the actual error in logs:**

1. Dashboard → Deployments → `atlas` → Pods → [pod] → **Logs**
2. Look for error messages in the startup output
3. Common errors:

**If you see "Port already in use":**
- Another Atlas is running
- Delete old pod: Pods → [old pod] → **Delete**

**If you see "Cannot connect to database":**
- Atlas tries to connect to backend (HBase/Cassandra)
- Embedded image should have it, but may fail if no storage
- Check PVCs status (below)

**If you see Java/Heap errors:**
- Increase memory (see OutOfMemory fix above)

---

### ❌ Failure 4: Pending (Stuck Starting)

**Pod status:** `Pending` (not even trying to start)

**Cause:** Not enough resources or PVCs not bound

**Fix:**

1. **Check PVCs first:**
   - Dashboard → Storage → **Persistent Volume Claims**
   - Look for `atlas-claim0` and `atlas-claim1`
   - If status is `Pending` (not `Bound`):
     - Storage class not configured
     - Contact SAP BTP admin
     - Or delete PVCs and redeploy without persistence

2. **Check Node Resources:**
   - Dashboard → Workloads → **Nodes** (if visible)
   - If all nodes show high CPU/memory usage:
     - Not enough cluster capacity
     - Contact admin

---

### ❌ Failure 5: Connection Refused

**Log shows:** `Connection refused` or `Cannot reach service`

**Cause:** Service not available or port mapping wrong

**Fix:**
1. Check Service exists:
   - Dashboard → Network → **Services** → `atlas`
   - Should show **Endpoints** with at least 1 IP
   
2. If no endpoints:
   - Pod selector not matching
   - Dashboard → Deployments → `atlas` → **Edit YAML**
   - Verify labels match selector
   - Default should be: `io.kompose.service: atlas`

---

## 🛠️ How to Find Your Specific Error

### Step 1: Open Pod Logs

1. **Workloads** → **Deployments** → `atlas`
2. Click **Pods** tab
3. Click the pod name
4. Click **Logs** tab
5. **Copy the error message** you see

### Step 2: Match to Solutions Above

Look for keywords in logs:
- `OutOfMemory` → Increase memory
- `ImagePullBackOff` → Fix image
- `CrashLoopBackOff` → Check actual error in logs
- `Connection refused` → Check service
- `Pending` → Check PVCs or resources

### Step 3: Apply Fix

Use the corresponding fix section above.

---

## 🔧 Emergency Recovery Steps

If container won't start no matter what:

### Option 1: Restart Deployment

1. Dashboard → Deployments → `atlas`
2. Click **⋮ (menu)** → **Restart**
3. Deployment will delete old pod and create new one
4. Wait 5-10 minutes

### Option 2: Delete and Redeploy

1. Dashboard → Deployments → `atlas` → **Delete**
2. Wait for deletion to complete
3. Reapply deployment YAML:
   ```bash
   kubectl apply -f apache-atlas/atlas-deployment.yaml
   kubectl apply -f apache-atlas/atlas-service.yaml
   ```
4. Wait 5-10 minutes for startup

### Option 3: Check Minimal Requirements

Atlas needs:
- ✅ Memory: 4Gi minimum (8Gi recommended)
- ✅ CPU: 1 core minimum
- ✅ Storage: If using PVCs, they must be Bound
- ✅ Network: Pod must reach external container registry
- ✅ Time: 5-10 minutes for cold start

---

## ✅ What "Success" Looks Like

**Pod Logs Should Show:**

```
Starting Apache Atlas...
[INFO] ... Atlas started successfully
[INFO] ... Server started on port 21000
```

**Pod Status Should Be:**
- Running ✓
- Ready 1/1 ✓
- Restarts: 0 ✓

**Service Should Show:**
- At least 1 endpoint IP ✓
- Port 23000 → 21000 mapping ✓

---

## 📋 Quick Diagnostic Checklist

Go through these in Kyma Dashboard:

- [ ] Open Deployments → `atlas` → check READY column
- [ ] If not 1/1, click Pods → click pod → open Logs
- [ ] Copy error from logs
- [ ] Match error to solutions above (OutOfMemory, ImagePullBackOff, etc.)
- [ ] Apply corresponding fix
- [ ] Wait 5 minutes
- [ ] Check pod status again
- [ ] Repeat until READY shows 1/1
- [ ] Then test: `curl http://localhost:23000/`

---

## 🆘 If You're Still Stuck

**Please provide:**

1. **Pod status** - Is it: Pending / CrashLoopBackOff / Running but 0/1?
2. **Error from logs** - Copy-paste the error message you see
3. **Current memory limit** - What does resources.limits.memory show?
4. **PVC status** - Are `atlas-claim0` and `atlas-claim1` Bound or Pending?

This will help me give you the exact fix.

---

## 🎯 Next Actions

1. **Go to Kyma Dashboard now**
2. **Navigate to:** Workloads → Deployments → `atlas` → Pods → [pod] → Logs
3. **Find the error message**
4. **Match it to a failure type above (1-5)**
5. **Apply the corresponding fix**
6. **Wait 5-10 minutes**
7. **Check if pod status is now 1/1**

If it worked → test `curl http://localhost:23000/`

If still failing → come back with the error message you're seeing.


