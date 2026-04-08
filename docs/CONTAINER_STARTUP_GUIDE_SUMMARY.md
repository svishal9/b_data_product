# 🆘 CONTAINER FAILED TO START - TROUBLESHOOTING GUIDE CREATED

## What Happened

Your Atlas container failed to start. This means the pod is in error state (likely `CrashLoopBackOff`, `OOMKilled`, `ImagePullBackOff`, or `Pending`).

---

## 📁 Resources Created For You

### **CONTAINER_FAILED_TO_START.md** (Comprehensive Guide)
**Location:** `/Users/vishal/IdeaProjects/scb-data-product/docs/CONTAINER_FAILED_TO_START.md`

This guide covers:

✅ **5 Most Common Container Failures:**
1. ❌ **OutOfMemory (OOMKilled)**
   - Fix: Increase memory limits
   - From 4Gi → 8Gi

2. ❌ **ImagePullBackOff**
   - Fix: Pull image manually or use different tag
   - Check network access to Docker Hub

3. ❌ **CrashLoopBackOff**
   - Fix: Check logs for actual error message
   - Common: port conflict, database connection

4. ❌ **Pending (Stuck)**
   - Fix: Check PVCs status, node resources
   - May need admin intervention

5. ❌ **Connection Refused**
   - Fix: Check service endpoints
   - Verify selector labels match

✅ **Step-by-step diagnosis:**
- How to find logs in Kyma Dashboard
- How to match error to fix
- Recovery options if nothing works

---

## 🚀 IMMEDIATE ACTION (5 minutes)

### Step 1: Find the Error
1. Go to **Kyma Dashboard**
2. **Workloads** → **Deployments** → `atlas`
3. Click **Pods** tab → Click the pod → **Logs**
4. **Copy the error message you see**

### Step 2: Match Error to Solution
Find your error message in CONTAINER_FAILED_TO_START.md:
- `OutOfMemory` → Use fix 1
- `ImagePullBackOff` → Use fix 2
- `CrashLoopBackOff` → Use fix 3
- `Pending` → Use fix 4
- `Connection refused` → Use fix 5

### Step 3: Apply Fix
Each fix tells you:
- What to change
- Exact YAML to use
- How to update in Dashboard

### Step 4: Wait & Check
- Wait 5-10 minutes
- Check if pod status is now `1/1 Ready`
- Try: `curl http://localhost:23000/`

---

## 🔍 Most Likely Cause (Atlas Container Specific)

Based on typical Atlas deployments on Kyma:

**#1 MOST LIKELY: OutOfMemory (OOMKilled)**
- Default memory limit (4Gi) is too small for Atlas
- Needs at least 4Gi, 8Gi recommended
- **Fix:** Increase memory in deployment

**#2 LIKELY: Pending (PVC stuck)**
- Storage class not configured on Kyma cluster
- PVCs not getting bound
- **Fix:** Check `atlas-claim0` and `atlas-claim1` status

**#3 POSSIBLE: ImagePullBackOff**
- Docker image can't be pulled
- Cluster may block external image registry
- **Fix:** Check network or use different image tag

---

## 📋 Complete Diagnostic Checklist

Use this if you want to verify everything:

- [ ] **Pod Status Check**
  - Dashboard → Deployments → `atlas` → Check READY column
  - If `0/1`: Pod failed

- [ ] **Pod Logs**
  - Pods → [pod] → Logs tab
  - Copy error message

- [ ] **Pod Status Reason**
  - Pods → [pod] → Status section
  - Look for: Pending / CrashLoopBackOff / OOMKilled / ImagePullBackOff

- [ ] **Memory Check**
  - Deployments → `atlas` → Edit YAML
  - Check `resources.limits.memory`
  - If `4Gi` or less: Likely cause

- [ ] **PVC Check**
  - Storage → Persistent Volume Claims
  - Check `atlas-claim0` and `atlas-claim1`
  - If `Pending`: Storage not available

- [ ] **Service Check**
  - Network → Services → `atlas`
  - Check Endpoints section
  - If empty: Pod selector not matching

---

## 🛠️ Quick Fixes (In Order of Likelihood)

### Fix #1: Increase Memory (Most Likely)

If pod shows `OOMKilled` or memory is `2Gi` / `4Gi`:

1. Dashboard → Deployments → `atlas` → **Edit YAML**
2. Find:
   ```yaml
   resources:
     limits:
       memory: "4Gi"
   ```
3. Change to:
   ```yaml
   resources:
     limits:
       memory: "8Gi"
   ```
4. **Save** → Pod restarts automatically
5. Wait 5-10 minutes

---

### Fix #2: Check PVCs (If Stuck Pending)

If pod shows `Pending` and won't start:

1. Dashboard → Storage → **Persistent Volume Claims**
2. Look for `atlas-claim0` and `atlas-claim1`
3. If status is `Pending` (not `Bound`):
   - Storage class not available
   - Contact SAP BTP admin to enable storage
   - OR: Delete PVCs and redeploy (no persistence)

---

### Fix #3: Fix Image (If ImagePullBackOff)

If pod shows `ImagePullBackOff`:

1. Dashboard → Deployments → `atlas` → **Edit YAML**
2. Find: `image: sburn/apache-atlas:latest`
3. Change to: `image: sburn/apache-atlas:2.3.1-hadoop3`
4. **Save** → Pod restarts
5. Wait 5-10 minutes

---

## ✅ Success Indicators

After applying fix, you should see:

**Pod Logs show:**
```
Starting Apache Atlas...
[INFO] Atlas started successfully
```

**Pod Status shows:**
- Ready: `1/1` ✓
- Status: `Running` ✓
- Restarts: `0` ✓

**Then test:**
```bash
curl http://localhost:23000/
# Expected: HTTP/1.1 401 Unauthorized (good!)
```

---

## 🎯 If Still Failing

Try recovery options in CONTAINER_FAILED_TO_START.md:

1. **Restart Deployment**
   - Dashboard → Deployments → `atlas` → Menu → **Restart**

2. **Delete and Redeploy**
   - Delete deployment
   - Reapply from YAML

3. **Check Minimal Requirements**
   - Memory: 4Gi minimum
   - CPU: 1 core minimum
   - Storage: Must be available
   - Network: Must reach Docker Hub

---

## 📞 When to Provide More Info

If the guide doesn't solve it, come back with:

1. **Exact error from logs** (copy-paste)
2. **Pod status** (Pending? CrashLoopBackOff? etc.)
3. **Memory limit** (from Edit YAML)
4. **PVC status** (Bound or Pending?)

---

## 🔗 Documentation Updated

Files now reference the new guide:
- ✅ **CREATE_ENTITIES_QUICK_START.md** - Added container failure section
- ✅ **TROUBLESHOOT_503_ERROR.md** - Added reference to container diagnostics
- ✅ **CONTAINER_FAILED_TO_START.md** - Complete diagnostic guide (NEW)

---

## 🚀 Next Immediate Steps

1. **Open Kyma Dashboard NOW**
2. **Go to:** Workloads → Deployments → `atlas` → Pods
3. **Copy the error from Logs tab**
4. **Open:** `/docs/CONTAINER_FAILED_TO_START.md`
5. **Find your error** in the guide (search for keywords)
6. **Apply the corresponding fix**
7. **Wait 5-10 minutes**
8. **Check if pod is now Ready 1/1**

---

**You've got this! The fix is usually just increasing memory.** 💪


