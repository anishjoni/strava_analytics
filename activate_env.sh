#!/bin/bash
# Activation script for Strava Analytics virtual environment

echo "🚀 Activating Strava Analytics environment..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Verify activation
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Virtual environment activated successfully"
    echo "📍 Virtual environment: $VIRTUAL_ENV"
    echo "🐍 Python version: $(python --version)"
    echo ""
    echo "Available commands:"
    echo "  python scripts/test_flows.py     - Test the setup"
    echo "  python scripts/setup_prefect.py  - Setup Prefect"
    echo "  prefect server start             - Start Prefect server"
    echo "  prefect deploy --all             - Deploy flows"
    echo "  prefect worker start --pool default-agent-pool - Start worker"
    echo ""
    echo "💡 To deactivate, run: deactivate"
else
    echo "❌ Failed to activate virtual environment"
    exit 1
fi
