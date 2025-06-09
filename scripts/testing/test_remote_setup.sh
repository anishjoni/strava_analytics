#!/bin/bash
# Comprehensive test script for Strava Analytics on remote terminal

echo "🧪 Testing Strava Analytics Setup on Remote Terminal"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_TOTAL=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="$3"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "   ${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "   ${RED}❌ FAIL${NC}"
        return 1
    fi
}

# Function to check file exists and is executable
check_executable() {
    local file="$1"
    if [ -f "$file" ] && [ -x "$file" ]; then
        return 0
    else
        return 1
    fi
}

# Function to check directory exists
check_directory() {
    local dir="$1"
    if [ -d "$dir" ]; then
        return 0
    else
        return 1
    fi
}

echo "🔍 Phase 1: Basic File Structure Tests"
echo "------------------------------------"

run_test "Project directory structure" "check_directory 'src' && check_directory 'scripts' && check_directory 'src/flows'"
run_test "Virtual environment exists" "check_directory '.venv'"
run_test "Virtual environment activate script" "check_executable '.venv/bin/activate'"
run_test "Python executable in venv" "check_executable '.venv/bin/python'"
run_test "Permission fix script exists" "check_executable 'fix_permissions.sh'"
run_test "Environment activation script exists" "check_executable 'activate_env.sh'"

echo ""
echo "🔧 Phase 2: Permission Tests"
echo "----------------------------"

run_test "Scripts are executable" "check_executable 'scripts/test_flows.py' && check_executable 'scripts/setup_prefect.py'"
run_test "Core Python files exist" "[ -f 'src/config.py' ] && [ -f 'src/utils.py' ]"
run_test "Flow files exist" "[ -f 'src/flows/token_management.py' ] && [ -f 'src/flows/main_pipeline.py' ]"
run_test "Configuration files exist" "[ -f 'prefect.yaml' ] && [ -f '.env.example' ]"

echo ""
echo "🐍 Phase 3: Python Environment Tests"
echo "-----------------------------------"

# Test virtual environment activation
echo -e "${BLUE}Test $((TESTS_TOTAL + 1)): Virtual environment activation${NC}"
TESTS_TOTAL=$((TESTS_TOTAL + 1))

if source .venv/bin/activate 2>/dev/null; then
    echo -e "   ${GREEN}✅ PASS - Virtual environment activated${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # Test Python version
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: Python version check${NC}"
    PYTHON_VERSION=$(python --version 2>&1)
    echo "   Python version: $PYTHON_VERSION"
    if [[ "$PYTHON_VERSION" == *"Python 3."* ]]; then
        echo -e "   ${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${RED}❌ FAIL - Python 3 not found${NC}"
    fi
    
    # Test package imports
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: Package imports${NC}"
    if python -c "import prefect, polars, requests, sqlalchemy; print('All packages imported successfully')" 2>/dev/null; then
        echo -e "   ${GREEN}✅ PASS - All required packages available${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${RED}❌ FAIL - Missing required packages${NC}"
        echo "   Run: uv add prefect polars requests sqlalchemy mysql-connector-python python-dotenv pandas"
    fi
    
    # Test our custom modules
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}Test $TESTS_TOTAL: Custom module imports${NC}"
    if python -c "
import sys
sys.path.insert(0, '.')
from src.config import settings
from src.utils import load_tokens
from src.flows.token_management import check_token_status
print('Custom modules imported successfully')
" 2>/dev/null; then
        echo -e "   ${GREEN}✅ PASS - Custom modules working${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "   ${RED}❌ FAIL - Custom module import issues${NC}"
    fi
    
else
    echo -e "   ${RED}❌ FAIL - Cannot activate virtual environment${NC}"
    echo "   Try running: ./fix_permissions.sh"
fi

echo ""
echo "⚙️ Phase 4: Configuration Tests"
echo "------------------------------"

# Test configuration loading
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo -e "${BLUE}Test $TESTS_TOTAL: Configuration loading${NC}"
if source .venv/bin/activate 2>/dev/null && python -c "
import sys
sys.path.insert(0, '.')
from src.config import settings
print(f'Database URL: {settings.database_url}')
print(f'Data directory: {settings.data_dir}')
print('Configuration loaded successfully')
" 2>/dev/null; then
    echo -e "   ${GREEN}✅ PASS - Configuration working${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "   ${RED}❌ FAIL - Configuration issues${NC}"
fi

# Test data directory creation
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo -e "${BLUE}Test $TESTS_TOTAL: Data directory creation${NC}"
if source .venv/bin/activate 2>/dev/null && python -c "
import sys
sys.path.insert(0, '.')
from src.config import settings
data_dir = settings.ensure_data_dir()
print(f'Data directory created: {data_dir}')
" 2>/dev/null; then
    echo -e "   ${GREEN}✅ PASS - Data directory working${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "   ${RED}❌ FAIL - Data directory issues${NC}"
fi

echo ""
echo "🧪 Phase 5: Flow Tests (Basic)"
echo "-----------------------------"

# Test flow imports
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo -e "${BLUE}Test $TESTS_TOTAL: Flow imports${NC}"
if source .venv/bin/activate 2>/dev/null && python scripts/test_flows.py 2>/dev/null | grep -q "All tests passed"; then
    echo -e "   ${GREEN}✅ PASS - All flows import correctly${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "   ${RED}❌ FAIL - Flow import issues${NC}"
    echo "   Run: python scripts/test_flows.py for details"
fi

echo ""
echo "📋 Phase 6: Environment File Tests"
echo "---------------------------------"

# Check if .env file exists
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo -e "${BLUE}Test $TESTS_TOTAL: Environment file${NC}"
if [ -f ".env" ]; then
    echo -e "   ${GREEN}✅ PASS - .env file exists${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    
    # Check if it has required variables
    if grep -q "STRAVA_CLIENT_ID" .env && grep -q "STRAVA_CLIENT_SECRET" .env; then
        echo -e "   ${GREEN}✅ BONUS - .env has Strava credentials configured${NC}"
    else
        echo -e "   ${YELLOW}⚠️ WARNING - .env needs Strava credentials${NC}"
        echo "   Edit .env file and add your STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET"
    fi
else
    echo -e "   ${YELLOW}⚠️ WARNING - .env file not found${NC}"
    echo "   Run: cp .env.example .env and edit with your credentials"
fi

echo ""
echo "🎯 Phase 7: Quick Functional Test"
echo "--------------------------------"

# Test token status check (without actual tokens)
TESTS_TOTAL=$((TESTS_TOTAL + 1))
echo -e "${BLUE}Test $TESTS_TOTAL: Token management (dry run)${NC}"
if source .venv/bin/activate 2>/dev/null && python -c "
import sys
sys.path.insert(0, '.')
from src.flows.token_management import check_token_status
try:
    result = check_token_status()
    print('Token status check completed (expected to fail without tokens.json)')
except FileNotFoundError:
    print('Token status check working (no tokens.json found - expected)')
except Exception as e:
    print(f'Token status check failed: {e}')
    raise
" 2>/dev/null; then
    echo -e "   ${GREEN}✅ PASS - Token management flow working${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "   ${RED}❌ FAIL - Token management issues${NC}"
fi

echo ""
echo "=================================================="
echo "📊 TEST SUMMARY"
echo "=================================================="
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}/$TESTS_TOTAL"

if [ $TESTS_PASSED -eq $TESTS_TOTAL ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ Your Strava Analytics setup is working perfectly!"
    echo ""
    echo "🚀 Next steps:"
    echo "1. Edit .env file with your Strava API credentials"
    echo "2. Run initial authentication to create tokens.json"
    echo "3. Start Prefect: prefect server start"
    echo "4. Deploy flows: prefect deploy --all"
    echo "5. Start worker: prefect worker start --pool default-agent-pool"
    echo ""
    echo "📖 See QUICKSTART.md for detailed instructions"
    
elif [ $TESTS_PASSED -gt $((TESTS_TOTAL * 3 / 4)) ]; then
    echo -e "${YELLOW}⚠️ MOSTLY WORKING - Minor issues detected${NC}"
    echo ""
    echo "Most tests passed. Check the failed tests above and:"
    echo "1. Run: ./fix_permissions.sh"
    echo "2. Ensure .env file is configured"
    echo "3. Check that all dependencies are installed"
    
else
    echo -e "${RED}❌ SIGNIFICANT ISSUES DETECTED${NC}"
    echo ""
    echo "Multiple tests failed. Please:"
    echo "1. Run: ./fix_permissions.sh"
    echo "2. Ensure virtual environment is properly set up"
    echo "3. Install missing dependencies"
    echo "4. Check file permissions and structure"
fi

echo ""
echo "🔍 For detailed testing, run:"
echo "   source activate_env.sh"
echo "   python scripts/test_flows.py"
echo ""
echo "📚 Documentation:"
echo "   README.md - Full documentation"
echo "   QUICKSTART.md - Quick start guide"
