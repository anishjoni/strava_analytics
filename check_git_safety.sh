#!/bin/bash
# Safety check script before pushing to git

echo "🔒 Git Safety Check - Strava Analytics"
echo "====================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SAFE_TO_PUSH=true

echo -e "${BLUE}1. Checking .gitignore coverage...${NC}"
echo "-----------------------------------"

# Check if .gitignore exists and has essential entries
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore file exists"
    
    # Check for essential patterns
    essential_patterns=(".env" "tokens.json" ".venv/" "__pycache__/")
    
    for pattern in "${essential_patterns[@]}"; do
        if grep -q "$pattern" .gitignore; then
            echo "✅ $pattern is ignored"
        else
            echo -e "${RED}❌ $pattern is NOT ignored${NC}"
            SAFE_TO_PUSH=false
        fi
    done
else
    echo -e "${RED}❌ .gitignore file missing${NC}"
    SAFE_TO_PUSH=false
fi

echo ""
echo -e "${BLUE}2. Checking for sensitive files that would be committed...${NC}"
echo "--------------------------------------------------------"

# Check what would be added to git
if command -v git >/dev/null 2>&1; then
    # Check if we're in a git repo
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo "📁 Checking files that would be committed..."
        
        # Get list of files that would be committed
        files_to_commit=$(git status --porcelain | grep -E "^[AM]|^\?\?" | cut -c4-)
        
        if [ -z "$files_to_commit" ]; then
            echo "✅ No new files to commit"
        else
            echo "📋 Files that would be committed:"
            echo "$files_to_commit" | while read -r file; do
                echo "  - $file"
                
                # Check for sensitive patterns in filenames (but exclude legitimate code files)
                if [[ "$file" =~ \.(env|key|secret|credential|pem|p12|pfx)$ ]] ||
                   [[ "$file" =~ (secret|credential|password|private_key) ]] ||
                   [[ "$file" =~ ^(tokens\.json|\.env|credentials\.json|secrets\.json)$ ]]; then
                    echo -e "    ${RED}⚠️ POTENTIALLY SENSITIVE FILE${NC}"
                    SAFE_TO_PUSH=false
                elif [[ "$file" =~ token.*\.py$ ]]; then
                    echo -e "    ${YELLOW}ℹ️ Python file with 'token' in name (likely code, not credentials)${NC}"
                fi
            done
        fi
        
        # Check for sensitive content in files to be committed
        echo ""
        echo "🔍 Checking file contents for sensitive data..."
        
        sensitive_patterns=(
            "client_secret.*[a-zA-Z0-9]{20,}"
            "api_key.*[a-zA-Z0-9]{20,}"
            "password.*[^=]*[a-zA-Z0-9]{8,}"
            "token.*[a-zA-Z0-9]{20,}"
            "secret.*[a-zA-Z0-9]{20,}"
        )
        
        for pattern in "${sensitive_patterns[@]}"; do
            if git diff --cached --name-only 2>/dev/null | xargs grep -l -i "$pattern" 2>/dev/null; then
                echo -e "${RED}⚠️ Found potential sensitive data matching: $pattern${NC}"
                SAFE_TO_PUSH=false
            fi
        done
        
    else
        echo "⚠️ Not in a git repository"
    fi
else
    echo "⚠️ Git not available"
fi

echo ""
echo -e "${BLUE}3. Checking specific sensitive files...${NC}"
echo "--------------------------------------------"

sensitive_files=(
    ".env"
    "data/tokens.json"
    "tokens.json"
    "src/access_token.json"
    "credentials.json"
    "secrets.json"
)

for file in "${sensitive_files[@]}"; do
    if [ -f "$file" ]; then
        if git check-ignore "$file" >/dev/null 2>&1; then
            echo "✅ $file exists but is properly ignored"
        else
            echo -e "${RED}❌ $file exists and is NOT ignored${NC}"
            SAFE_TO_PUSH=false
            
            # Check if it contains real credentials
            if [[ "$file" == ".env" ]]; then
                if grep -q "your_client_id_here\|your_client_secret_here" "$file"; then
                    echo "  ℹ️ Contains placeholder values (safe)"
                else
                    echo -e "  ${RED}⚠️ May contain real credentials${NC}"
                fi
            fi
        fi
    fi
done

echo ""
echo -e "${BLUE}4. Checking for database files...${NC}"
echo "--------------------------------"

db_files=$(find . -name "*.db" -o -name "*.sqlite" -o -name "*.sqlite3" 2>/dev/null | grep -v ".venv")
if [ -z "$db_files" ]; then
    echo "✅ No database files found"
else
    echo "📋 Database files found:"
    echo "$db_files" | while read -r file; do
        if git check-ignore "$file" >/dev/null 2>&1; then
            echo "✅ $file (ignored)"
        else
            echo -e "${RED}❌ $file (NOT ignored)${NC}"
            SAFE_TO_PUSH=false
        fi
    done
fi

echo ""
echo -e "${BLUE}5. Checking virtual environment...${NC}"
echo "--------------------------------"

if [ -d ".venv" ]; then
    if git check-ignore ".venv" >/dev/null 2>&1; then
        echo "✅ .venv directory is properly ignored"
    else
        echo -e "${RED}❌ .venv directory is NOT ignored${NC}"
        SAFE_TO_PUSH=false
    fi
else
    echo "ℹ️ No .venv directory found"
fi

echo ""
echo "====================================="
echo -e "${BLUE}🎯 SAFETY CHECK RESULTS${NC}"
echo "====================================="

if [ "$SAFE_TO_PUSH" = true ]; then
    echo -e "${GREEN}✅ SAFE TO PUSH${NC}"
    echo ""
    echo "Your repository is properly configured:"
    echo "✅ Sensitive files are ignored"
    echo "✅ No credentials in tracked files"
    echo "✅ Virtual environment is ignored"
    echo "✅ Database files are ignored"
    echo ""
    echo -e "${GREEN}🚀 You can safely push to your git repository!${NC}"
    echo ""
    echo "Recommended commands:"
    echo "  git add ."
    echo "  git commit -m 'Add automated Strava analytics pipeline with Prefect'"
    echo "  git push origin agent"
else
    echo -e "${RED}❌ NOT SAFE TO PUSH${NC}"
    echo ""
    echo -e "${YELLOW}⚠️ Issues found that need to be resolved:${NC}"
    echo "- Check the warnings above"
    echo "- Update .gitignore if needed"
    echo "- Remove or ignore sensitive files"
    echo "- Verify no real credentials are in tracked files"
    echo ""
    echo -e "${YELLOW}🛠️ Fix issues before pushing!${NC}"
fi

echo ""
echo "📚 For more info, see:"
echo "  - .gitignore file"
echo "  - REMOTE_ACCESS_GUIDE.md"
echo "  - README.md"
