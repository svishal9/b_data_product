# 🚀 CREATE ENTITIES IN LOCAL ATLAS - COMPLETE GUIDE

## Quick Summary

You can create all entities in a local Atlas instance (port 23000) in just 3 steps:

```bash
# Step 1: Ensure Atlas is running (port 23000)
# Step 2: Run the setup script
uv run python create_entities_with_pydantic.py

# Step 3: Access Atlas UI
# Open: http://localhost:23000 (admin/admin)
```

---

## 📋 Complete Setup Instructions

### Prerequisites

1. **Atlas running on port 23000**
   ```bash
   # Docker option
   docker-compose up -d
   
   # Kubernetes option
   kubectl port-forward svc/atlas 23000:23000
   ```

2. **Verify Atlas is accessible**
   ```bash
   curl http://localhost:23000
   # Should return: HTTP/1.1 401 Unauthorized (that's OK)
   ```

3. **Python dependencies installed**
   ```bash
   # Already installed if you have uv
   uv sync
   ```

---

## 🚀 Create All Entities (Automated)

### Method 1: Using Setup Script (Recommended)

```bash
cd /Users/vishal/IdeaProjects/scb-data-product
bash setup_atlas.sh
```

### Method 2: Using Python Directly

```bash
cd /Users/vishal/IdeaProjects/scb-data-product
uv run python create_entities_with_pydantic.py
```

### What Gets Created

✅ **Type Definitions** (5 types)
- SCB_Database
- SCB_Table
- SCB_Column
- SCB_Process
- SCB_DataProduct

✅ **Sample Entities**
- 1 Database (finance_db)
- 3 Tables (trades, transactions, daily_summary)
- 15 Columns (across all tables)
- 2 Processes (daily_trade_aggregation, transaction_validation)
- 1 Data Product (Finance Trading Data Product)

---

## 🌐 Access Atlas UI

### Login to Atlas

1. Open: **http://localhost:23000**
2. Username: **admin**
3. Password: **admin**

### Find Your Entities

1. Click **Search** tab
2. Click **Advanced Search**
3. Select **Entity Type** dropdown
4. Choose from:
   - `SCB_Database`
   - `SCB_Table`
   - `SCB_Column`
   - `SCB_Process`
   - `SCB_DataProduct`

### View Entity Details

- Click any entity in results
- View properties, lineage, schema, relationships
- Explore data flow connections

---

## 🛠️ Create Custom Entities (Manual)

### Create Database

```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.entity_service import create_database_entity

atlas_client = create_atlas_client()

create_database_entity(
    atlas_client,
    database_name="my_database",
    location_uri="hdfs://data/my_database",
    description="My custom database"
)
```

### Create Table

```text
from scb_atlas.atlas.entity_service import create_table_entity

create_table_entity(
    atlas_client,
    table_name="my_table",
    database_name="my_database",
    table_type="EXTERNAL",
    description="My table"
)
```

### Create Columns

```text
from scb_atlas.atlas.entity_service import create_column_entity

create_column_entity(
    atlas_client,
    column_name="id",
    data_type="bigint",
    table_name="my_database.my_table",
    comment="Primary key identifier",
    position=1
)

create_column_entity(
    atlas_client,
    column_name="name",
    data_type="string",
    table_name="my_database.my_table",
    comment="Entity name",
    position=2
)
```

### Create Process

```text
from scb_atlas.atlas.entity_service import create_process_entity_advanced
import time

create_process_entity_advanced(
    atlas_client,
    process_name="data_transformation",
    query_id="proc_transform_001",
    query_text="SELECT * FROM my_table WHERE status = 'ACTIVE'",
    user_name="data_team",
    start_time=int(time.time() * 1000),
    end_time=int(time.time() * 1000) + 3600000
)
```

### Create Data Product

```text
from datetime import date
from scb_atlas.atlas.metadata_models import (
    CompleteDataProductModel,
    DataProductBasicMetadata,
    DataProductBusinessMetadata,
    DataProductClassification,
    LifecycleStatusEnum,
)
from scb_atlas.atlas.service.entity_service import create_data_product_from_model

data_product_model = CompleteDataProductModel(
    basic_metadata=DataProductBasicMetadata(
        data_product_name="My Data Product",
        description="My sample data product",
        data_product_category="Source-Aligned"
    ),
    business_metadata=DataProductBusinessMetadata(
        business_purpose="Sales order tracking",
        gcfo_owner_name="Data Team",
        gcfo_owner_contact="datasteam@company.com"
    ),
    classification=DataProductClassification(
        sensitivity="Internal",
        personal=False
    )
)

create_data_product_from_model(atlas_client, data_product_model)
```

---

## 📊 Sample Data Structure Created

```
finance_db (Database at hdfs://data/finance)
│
├─ trades (Table - EXTERNAL)
│  ├─ trade_id (string) - Unique trade identifier
│  ├─ trade_date (date) - Date of trade execution
│  ├─ currency_pair (string) - Currency pair
│  ├─ amount (decimal) - Trade amount
│  ├─ rate (decimal) - Exchange rate
│  └─ settlement_date (date) - Settlement date
│
├─ transactions (Table - MANAGED)
│  ├─ transaction_id (string) - Unique identifier
│  ├─ transaction_date (date) - Transaction date
│  ├─ amount (decimal) - Amount
│  ├─ description (string) - Description
│  └─ status (string) - Status
│
├─ daily_summary (Table - EXTERNAL)
│  ├─ summary_date (date) - Summary date
│  ├─ total_trades (bigint) - Total trades count
│  ├─ total_volume (decimal) - Total volume
│  └─ avg_rate (decimal) - Average rate
│
├─ daily_trade_aggregation (Process)
│  Query: Aggregates trades by date
│  Inputs: finance_db.trades
│  Outputs: finance_db.daily_summary
│
├─ transaction_validation (Process)
│  Query: Finds invalid transactions
│  Inputs: finance_db.transactions
│
└─ Finance Trading Data Product (DataProduct)
   Owner: Finance Data Team
   Category: Source-Aligned
   Sources: Murex, Bloomberg, Internal Systems
```

---

## 🔍 View Entities Programmatically

### Search for Database

```text
from scb_atlas.atlas.discovery_service import dsl_search

databases = dsl_search(
    atlas_client=atlas_client,
    names=["finance_db"],
    type_name="SCB_Database"
)

for db in databases:
    print(f"Database: {db['attributes']['database_name']}")
    print(f"Location: {db['attributes']['locationUri']}")
    print()
```

### Search for Tables

```text
tables = dsl_search(
    atlas_client=atlas_client,
    names=["trades"],
    type_name="SCB_Table"
)

for table in tables:
    print(f"Table: {table['attributes']['table_name']}")
```

### Search for Processes

```text
processes = dsl_search(
    atlas_client=atlas_client,
    names=["daily_trade_aggregation"],
    type_name="SCB_Process"
)

for proc in processes:
    print(f"Process: {proc['attributes']['process_name']}")
```

---

## 🛑 Troubleshooting

### Issue: Container Failed to Start

```
Pod Status: CrashLoopBackOff / ImagePullBackOff / OOMKilled
```

**This means the Atlas container couldn't start.** See **CONTAINER_FAILED_TO_START.md** for detailed diagnostics.

**Quick checks in Kyma Dashboard:**
- Workloads → Deployments → `atlas` → Pods → [pod] → **Logs**
- Look for errors like `OutOfMemory`, `ImagePullBackOff`, or `CrashLoopBackOff`
- Common fixes:
  - Increase memory limit (OutOfMemory)
  - Check image availability (ImagePullBackOff)
  - Check PVC status (Pending storage)

### Issue: Atlas Not Running

```
Error: Failed to connect to Atlas at http://localhost:23000
```

**Solution:**

```bash
# Using Docker
docker-compose up -d

# Using Kubernetes
kubectl get svc
kubectl port-forward svc/atlas 23000:23000

# Verify
curl http://localhost:23000
```

### Issue: 503 Service Unavailable

```
HTTP ERROR 503 Service Unavailable
```

**This means Atlas is not ready yet.** Common causes:

1. **Pod still starting** - Atlas takes 5-10 minutes on cold start
2. **Pod crashed** - Check logs in Kyma Dashboard
3. **No running pods** - Deployment may have 0 replicas
4. **Storage not available** - PVCs may be stuck in Pending

**Solution:**

See **TROUBLESHOOT_503_ERROR.md** for detailed Kyma Dashboard troubleshooting without kubectl.

**Quick checks in Kyma Dashboard:**
- Workloads → Deployments → `atlas` → Check READY column (should be 1/1)
- Click pod → Logs tab → Look for errors
- Network → Services → `atlas` → Check Endpoints (should show at least 1)

**Wait and retry:**
```bash
sleep 300  # Wait 5 minutes
curl http://localhost:23000/
```

Expected response after startup:
```
HTTP/1.1 401 Unauthorized  # ← Good! Atlas is running
```

### Issue: Authentication Failed

```
Error: Authentication failed with credentials admin/admin
```

**Solution:**

Check credentials in environment:
```bash
export ATLAS_USERNAME="admin"
export ATLAS_PASSWORD="admin"
echo $ATLAS_USERNAME
echo $ATLAS_PASSWORD
```

### Issue: Types Don't Exist

```
Error: Type SCB_Database does not exist
```

**Solution:**

Types may need to be created first:
- `from scb_atlas.atlas.type_service import create_typedef`
- `from scb_atlas.atlas.atlas_types import type_definitions`
- `create_typedef(type_definitions, atlas_client)`

### Issue: Entity Already Exists

```
Warning: Entity already exists
```

**Solution:** This is normal. Atlas will update the existing entity or skip it.

---

## 📋 File Reference

| File | Purpose |
|------|---------|
| `create_entities_with_pydantic.py` | Main script to create all entities using Pydantic models |
| `setup_atlas.sh` | Bash wrapper script |
| `ATLAS_SETUP_GUIDE.md` | Detailed setup guide |
| `CONTAINER_FAILED_TO_START.md` | Debugging container startup failures (OOMKilled, ImagePullBackOff, etc.) |
| `TROUBLESHOOT_503_ERROR.md` | Debugging 503 Service Unavailable errors (Kyma Dashboard only) |
| `scb_atlas/atlas/atlas_client.py` | Atlas client initialization |
| `scb_atlas/atlas/service/entity_service.py` | Entity creation functions |
| `scb_atlas/atlas/metadata_models/` | Pydantic model definitions for entities |
| `scb_atlas/atlas/service/entity_service.py` | Entity creation functions |
| `scb_atlas/atlas/metadata_models/` | Pydantic model definitions for entities |

---

## ⚡ Quick Commands

```bash
# Start Atlas (Docker)
docker-compose up -d

# Port forward (Kubernetes)
kubectl port-forward svc/atlas 23000:23000

# Create entities
uv run python create_entities_with_pydantic.py

# Check Atlas health
curl http://localhost:23000

# View Atlas logs (Docker)
docker logs atlas_server

# View Atlas logs (Kubernetes)
kubectl logs -l io.kompose.service=atlas

# Clean up (Docker)
docker-compose down

# Clean up (Kubernetes)
kubectl delete deployment,service -l io.kompose.service=atlas
```

---

## 🎯 Next Steps

1. ✅ **Start Atlas** - Ensure it's running on port 23000
2. ✅ **Run Script** - Execute `uv run python create_entities_with_pydantic.py`
3. ✅ **Access UI** - Open http://localhost:23000
4. ✅ **Login** - Use admin/admin
5. ✅ **Search** - Find your entities using Advanced Search
6. ✅ **Explore** - Click entities to view details and lineage
7. ✅ **Customize** - Modify script to create your own entities

---

## ✅ Verification Checklist

After running setup:

- [ ] Atlas is accessible at http://localhost:23000
- [ ] Can login with admin/admin
- [ ] 5 entity types are registered
- [ ] Database `finance_db` appears in search
- [ ] 3 tables appear when searching for SCB_Table
- [ ] Columns appear in table details
- [ ] Processes are visible
- [ ] Data product appears in search
- [ ] Can view entity details
- [ ] Can see lineage relationships

---

## 📞 Support

For more information:
- See **CONTAINER_FAILED_TO_START.md** for container startup failures (OOMKilled, ImagePullBackOff, etc.)
- See **TROUBLESHOOT_503_ERROR.md** for 503 Service Unavailable errors (Kyma Dashboard troubleshooting)
- See **ATLAS_SETUP_GUIDE.md** for detailed setup guide
- See **ENTITY_TYPES.md** for entity API reference
- See **README.md** for project overview
- Check **scb_example_entities.py** for code examples

---

## 🎉 You're All Set!

Your entities are now in Atlas on port 23000. 

**Access them at:** http://localhost:23000 (admin/admin)

**Happy exploring!** 🚀
