# ✅ Entities Not Created - Troubleshooting Guide

## Issues Fixed

I've identified and fixed several issues that were preventing entities from being created:

### 1. ❌ **create_typedef function signature was wrong**
   - **Issue**: Function expected `atlas_client` only, but script passed `type_definitions`
   - **Fix**: Updated function to accept both `type_defs` and `atlas_client` parameters
   - **File**: `scb_atlas/atlas/type_service.py`

### 2. ❌ **Missing return statements**
   - **Issue**: Entity creation functions didn't return True/False
   - **Fix**: Added return statements to all entity creation functions
   - **File**: `scb_atlas/atlas/entity_service.py`

### 3. ❌ **Poor error handling in script**
   - **Issue**: Errors were being swallowed silently
   - **Fix**: Added verbose logging and error tracking
   - **File**: `create_atlas_entities.py`

---

## 🚀 How to Test the Fix

### Step 1: Run the Diagnostic Script
```bash
cd /Users/vishal/IdeaProjects/scb-data-product
uv run python tests/manual/diagnose_atlas.py
```

This will test:
- ✅ Atlas connection
- ✅ Type definitions loading
- ✅ Type creation
- ✅ Entity creation
- ✅ Entity search

### Step 2: Run the Fixed Creation Script
```bash
uv run python create_atlas_entities.py
```

This should now:
- ✅ Connect to Atlas
- ✅ Create type definitions
- ✅ Create all sample entities
- ✅ Report success

### Step 3: Verify in Atlas UI
1. Open: http://localhost:23000
2. Login: admin/admin
3. Go to Search tab
4. Advanced Search
5. Entity Type: `SCB_Database`
6. Click Search
7. You should see `finance_db`

---

## 🔍 What to Check

### If Entities Still Don't Appear

**Check 1: Is Atlas Running?**
```bash
curl -i http://localhost:23000
# Should return HTTP/1.1 401 Unauthorized
```

**Check 2: Are Types Created?**
```bash
# Search for SCB_Database type in Atlas UI
# Go to Admin → Types
```

**Check 3: Check Atlas Logs**
```bash
# Docker
docker logs atlas_server

# Kubernetes
kubectl logs -l io.kompose.service=atlas -f
```

**Check 4: Wait for Indexing**
- Atlas may take 5-10 seconds to index new entities
- Refresh the UI (F5)
- Try searching again

### If You Get Connection Errors

```bash
# Test Atlas connectivity
curl -v http://localhost:23000

# Test with authentication
curl -u admin:admin http://localhost:23000

# Check if port is open
netstat -tuln | grep 23000
```

---

## 🛠️ Manual Testing

### Test Connection Only
```text
from scb_atlas.atlas.atlas_client import create_atlas_client

atlas_client = create_atlas_client()
print("✅ Connected successfully!")
```

### Test Type Creation Only
```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.type_service import create_typedef
from scb_atlas.atlas.atlas_types import type_definitions

atlas_client = create_atlas_client()
result = create_typedef(type_definitions, atlas_client)
print("✅ Types created!")
print(f"Result: {result}")
```

### Test Database Entity Creation Only
```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.entity_service import create_database_entity

atlas_client = create_atlas_client()
create_database_entity(
    atlas_client,
    "test_db",
    "hdfs://test",
    "Test database"
)
print("✅ Database created!")
```

---

## 📊 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Connection refused | Atlas not running | Start Atlas with `docker-compose up -d` |
| Auth failed | Wrong credentials | Use admin/admin (default) |
| Entity not visible | Not indexed yet | Wait 5-10 seconds, refresh UI |
| Type doesn't exist | Types not created | Run type creation first |
| Silent failure | Error not logged | Check diagnose_atlas.py output |
| Port already in use | Port 23000 taken | Change port or kill process |

---

## ✅ Step-by-Step Resolution

### Step 1: Verify Atlas is Running
```bash
docker ps | grep atlas
# Should show running atlas container
```

### Step 2: Run Diagnostic
```bash
uv run python tests/manual/diagnose_atlas.py
# Should show all ✅ marks
```

### Step 3: Create Entities
```bash
uv run python create_atlas_entities.py
# Should complete without errors
```

### Step 4: Verify in UI
```
1. Open http://localhost:23000
2. Login with admin/admin
3. Search → Advanced Search
4. Entity Type: SCB_Database
5. Should find finance_db
```

---

## 🔍 Detailed Troubleshooting

### Issue: "Failed to connect to Atlas"

**Check these:**
```bash
# 1. Is Atlas running?
docker ps | grep atlas

# 2. Is port 23000 open?
netstat -tuln | grep 23000

# 3. Can you ping it?
curl http://localhost:23000

# 4. Are credentials correct?
curl -u admin:admin http://localhost:23000
```

**If still failing:**
- Stop Atlas: `docker-compose down`
- Start Atlas: `docker-compose up -d`
- Wait 30 seconds
- Try again

### Issue: "Type creation failed"

**Check these:**
```bash
# 1. Are types already there?
# Go to Admin → Types in Atlas UI

# 2. Check error message for details
# Run: uv run python tests/manual/diagnose_atlas.py

# 3. Check Atlas logs
docker logs atlas_server | grep -i type
```

### Issue: "Entities created but not visible"

**This is normal!** Do this:

```bash
# 1. Wait 10 seconds (indexing)
sleep 10

# 2. Refresh Atlas UI (F5 or Cmd+R)

# 3. Search again
# Advanced Search → Entity Type: SCB_Database

# 4. If still not visible:
# Wait another 10 seconds and try "refresh" button in Atlas UI
```

---

## 📋 Verification Commands

### Check Types Exist
```bash
# In Python terminal
from scb_atlas.atlas.atlas_client import create_atlas_client
atlas_client = create_atlas_client()
exists = atlas_client.typedef.type_with_name_exists("SCB_Database")
print(f"SCB_Database exists: {exists}")
```

### Count Entities
```bash
# Search for all entities of type
results = atlas_client.entity.get_entities_by_attribute(
    "SCB_Database",
    [{"database_name": "finance_db"}]
)
print(f"Found {len(results.get('entities', []))} entities")
```

### Check Entity GUID
```bash
# If entity was created, it has a GUID
from scb_atlas.atlas.discovery_service import dsl_search

results = dsl_search(atlas_client, ["finance_db"], "SCB_Database")
if results:
    print(f"GUID: {results[0]['guid']}")
    print(f"Attributes: {results[0]['attributes']}")
```

---

## 🎯 Quick Resolution Checklist

- [ ] Atlas is running on port 23000
- [ ] Can access http://localhost:23000
- [ ] Can login with admin/admin
- [ ] Run `uv run python tests/manual/diagnose_atlas.py`
- [ ] All checks pass ✅
- [ ] Run `uv run python create_atlas_entities.py`
- [ ] Script completes successfully
- [ ] Wait 10 seconds for indexing
- [ ] Refresh Atlas UI (F5)
- [ ] Search for entities
- [ ] Entities appear in results ✅

---

## 📞 Still Having Issues?

1. **Run diagnostic script first:**
   ```bash
   uv run python tests/manual/diagnose_atlas.py
   ```

2. **Check the output for which step fails**

3. **Review the solution for that specific issue above**

4. **If still stuck:**
   - Check Atlas logs: `docker logs atlas_server`
   - Restart Atlas: `docker-compose restart`
   - Try again

---

## ✅ Next Steps

Now that the issues are fixed:

1. Run the diagnostic script
2. Run the creation script
3. Check Atlas UI
4. Entities should now appear!

**If you still have issues, run:**
```bash
uv run python tests/manual/diagnose_atlas.py 2>&1 | tee diagnostic_output.txt
```

And share the output for detailed analysis.

