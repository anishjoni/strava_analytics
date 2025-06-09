# 🌐 Remote Access Guide - Prefect UI

## Understanding the Current Setup

When you run tests and see logs like:
```
INFO | Flow run 'misty-toad' - View at http://localhost:4200/runs/flow-run/...
```

**This means:**
- ✅ Prefect is running successfully on your **remote server**
- ❌ The URL `http://localhost:4200` refers to **localhost on the remote server**
- ❌ You **cannot** access this directly from your local browser

## 🔧 Solution Options

### Option 1: SSH Port Forwarding (Recommended) 🚀

**From your local machine:**
```bash
# Create SSH tunnel
ssh -L 4200:localhost:4200 username@your-remote-server-ip

# Keep this terminal open, then open your browser to:
# http://localhost:4200
```

**What this does:**
- Forwards port 4200 from remote server to your local machine
- Makes remote Prefect UI accessible at `http://localhost:4200` on your local browser
- Secure and doesn't require firewall changes

### Option 2: Use the Helper Script 🛠️

**From your local machine:**
```bash
# Use the provided script
./scripts/connect_prefect_ui.sh username@your-remote-server

# Follow the instructions, then open:
# http://localhost:4200 in your local browser
```

### Option 3: Configure Prefect for Remote Access 🌍

**On your remote server:**
```bash
# Instead of: prefect server start
# Use: prefect server start --host 0.0.0.0 --port 4200

# Then access from your local browser:
# http://your-remote-server-ip:4200
```

**Requirements:**
- Firewall must allow port 4200
- Security group must allow inbound traffic on port 4200
- Less secure than SSH tunneling

## 🎯 Recommended Workflow

### For Development/Testing:
1. **On remote server:** Start Prefect normally
   ```bash
   source activate_env.sh
   prefect server start
   ```

2. **On local machine:** Create SSH tunnel
   ```bash
   ssh -L 4200:localhost:4200 user@remote-server
   ```

3. **On local browser:** Open `http://localhost:4200`

### For Production:
1. **Use SSH tunneling** for security
2. **Or configure proper firewall rules** and use `--host 0.0.0.0`

## 🔍 Verifying Access

Once you have access, you should see:
- 📊 **Dashboard**: Overview of flow runs
- 📅 **Deployments**: Your scheduled flows (token-management-hourly, daily-strava-sync, etc.)
- 🏃 **Flow Runs**: Real-time and historical execution logs
- ⚙️ **Work Pools**: Worker status and configuration

## 🚨 Troubleshooting

### "Connection Refused" Error
```bash
# Check if Prefect server is running on remote server
ssh user@remote-server "ps aux | grep prefect"

# Start Prefect server if not running
ssh user@remote-server "cd /path/to/project && source .venv/bin/activate && prefect server start"
```

### SSH Tunnel Issues
```bash
# Check if tunnel is active
netstat -an | grep 4200

# Kill existing tunnels
pkill -f "ssh.*4200"

# Create new tunnel
ssh -L 4200:localhost:4200 user@remote-server
```

### Port Already in Use
```bash
# Use different local port
ssh -L 4201:localhost:4200 user@remote-server

# Then access: http://localhost:4201
```

## 🎉 What You'll See

Once connected, you can:
- ✅ **Monitor flow runs** in real-time
- ✅ **View logs** for debugging
- ✅ **Trigger manual runs** of your flows
- ✅ **Check schedules** (hourly token refresh, daily sync, weekly sync)
- ✅ **Monitor worker status**
- ✅ **View flow run history** and performance metrics

## 🔐 Security Notes

- **SSH tunneling** is the most secure option
- **Direct remote access** requires proper firewall configuration
- **Never expose Prefect UI** to the internet without authentication
- **Use VPN** if accessing from untrusted networks

## 📱 Mobile Access

You can even access the Prefect UI from your phone:
1. Create SSH tunnel from your laptop
2. Connect phone to same WiFi as laptop
3. Access `http://laptop-ip:4200` from phone browser

## 🎯 Quick Commands Reference

```bash
# Create tunnel (from local machine)
ssh -L 4200:localhost:4200 user@server

# Start Prefect (on remote server)
prefect server start

# Start with remote access (on remote server)
prefect server start --host 0.0.0.0

# Check if Prefect is running (on remote server)
curl http://localhost:4200/api/health

# Kill tunnel (from local machine)
pkill -f "ssh.*4200"
```

Now you can fully monitor and manage your automated Strava analytics pipeline from your local browser! 🚀
