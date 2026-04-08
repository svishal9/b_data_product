# ✅ 503 ERROR TROUBLESHOOTING - COMPLETE GUIDE CREATED

## What Was Done

You're getting a **503 Service Unavailable** error when trying to access Atlas. I've created a complete troubleshooting guide.

---

## 📁 New Resources Created

### 1. **TROUBLESHOOT_503_ERROR.md** (New Comprehensive Guide)
**Location:** `/Users/vishal/IdeaProjects/scb-data-product/docs/TROUBLESHOOT_503_ERROR.md`

This guide includes:

✅ **Kyma Dashboard-only checks** (no kubectl needed):
- Pod status verification (1/1 Ready?)
- Pod logs inspection
- Service endpoint validation
- Storage volume status
- Memory/CPU usage checks

✅ **Common causes & fixes:**
- Pod still starting (wait 5-10 min)
- Pod crashed (check logs for OOMKilled, errors)
- No running pods (replicas = 0?)
- PVCs stuck in Pending (storage not available)
- Port forwarding issues

✅ **Diagnostic workflow:**
- Check Deployment status
- Check Pod details
- Check Service port mapping
- Check PersistentVolumes

✅ **Quick reference table:**
- Dashboard paths for each check
- Expected values
- What to do if wrong

✅ **Expected vs actual responses:**
- ❌ 503 = Service not ready
- ✅ 401 = Atlas running (good!)
- ✅ 200 = Fully ready

---

### 2. **CREATE_ENTITIES_QUICK_START.md** (Updated)
**Location:** `/Users/vishal/IdeaProjects/scb-data-product/docs/CREATE_ENTITIES_QUICK_START.md`

Added/Updated:
- ✅ New "503 Service Unavailable" troubleshooting section
- ✅ Reference to TROUBLESHOOT_503_ERROR.md
- ✅ Quick Kyma Dashboard checks
- ✅ Wait-and-retry instructions
- ✅ Expected response guidance (401 = good!)
- ✅ File Reference table updated
- ✅ Support section updated

---

## 🚀 Immediate Next Steps

### Step 1: Check Your Pod Status (No kubectl!)

**In Kyma Dashboard:**
1. Go to **Workloads** → **Deployments** → `atlas`
2. Look at the **READY** column
   - ✅ `1/1` = Pod is running → try curl again
   - ⏳ `0/1` = Pod not ready → see below
   - ❌ `0/1 pending` = Not enough resources

---

### Step 2: Check Pod Logs (If 0/1)

**In Kyma Dashboard:**
1. Deployments → `atlas`
2. Click **Pods** tab
3. Click the pod name
4. Go to **Logs** tab
5. Look for error messages:

**If you see `Started` or `Running`:**
- Pod is OK, just not ready yet
- Wait 5 more minutes
- Try curl again

**If you see errors:**
- `OutOfMemory` → increase memory limit
- `Connection refused` → network issue
- `ImagePullBackOff` → container image not available

---

### Step 3: Wait & Retry

Atlas takes **5-10 minutes on cold start**.

```bash
sleep 300  # Wait 5 minutes

# Try again
curl http://localhost:23000/

# Expected response if ready:
# HTTP/1.1 401 Unauthorized   ← This means Atlas is running!
```

---

## 📊 Kyma Dashboard Quick Reference

| What to Check | Where | What to Look For |
|---------------|-------|-----------------|
| **Pod Running?** | Workloads → Deployments → atlas | READY: 1/1 |
| **Logs** | Deployments → atlas → Pods → [pod] → Logs | "Running" or errors |
| **Service Connected?** | Network → Services → atlas | Endpoints section |
| **Storage Available?** | Storage → PVCs | Status: Bound |

---

## ✅ Response Guide

### ❌ Still Getting 503?
This means Atlas isn't ready. Check:
1. Pod status = 1/1 ready?
2. Pod logs = any errors?
3. Service endpoints = any IPs showing?
4. Wait longer (maybe only 2 minutes in)?

### ✅ Getting 401 Unauthorized?
**Great! Atlas is running.** This is the expected response.
- Login: admin/admin
- Run: `uv run python create_entities_with_pydantic.py`

---

## 📚 Documentation Files Updated

1. **CREATE_ENTITIES_QUICK_START.md** - Updated troubleshooting section
2. **TROUBLESHOOT_503_ERROR.md** - New comprehensive guide
3. **ENTITY_CREATION_CORRECTIONS.md** - Earlier fixes (wrong script names, imports)

---

## 🎯 Your Workflow Now

```bash
# 1. Wait for Atlas to be ready (check Kyma Dashboard)
# Dashboard: Workloads → Deployments → atlas (check READY = 1/1)

# 2. Once READY = 1/1, test connectivity
curl http://localhost:23000/
# Expected: HTTP/1.1 401 Unauthorized (that's OK!)

# 3. If still 503, check pod logs in Kyma Dashboard
# Dashboard: Deployments → atlas → Pods → [pod] → Logs

# 4. Once you get 401, run entity creation
uv run python create_entities_with_pydantic.py

# 5. Access Atlas UI
# Browser: http://localhost:23000
# Login: admin/admin
```

---

## 🔗 Links to New Resources

**Read Next:**
- Full troubleshooting guide: `/docs/TROUBLESHOOT_503_ERROR.md`
- Entity creation guide: `/docs/CREATE_ENTITIES_QUICK_START.md`

**For Script Issues:**
- Correction summary: `/docs/ENTITY_CREATION_CORRECTIONS.md`

---

## 💡 Remember

- **503 = Not ready yet** (usually just needs time)
- **401 = Atlas is ready** (good to go!)
- **5-10 min wait** on cold start is normal
- **Check Kyma Dashboard** without needing kubectl
- **Logs are your friend** → Deployments → Pods → Logs tab

---

Good luck! Let me know if you hit any other issues. 🚀


