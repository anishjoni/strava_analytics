#!/bin/bash
# Debug script to understand how Prefect UI is accessible

echo "🔍 Debugging Prefect UI Access"
echo "=============================="
echo ""

echo "1. 🌐 Checking network connections on port 4200:"
echo "------------------------------------------------"
netstat -tulpn 2>/dev/null | grep 4200 || echo "No connections found on port 4200"
echo ""

echo "2. 🔍 Checking if Prefect server is running:"
echo "-------------------------------------------"
ps aux | grep prefect | grep -v grep || echo "No Prefect processes found"
echo ""

echo "3. 📡 Checking what's listening on port 4200:"
echo "--------------------------------------------"
lsof -i :4200 2>/dev/null || echo "Nothing listening on port 4200"
echo ""

echo "4. 🌍 Checking network interfaces:"
echo "---------------------------------"
ip addr show 2>/dev/null | grep -E "inet|UP" || ifconfig 2>/dev/null | grep -E "inet|UP" || echo "Could not get network info"
echo ""

echo "5. 🔧 Checking environment variables:"
echo "------------------------------------"
env | grep -i prefect || echo "No Prefect environment variables found"
echo ""

echo "6. 📂 Checking current directory and Prefect config:"
echo "--------------------------------------------------"
echo "Current directory: $(pwd)"
if command -v prefect >/dev/null 2>&1; then
    echo "Prefect version: $(prefect version 2>/dev/null || echo 'Could not get version')"
    echo "Prefect config:"
    prefect config view 2>/dev/null || echo "Could not get Prefect config"
else
    echo "Prefect command not found"
fi
echo ""

echo "7. 🌐 Testing local Prefect API access:"
echo "--------------------------------------"
if command -v curl >/dev/null 2>&1; then
    echo "Testing http://localhost:4200/api/health"
    curl -s http://localhost:4200/api/health 2>/dev/null || echo "Could not reach Prefect API on localhost:4200"
    echo ""
    echo "Testing http://127.0.0.1:4200/api/health"
    curl -s http://127.0.0.1:4200/api/health 2>/dev/null || echo "Could not reach Prefect API on 127.0.0.1:4200"
else
    echo "curl not available for testing"
fi
echo ""

echo "8. 🔍 Checking for tunnel/proxy processes:"
echo "-----------------------------------------"
ps aux | grep -E "(ssh|tunnel|proxy|ngrok|localtunnel)" | grep -v grep || echo "No tunnel/proxy processes found"
echo ""

echo "9. 📱 Checking if this is a cloud environment:"
echo "---------------------------------------------"
if [ -n "$CODESPACES" ]; then
    echo "✅ GitHub Codespaces detected"
    echo "CODESPACE_NAME: $CODESPACE_NAME"
    echo "GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN: $GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
elif [ -n "$GITPOD_WORKSPACE_ID" ]; then
    echo "✅ GitPod detected"
    echo "GITPOD_WORKSPACE_URL: $GITPOD_WORKSPACE_URL"
elif [ -n "$AWS_CLOUD9_USER" ]; then
    echo "✅ AWS Cloud9 detected"
elif [ -n "$REPL_ID" ]; then
    echo "✅ Replit detected"
else
    echo "No known cloud environment detected"
fi
echo ""

echo "10. 🌐 What URL are you using to access Prefect UI?"
echo "--------------------------------------------------"
echo "Please tell us what URL you're using in your browser to access the Prefect UI"
echo "Examples:"
echo "  - http://localhost:4200"
echo "  - https://some-random-string.github.dev"
echo "  - https://4200-username-repo.gitpod.io"
echo "  - http://your-server-ip:4200"
echo ""

echo "🎯 Summary:"
echo "----------"
echo "This debug info will help us understand how you're accessing the Prefect UI."
echo "Please share the output and the URL you're using in your browser!"
