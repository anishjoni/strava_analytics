#!/bin/bash
# Fix permissions for Strava Analytics project

echo "🔧 Fixing permissions for Strava Analytics project..."

# Fix virtual environment permissions
if [ -d ".venv" ]; then
    echo "📁 Fixing virtual environment permissions..."
    chmod +x .venv/bin/*
    echo "✅ Virtual environment permissions fixed"
else
    echo "⚠️ Virtual environment not found"
fi

# Fix script permissions
echo "📁 Fixing script permissions..."
chmod +x scripts/*.py
chmod +x *.sh

# Fix Python file permissions (make them readable/writable)
find src/ -name "*.py" -exec chmod 644 {} \;

# Make sure directories are accessible
find . -type d -exec chmod 755 {} \;

echo "✅ All permissions fixed!"
echo ""
echo "You can now:"
echo "1. Activate environment: source activate_env.sh"
echo "2. Or manually: source .venv/bin/activate"
echo "3. Test setup: python scripts/test_flows.py"
