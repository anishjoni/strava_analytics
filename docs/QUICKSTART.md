# 🚀 Quick Start Guide - Strava Analytics Automation

## For SSH/Remote Workspace Users

### Step 1: Fix Permissions
```bash
# Run this first to fix all permission issues
./fix_permissions.sh
```

### Step 2: Activate Environment
```bash
# Use the convenient activation script
source activate_env.sh

# You should see:
# ✅ Virtual environment activated successfully
# 🐍 Python version: Python 3.13.3
```

### Step 3: Test Setup
```bash
# Test that everything is working
python scripts/test_flows.py

# You should see:
# 🎉 All tests passed!
```

### Step 4: Configure Credentials
```bash
# Edit the .env file with your Strava API credentials
nano .env

# Add your credentials:
# STRAVA_CLIENT_ID=your_client_id_here
# STRAVA_CLIENT_SECRET=your_client_secret_here
```

### Step 5: Initial Authentication (One-time)
You need to run your existing authentication workflow once to create the `tokens.json` file. After this, the system will automatically handle all token refreshes.

### Step 6: Start Prefect (3 terminals recommended)

**Terminal 1 - Start Prefect Server:**
```bash
source activate_env.sh

# Option A: For local access only (current setup)
prefect server start

# Option B: For remote access (bind to all interfaces)
prefect server start --host 0.0.0.0 --port 4200

# Keep this running
# Local access: http://localhost:4200
# Remote access: http://your-server-ip:4200 (if firewall allows)
```

**Terminal 2 - Deploy Flows:**
```bash
source activate_env.sh
prefect deploy --all
# This deploys all scheduled flows
```

**Terminal 3 - Start Worker:**
```bash
source activate_env.sh
prefect worker start --pool default-agent-pool
# Keep this running to execute flows
```

### Step 7: Verify Automation
1. Visit http://localhost:4200 (Prefect UI)
2. Check "Deployments" tab - you should see:
   - `token-management-hourly` (runs every hour)
   - `daily-strava-sync` (runs daily at 6 AM UTC)
   - `weekly-strava-sync` (runs weekly on Sunday at 2 AM UTC)

### Step 8: Test Manual Run
```bash
# Test the full pipeline manually
python -c "from src.flows.main_pipeline import strava_analytics_pipeline_flow; print(strava_analytics_pipeline_flow())"
```

## 🎉 You're Done!

Your Strava data pipeline is now fully automated:
- ✅ Tokens refresh automatically 10 minutes before expiration
- ✅ Daily sync keeps your data up to date
- ✅ Weekly full sync ensures data completeness
- ✅ No more manual Selenium authentication needed!

## 📊 What Happens Next

1. **Hourly**: Token management checks and refreshes if needed
2. **Daily at 6 AM UTC**: Syncs last 7 days of activities
3. **Weekly on Sunday at 2 AM UTC**: Full historical sync
4. **All data**: Automatically cleaned, transformed, and loaded to your MySQL database

## 🔍 Monitoring

- **Prefect UI**: http://localhost:4200
- **Flow Runs**: See all executions, logs, and status
- **Schedules**: View upcoming runs
- **Logs**: Detailed execution logs for debugging

## ⚠️ Important Notes

- Keep the Prefect server and worker running for automation
- The system will handle all token refreshes automatically
- Check the Prefect UI if flows fail
- Database credentials are in `.env` file
- Tokens are stored in `data/tokens.json`

## 🆘 Need Help?

- Run `./fix_permissions.sh` for permission issues
- Run `python scripts/test_flows.py` to test setup
- Check Prefect UI logs for flow failures
- Ensure database is running and accessible
