# Strava Analytics - Prefect Cloud Monitoring Guide

## 🌐 Quick Access

**Prefect Cloud Dashboard**: https://app.prefect.cloud

## 🚀 Initial Setup

### 1. Connect to Prefect Cloud
```bash
prefect cloud login
```

### 2. Start Worker (Choose One Method)

**Option 1: Python Script (Recommended)**
```bash
python start_worker.py
```

**Option 2: Windows Batch File**
```bash
start_worker.bat
```

**Option 3: PowerShell Script**
```powershell
.\start_worker.ps1
```

**Option 4: Manual (if encoding issues persist)**
```bash
# Set encoding first
set PYTHONIOENCODING=utf-8
chcp 65001

# Then start worker
prefect worker start --pool default-agent-pool
```

### 3. Run Monitoring Setup
```bash
python setup_monitoring.py
```

## 📊 Dashboard Overview

### **Deployments Tab**
- **View**: All your scheduled flows
- **Features**:
  - ✅ Active/Paused status
  - ⏰ Next run times
  - 📈 Success rates
  - ▶️ Quick run buttons

### **Flow Runs Tab**
- **View**: Real-time execution status
- **Features**:
  - 🔴 Live status indicators
  - 📝 Detailed logs
  - ⏱️ Execution duration
  - 🔄 Retry information

### **Analytics Tab**
- **View**: Performance metrics
- **Features**:
  - 📈 Success rate trends
  - ⏱️ Average execution times
  - 📊 Resource usage
  - 🔍 Failure analysis

## 🔔 Setting Up Alerts

### **Email Notifications**
1. Go to **Settings** → **Notifications**
2. Click **Create Notification**
3. Configure for:
   - Flow run failures
   - Deployment issues
   - Worker disconnections

### **Slack Integration**
1. Go to **Settings** → **Integrations**
2. Add Slack webhook URL
3. Configure notification triggers

## 📋 Your Strava Analytics Deployments

### **1. Token Management (Hourly)**
- **Name**: `proactive-token-management/token-management-hourly`
- **Schedule**: Every hour
- **Monitor**: Token refresh success
- **Alert on**: Consecutive failures

### **2. Daily Sync**
- **Name**: `strava-analytics-pipeline/daily-strava-sync`
- **Schedule**: 6 AM daily (Toronto time)
- **Monitor**: Data extraction success
- **Alert on**: Sync failures

### **3. Weekly Sync**
- **Name**: `strava-analytics-pipeline/weekly-strava-sync`
- **Schedule**: 7 AM Sundays (Toronto time)
- **Monitor**: Full data sync completion
- **Alert on**: Long execution times

### **4. Manual Pipeline**
- **Name**: `strava-analytics-pipeline/manual-full-pipeline`
- **Schedule**: On-demand
- **Monitor**: Manual execution results
- **Alert on**: Not applicable

## 🛠️ Monitoring Commands

### **Check Status**
```bash
# View all deployments
prefect deployment ls

# Check recent flow runs
prefect flow-run ls --limit 10

# Check worker status
prefect worker ls
```

### **Manual Execution**
```bash
# Test token management
prefect deployment run 'proactive-token-management/token-management-hourly'

# Run daily sync manually
prefect deployment run 'strava-analytics-pipeline/daily-strava-sync'

# Run weekly sync manually
prefect deployment run 'strava-analytics-pipeline/weekly-strava-sync'
```

### **Deployment Management**
```bash
# Pause a deployment
prefect deployment pause 'strava-analytics-pipeline/daily-strava-sync'

# Resume a deployment
prefect deployment resume 'strava-analytics-pipeline/daily-strava-sync'

# View deployment details
prefect deployment inspect 'strava-analytics-pipeline/daily-strava-sync'
```

### **Logs and Debugging**
```bash
# View flow run logs (replace with actual flow-run-id)
prefect flow-run logs <flow-run-id>

# View work pool details
prefect work-pool inspect default-agent-pool
```

## 📈 Key Metrics to Monitor

### **Daily Monitoring**
- ✅ Flow run success rates
- ⏱️ Execution times
- 🔄 Token refresh status
- 👷 Worker health

### **Weekly Review**
- 📊 Data sync completeness
- 📈 Performance trends
- 🚨 Error patterns
- 💾 Database growth

### **Monthly Analysis**
- 📊 Overall system health
- 🔧 Optimization opportunities
- 📈 Usage patterns
- 💰 Resource costs

## 🚨 Common Issues & Solutions

### **Token Refresh Failures**
- **Symptom**: Token management flow fails
- **Solution**: Check Strava API credentials
- **Command**: `prefect deployment run 'proactive-token-management/token-management-hourly'`

### **Data Sync Failures**
- **Symptom**: Daily/weekly sync fails
- **Solution**: Check API rate limits and network
- **Command**: Check logs in Prefect Cloud UI

### **Worker Disconnections**
- **Symptom**: Flows stuck in "Pending" state
- **Solution**: Restart worker with encoding fix
- **Command**: `python start_worker.py` or `start_worker.bat`

### **Encoding Errors (Windows)**
- **Symptom**: UnicodeDecodeError when starting worker
- **Solution**: Use provided startup scripts
- **Command**: `python start_worker.py` (handles UTF-8 properly)

### **Database Connection Issues**
- **Symptom**: Database operations fail
- **Solution**: Check database connectivity
- **Command**: Test database connection manually

## 🎯 Best Practices

### **Monitoring Routine**
1. **Daily**: Quick dashboard check (2 minutes)
2. **Weekly**: Review analytics and trends (10 minutes)
3. **Monthly**: Deep dive analysis (30 minutes)

### **Alert Configuration**
- Set up email alerts for failures
- Use Slack for team notifications
- Configure escalation for critical issues

### **Performance Optimization**
- Monitor execution times
- Adjust `max_pages` parameters
- Scale workers based on load

## 🔗 Useful Links

- **Prefect Cloud Dashboard**: https://app.prefect.cloud
- **Prefect Documentation**: https://docs.prefect.io
- **Strava API Documentation**: https://developers.strava.com
- **Your GitHub Repository**: https://github.com/anishjoni/strava_analytics
