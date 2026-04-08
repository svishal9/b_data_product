#!/bin/bash
# Quick setup script for Atlas entities

set -e

echo ""
echo "=================================="
echo "SCB Atlas - Quick Setup Script"
echo "=================================="
echo ""

# Step 1: Check if Atlas is running
echo "1️⃣  Checking if Atlas is running on port 23000..."
if curl -s http://localhost:23000 > /dev/null; then
    echo "   ✅ Atlas is running"
else
    echo "   ❌ Atlas is NOT running on port 23000"
    echo ""
    echo "   Please start Atlas first:"
    echo ""
    echo "   Option 1 - Docker:"
    echo "   docker-compose up -d"
    echo ""
    echo "   Option 2 - Kubernetes:"
    echo "   kubectl port-forward svc/atlas 23000:23000"
    echo ""
    exit 1
fi

# Step 2: Check Python is available
echo ""
echo "2️⃣  Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python3 is not installed"
    exit 1
fi
echo "   ✅ Python3 is available"

# Step 3: Check project directory
echo ""
echo "3️⃣  Checking project directory..."
if [ ! -f "create_entities_with_pydantic.py" ]; then
    echo "   ❌ create_entities_with_pydantic.py not found"
    echo "   Please run from project root: /Users/vishal/IdeaProjects/scb-data-product"
    exit 1
fi
echo "   ✅ Project files found"

# Step 4: Create entities
echo ""
echo "4️⃣  Creating entities in Atlas..."
echo ""

if command -v uv &> /dev/null; then
    uv run python create_entities_with_pydantic.py
else
    python3 create_entities_with_pydantic.py
fi

RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "=================================="
    echo "✅ Setup Complete!"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo "1. Open http://localhost:23000 in your browser"
    echo "2. Login with admin / admin"
    echo "3. Go to Search tab"
    echo "4. Search for entities by type"
    echo ""
else
    echo ""
    echo "=================================="
    echo "❌ Setup Failed"
    echo "=================================="
    echo ""
    echo "Please check the errors above and try again."
    exit 1
fi

