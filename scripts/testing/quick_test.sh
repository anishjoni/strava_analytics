#!/bin/bash
# Quick test script for immediate verification

echo "🚀 Quick Test - Strava Analytics"
echo "==============================="

# Fix permissions first
echo "🔧 Fixing permissions..."
./scripts/setup/fix_permissions.sh > /dev/null 2>&1

# Test virtual environment
echo "🐍 Testing virtual environment..."
if source .venv/bin/activate 2>/dev/null; then
    echo "✅ Virtual environment: OK"
    
    # Test Python and packages
    if python -c "import prefect, polars, requests; print('✅ Packages: OK')" 2>/dev/null; then
        echo "✅ Required packages: OK"
        
        # Test our modules
        if python -c "
import sys
sys.path.insert(0, '.')
from src.strava_analytics.config import settings
from src.strava_analytics.flows.token_management import check_token_status
print('✅ Custom modules: OK')
" 2>/dev/null; then
            echo "✅ Custom modules: OK"
            echo ""
            echo "🎉 SUCCESS! Everything is working!"
            echo ""
            echo "Next steps:"
            echo "1. Edit .env with your Strava credentials"
            echo "2. Run: source activate_env.sh"
            echo "3. Follow QUICKSTART.md"
            exit 0
        else
            echo "❌ Custom modules: FAILED"
        fi
    else
        echo "❌ Required packages: FAILED"
        echo "Run: source .venv/bin/activate && uv add prefect polars requests sqlalchemy mysql-connector-python python-dotenv pandas"
    fi
else
    echo "❌ Virtual environment: FAILED"
    echo "Run: ./scripts/setup/fix_permissions.sh"
fi

echo ""
echo "❌ Issues detected. Run ./scripts/testing/test_remote_setup.sh for detailed diagnosis"
exit 1
