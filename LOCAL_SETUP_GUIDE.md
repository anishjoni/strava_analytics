# Local Prefect Server Setup Guide

## 🏠 Quick Setup for Local Prefect Server

Due to encoding issues with Prefect CLI on Windows, here's a manual setup approach:

### **Step 1: Set Environment Variables**

In your PowerShell terminal, run:
```powershell
$env:PREFECT_API_URL = "http://localhost:4200/api"
$env:PREFECT_UI_URL = "http://localhost:4200"
$env:PYTHONIOENCODING = "utf-8"
```

### **Step 2: Start Prefect Server**

Open a **new terminal** and run:
```bash
prefect server start
```

**Keep this terminal open!** The server needs to stay running.

### **Step 3: Create Work Pool**

In your **original terminal**, run:
```bash
prefect work-pool create --type process default-agent-pool
```

### **Step 4: Deploy Your Flows**

```bash
python deploy_simple.py
```

### **Step 5: Start Worker**

```bash
python worker_venv.py
```

### **Step 6: Monitor**

Open your browser to: http://localhost:4200

## 🔧 Alternative: Use Batch File

Run the setup batch file:
```bash
start_local_setup.bat
```

Then follow the instructions it provides.

## 📋 What Each Component Does

### **Prefect Server** (`prefect server start`)
- Provides the API and web UI
- Stores flow run history and metadata
- Schedules flow runs
- **Must stay running**

### **Work Pool** (`default-agent-pool`)
- Defines where flows execute (your local machine)
- Routes flow runs to workers

### **Worker** (`python worker_venv.py`)
- Polls for scheduled flow runs
- Executes your Python flow code
- **Must stay running** for flows to execute

### **Deployments** (from `prefect.yaml`)
- `token-management-hourly`: Runs every hour
- `daily-strava-sync`: Runs daily at 6 AM
- `weekly-strava-sync`: Runs weekly on Sunday at 7 AM
- `manual-full-pipeline`: On-demand execution

## 🎯 Typical Workflow

### **Development:**
1. Start server: `prefect server start` (separate terminal)
2. Deploy flows: `python deploy_simple.py`
3. Start worker: `python worker_venv.py` (separate terminal)
4. Monitor: http://localhost:4200

### **Production:**
- Run server and worker as background services
- Flows execute automatically on schedule

## 🚨 Troubleshooting

### **"Connection refused" errors:**
- Make sure Prefect server is running
- Check that `PREFECT_API_URL` is set correctly

### **Flows not executing:**
- Make sure worker is running
- Check work pool exists: `prefect work-pool ls`

### **Encoding errors:**
- Set `PYTHONIOENCODING=utf-8` in environment
- Use the provided batch files

### **Can't access UI:**
- Make sure server is running on port 4200
- Check firewall settings

## 🔄 Starting/Stopping

### **To Start Everything:**
1. Terminal 1: `prefect server start`
2. Terminal 2: `python worker_venv.py`
3. Browser: http://localhost:4200

### **To Stop Everything:**
1. Ctrl+C in worker terminal
2. Ctrl+C in server terminal

## 📊 Monitoring Your Flows

### **Web UI (http://localhost:4200):**
- Flow Runs: See execution status
- Deployments: View schedules and trigger manual runs
- Work Pools: Check worker status
- Logs: View detailed execution logs

### **CLI Commands:**
```bash
# List deployments
prefect deployment ls

# List recent flow runs
prefect flow-run ls --limit 10

# Check worker status
prefect worker ls

# Run a deployment manually
prefect deployment run "daily-strava-sync"
```

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Server UI loads at http://localhost:4200
- ✅ Worker shows "Polling for work" messages
- ✅ Deployments appear in the UI
- ✅ Test runs complete successfully

## 📞 Next Steps

Once everything is running:
1. Test with: `prefect deployment run "token-management-hourly"`
2. Check logs in the UI
3. Verify your Strava data pipeline works
4. Set up automatic startup (optional)
