#!/bin/bash
# Script to create SSH tunnel for Prefect UI access

echo "🌐 Prefect UI SSH Tunnel Setup"
echo "=============================="
echo ""

# Check if SSH connection details are provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 [user@]hostname [ssh_options]"
    echo ""
    echo "Examples:"
    echo "  $0 user@remote-server.com"
    echo "  $0 user@192.168.1.100"
    echo "  $0 user@server.com -i ~/.ssh/my_key"
    echo ""
    echo "This will create an SSH tunnel to access Prefect UI at:"
    echo "  http://localhost:4200 (on your local browser)"
    echo ""
    exit 1
fi

SSH_TARGET="$1"
shift
SSH_OPTIONS="$@"

echo "🔗 Creating SSH tunnel to $SSH_TARGET"
echo "📡 Forwarding remote port 4200 to local port 4200"
echo ""
echo "Once connected:"
echo "  ✅ Open http://localhost:4200 in your local browser"
echo "  ✅ You'll see the Prefect UI from the remote server"
echo ""
echo "Press Ctrl+C to close the tunnel"
echo ""

# Create SSH tunnel
ssh -L 4200:localhost:4200 $SSH_OPTIONS "$SSH_TARGET"
