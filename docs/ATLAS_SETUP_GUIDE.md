# 🚀 How to Create Entities in Local Atlas (Port 23000)

## Complete Setup Guide

---

## 📋 Prerequisites

Before creating entities in Atlas, ensure:

1. **Atlas is running** on port 23000
2. **Network connectivity** to Atlas
3. **Valid credentials** (default: admin/admin)
4. **Python dependencies** installed
5. **Project configured** properly

---

## 🔧 Step 1: Start Local Atlas

### Option 1: Using Docker Compose (Recommended)

```bash
cd /Users/vishal/IdeaProjects/scb-data-product/apache-atlas/dcompose

# Start Atlas container
docker-compose up -d

# Verify it's running
docker ps | grep atlas

# Check logs
docker logs atlas_server
```

### Option 2: Using Kubernetes (Minikube)

```bash
cd /Users/vishal/IdeaProjects/scb-data-product/apache-atlas

# Apply configurations
kubectl apply -f atlas-claim0-persistentvolumeclaim.yaml
kubectl apply -f atlas-claim1-persistentvolumeclaim.yaml
kubectl apply -f atlas-deployment.yaml
kubectl apply -f atlas-service.yaml

# Port forward to access locally
kubectl port-forward svc/atlas 23000:23000

# Check pod status
kubectl get pods -l io.kompose.service=atlas
```

### Option 3: Verify Atlas is Running

```bash
# Check if Atlas is accessible
curl -I http://localhost:23000

# Expected response: HTTP/1.1 401 Unauthorized (that's OK, means Atlas is running)
```

---

## 📝 Step 2: Verify Configuration

The project uses these default settings:

```text
# scb_atlas/atlas/atlas_settings.py
ATLAS_URL = "http://localhost:23000"
USERNAME = "admin"
PASSWORD = "admin"
```

**To override with environment variables:**

```bash
export ATLAS_URL="http://localhost:23000"
export ATLAS_USERNAME="admin"
export ATLAS_PASSWORD="admin"
```

---

## 🚀 Step 3: Create All Entities

### Quick Method: Run Setup Script

```bash
cd /Users/vishal/IdeaProjects/scb-data-product

# Run the entity creation script
uv run python create_atlas_entities.py
```

This will automatically:
1. ✅ Create all type definitions
2. ✅ Create sample database (finance_db)
3. ✅ Create 3 sample tables
4. ✅ Create 15 columns across tables
5. ✅ Create 2 sample processes
6. ✅ Create 1 data product

### Expected Output

```
================================================================================
🚀 SCB Atlas - Entity Creation Setup
================================================================================

Step 1: Connecting to Atlas
✅ Connected to Atlas successfully!

Step 2: Creating Entity Type Definitions
✅ Type definitions created successfully!
   - SCB_Database
   - SCB_Table
   - SCB_Column
   - SCB_Process
   - SCB_DataProduct

Step 3: Creating Sample Database
✅ Database created: finance_db

Step 4: Creating Sample Tables
✅ Table created: finance_db.trades
✅ Table created: finance_db.transactions
✅ Table created: finance_db.daily_summary

Step 5: Creating Table Columns - Trades Table
✅ Column created: trade_id (string)
✅ Column created: trade_date (date)
✅ Column created: currency_pair (string)
...

Step 10: Setup Complete!
✅ All entities have been created successfully!

📊 Created Entities Summary:
  Database: 1 (finance_db)
  Tables: 3 (trades, transactions, daily_summary)
  Columns: 15
  Processes: 2
  Data Products: 1
```

---

## 🌐 Step 4: Access Atlas UI

### Navigate to Atlas

1. Open browser: **http://localhost:23000**
2. Login with credentials:
   - Username: **admin**
   - Password: **admin**

### Find Created Entities

**Search for entities by type:**

1. Click on **Search** tab
2. Click **Advanced Search**
3. Select **Entity Type**:
   - `SCB_Database` - Find databases
   - `SCB_Table` - Find tables
   - `SCB_Column` - Find columns
   - `SCB_Process` - Find processes
   - `SCB_DataProduct` - Find data products

### View Entity Details

1. Click on any entity in search results
2. View:
   - **Properties** - All attributes
   - **Lineage** - Data flow relationships
   - **Schema** - Column definitions
   - **Relationships** - Connected entities

---

## 📊 Sample Database Structure

### Created Database: `finance_db`

```
finance_db (Database)
├── trades (Table)
│   ├── trade_id (string)
│   ├── trade_date (date)
│   ├── currency_pair (string)
│   ├── amount (decimal)
│   ├── rate (decimal)
│   └── settlement_date (date)
├── transactions (Table)
│   ├── transaction_id (string)
│   ├── transaction_date (date)
│   ├── amount (decimal)
│   ├── description (string)
│   └── status (string)
├── daily_summary (Table)
│   ├── summary_date (date)
│   ├── total_trades (bigint)
│   ├── total_volume (decimal)
│   └── avg_rate (decimal)
├── daily_trade_aggregation (Process)
└── transaction_validation (Process)
```

---

## 🔍 Viewing Entities Programmatically

### Option 1: Search via Python

```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.discovery_service import dsl_search

# Connect to Atlas
atlas_client = create_atlas_client()

# Search for databases
databases = dsl_search(
    atlas_client=atlas_client,
    names=["finance_db"],
    type_name="SCB_Database"
)

print("Found databases:")
for db in databases:
    print(f"  - {db['attributes']['database_name']}")
```

### Option 2: Create Custom Entities

```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.entity_service import create_database_entity

atlas_client = create_atlas_client()

# Create your own database
create_database_entity(
    atlas_client,
    database_name="my_custom_db",
    location_uri="hdfs://data/custom",
    description="My custom database"
)

print("✅ Custom database created!")
```

---

## 🛠️ Troubleshooting

### Issue 1: Connection Refused

```
Error: Failed to connect to Atlas at http://localhost:23000
```

**Solution:**
```bash
# Verify Atlas is running
curl http://localhost:23000

# If using Kubernetes, ensure port-forward is active
kubectl port-forward svc/atlas 23000:23000

# If using Docker, check container
docker ps | grep atlas
docker logs atlas_server
```

### Issue 2: Authentication Failed

```
Error: Unable to connect to Atlas: Authentication failed
```

**Solution:**
```bash
# Verify credentials (default: admin/admin)
# Check if credentials are correct in atlas_settings.py
# Or set via environment variables:

export ATLAS_USERNAME="admin"
export ATLAS_PASSWORD="admin"
```

### Issue 3: Types Already Exist

```
Warning: Type creation error (may already exist)
```

**Solution:** This is normal if types were already created. The script will continue with entity creation.

### Issue 4: Entity Creation Failed

```
Error: Entity creation error
```

**Solution:**
1. Ensure types were created first
2. Check entity names are unique
3. Verify Atlas is responsive
4. Review Atlas logs for details

---

## 📋 Commands Reference

### Create Types Only

```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.type_service import create_typedef
from scb_atlas.atlas.atlas_types import type_definitions

atlas_client = create_atlas_client()
create_typedef(type_definitions, atlas_client)
```

### Create Database

```text
from scb_atlas.atlas.entity_service import create_database_entity

create_database_entity(
    atlas_client,
    database_name="my_db",
    location_uri="hdfs://path",
    description="My database"
)
```

### Create Table

```text
from scb_atlas.atlas.entity_service import create_table_entity

create_table_entity(
    atlas_client,
    table_name="my_table",
    database_name="my_db",
    table_type="EXTERNAL",
    description="My table"
)
```

### Create Column

```text
from scb_atlas.atlas.entity_service import create_column_entity

create_column_entity(
    atlas_client,
    column_name="id",
    data_type="bigint",
    table_name="my_db.my_table",
    comment="Primary key",
    position=1
)
```

### Create Process

```text
from scb_atlas.atlas.entity_service import create_process_entity_advanced

create_process_entity_advanced(
    atlas_client,
    process_name="my_process",
    query_id="proc_001",
    query_text="SELECT * FROM my_table",
    user_name="data_team"
)
```

---

## 🎯 Complete Example

```text
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.entity_service import (
    create_database_entity,
    create_table_entity,
    create_column_entity
)

# Connect
atlas_client = create_atlas_client()

# Create database
create_database_entity(
    atlas_client,
    database_name="sales_db",
    location_uri="hdfs://data/sales"
)

# Create table
create_table_entity(
    atlas_client,
    table_name="orders",
    database_name="sales_db",
    table_type="EXTERNAL"
)

# Create columns
create_column_entity(
    atlas_client,
    column_name="order_id",
    data_type="bigint",
    table_name="sales_db.orders",
    position=1
)

create_column_entity(
    atlas_client,
    column_name="order_date",
    data_type="date",
    table_name="sales_db.orders",
    position=2
)

print("✅ All entities created!")
```

---

## ✅ Verification Checklist

After running the setup script:

- [ ] Atlas is accessible at http://localhost:23000
- [ ] Can login with admin/admin
- [ ] All 5 entity types are created
- [ ] Database `finance_db` exists
- [ ] 3 tables are visible (trades, transactions, daily_summary)
- [ ] Columns appear in each table
- [ ] 2 processes are created
- [ ] 1 data product is created
- [ ] Can view entity details in Atlas UI
- [ ] Can see lineage relationships

---

## 📚 Next Steps

1. **Explore the UI**: Browse created entities
2. **Create Custom Entities**: Use the provided functions
3. **Build Data Lineage**: Connect processes to data flow
4. **Monitor Changes**: Track entity updates
5. **Extend Framework**: Add more entity types as needed

---

## 🆘 Need Help?

1. Review **ENTITY_TYPES.md** for API reference
2. Check **scb_example_entities.py** for code examples
3. Review **README.md** for project overview
4. Check Atlas logs for detailed errors
5. Verify connectivity: `curl http://localhost:23000`

---

## 📞 Summary

✅ **Quick Start**: `uv run python create_atlas_entities.py`
✅ **Access UI**: http://localhost:23000 (admin/admin)
✅ **Search Entities**: Use Advanced Search by type
✅ **Customize**: Modify create_atlas_entities.py for your needs
✅ **Done!** Your entities are now in Atlas!

