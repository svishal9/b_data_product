#!/bin/bash
# Quick test script for the lineage fix

set -e

echo "================================"
echo "🧪 Testing Workbook Lineage Fix"
echo "================================"
echo ""

cd /Users/vishal/IdeaProjects/scb-data-product

echo "1️⃣  Checking Atlas is running..."
if curl -s http://localhost:23000 > /dev/null 2>&1; then
    echo "   ✅ Atlas is running on port 23000"
else
    echo "   ❌ Atlas is NOT running on port 23000"
    echo "   Start with: docker-compose up -d (or kubectl port-forward)"
    exit 1
fi

echo ""
echo "2️⃣  Verifying Python syntax..."
python3 -m py_compile scb_atlas/atlas/read_data_product.py
echo "   ✅ Syntax check passed"

echo ""
echo "3️⃣  Checking imports..."
python3 -c "from scb_atlas.atlas.read_data_product import create_data_products_from_workbook, _create_lineage_processes" > /dev/null 2>&1
echo "   ✅ Imports work correctly"

echo ""
echo "4️⃣  Creating data products with lineage..."
echo "   (This may take 30-60 seconds)"
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx

echo ""
echo "5️⃣  Verifying lineage creation..."
echo "   (Testing for ingest and publish processes)"
uv run python tests/manual/test_lineage_creation.py

echo ""
echo "================================"
echo "✅ All tests passed!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Open Atlas: http://localhost:23000"
echo "2. Login: admin/admin"
echo "3. Search → Advanced Search"
echo "4. Type: SCB_DataProduct"
echo "5. Click a data product"
echo "6. Click Lineage tab to see the processes"
echo ""

