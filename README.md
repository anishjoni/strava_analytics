# Strava Analytics - Automated Data Pipeline

An automated data pipeline that extracts, transforms, and loads Strava activity data using Prefect for orchestration. The system includes proactive token management to avoid manual authentication workflows.

## 🚀 Features

- **Automated Token Management**: Proactive token refresh 10 minutes before expiration
- **Scheduled Data Sync**: Daily and weekly automated data synchronization
- **Robust Error Handling**: Comprehensive retry logic and error reporting
- **Data Transformation**: Clean, standardized data with feature engineering
- **Database Integration**: Automated loading to MySQL database
- **Monitoring**: Prefect UI for flow monitoring and management

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Strava API    │───▶│  Prefect Flows   │───▶│  MySQL Database │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Token Manager   │
                       │ (Auto Refresh)   │
                       └──────────────────┘
```

### Flow Architecture:
1. **Token Management Flow**: Runs hourly to ensure valid authentication
2. **Data Extraction Flow**: Fetches activities from Strava API with pagination
3. **Data Transformation Flow**: Cleans and standardizes data with unit conversions
4. **Database Operations Flow**: Loads data to MySQL with duplicate handling
5. **Main Pipeline Flow**: Orchestrates the complete end-to-end process

## 📁 Project Structure

```
strava_analytics/
├── README.md                     # Main documentation
├── pyproject.toml               # Project configuration
├── prefect.yaml                 # Prefect deployment config
├── .env.example                 # Environment template
├── setup.sh                    # Quick setup script
├── test.sh                     # Quick test script
│
├── docs/                        # Documentation
│   ├── QUICKSTART.md           # Quick start guide
│   └── REMOTE_ACCESS_GUIDE.md  # Remote access instructions
│
├── scripts/                     # Utility scripts
│   ├── setup/                   # Setup and installation
│   │   ├── setup_prefect.py    # Prefect setup
│   │   ├── fix_permissions.sh  # Permission fixes
│   │   └── activate_env.sh     # Environment activation
│   ├── testing/                 # Testing scripts
│   │   ├── test_flows.py       # Basic flow tests
│   │   ├── test_with_sample_data.py # Comprehensive tests
│   │   └── run_complete_test.sh # Complete test suite
│   └── utils/                   # Utility scripts
│       └── connect_prefect_ui.sh # SSH tunnel helper
│
├── src/strava_analytics/        # Main package
│   ├── __init__.py             # Package initialization
│   ├── config.py               # Configuration management
│   ├── utils.py                # Utility functions
│   └── flows/                  # Prefect flows
│       ├── token_management.py # Token refresh and validation
│       ├── data_extraction.py  # Strava API data fetching
│       ├── data_transformation.py # Data cleaning
│       ├── database_operations.py # Database operations
│       └── main_pipeline.py    # Main orchestration
│
├── notebooks/                   # Jupyter notebooks
│   ├── 01-pull_data_from_strava.ipynb
│   └── 03-push_data_to_DB.ipynb
│
└── data/                        # Data directory
    └── .gitkeep                # Ensures directory is tracked
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.12+
- MySQL database
- Strava API application (get credentials from [Strava API Settings](https://www.strava.com/settings/api))

### 1. Install Dependencies
```bash
# Install dependencies using uv (recommended)
uv add prefect polars requests sqlalchemy mysql-connector-python python-dotenv

# Or using pip
pip install prefect polars requests sqlalchemy mysql-connector-python python-dotenv
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Required environment variables:
- `STRAVA_CLIENT_ID`: Your Strava application client ID
- `STRAVA_CLIENT_SECRET`: Your Strava application client secret
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database connection details

### 3. Initial Authentication
You'll need to perform initial Strava authentication to get refresh tokens. This is a one-time setup:

```python
# Run your existing authentication workflow to create tokens.json
# The automated system will handle all subsequent token refreshes
```

### 4. Fix Permissions (if using SSH/remote workspace)
```bash
# Fix all permissions
./scripts/setup/fix_permissions.sh

# Activate virtual environment
source scripts/setup/activate_env.sh
# OR manually: source .venv/bin/activate
```

### 5. Setup Prefect
```bash
# Run the setup script
python scripts/setup_prefect.py

# Or manually:
# 1. Start Prefect server
prefect server start

# 2. Deploy flows
prefect deploy --all

# 3. Start worker
prefect worker start --pool default-agent-pool
```

### 6. Test the Setup
```bash
# Test basic functionality
python scripts/test_flows.py

# Test individual flows
python -m src.flows.token_management
python -m src.flows.main_pipeline
```

## 🔄 Automated Scheduling

The system includes three automated schedules:

### 1. Token Management (Hourly)
- **Schedule**: Every hour (`0 * * * *`)
- **Purpose**: Proactive token refresh 10 minutes before expiration
- **Flow**: `proactive_token_management_flow`

### 2. Daily Sync (Daily at 6 AM UTC)
- **Schedule**: Daily at 6 AM UTC (`0 6 * * *`)
- **Purpose**: Sync recent activities (last 7 days)
- **Flow**: `daily_strava_sync_flow`

### 3. Weekly Full Sync (Sunday at 2 AM UTC)
- **Schedule**: Weekly on Sunday at 2 AM UTC (`0 2 * * 0`)
- **Purpose**: Full historical sync for data completeness
- **Flow**: `weekly_full_sync_flow`

## 🎯 Key Benefits

### Eliminates Manual Authentication
- **Problem Solved**: No more manual Selenium-based authentication
- **Solution**: Proactive token refresh before expiration
- **Buffer**: Configurable refresh buffer (default: 10 minutes)

### Automated Data Pipeline
- **Extraction**: Paginated API calls with retry logic
- **Transformation**: Unit conversions, data typing, feature engineering
- **Loading**: Duplicate handling, error recovery, transaction safety

### Monitoring & Observability
- **Prefect UI**: Visual flow monitoring (see access instructions below)
- **Logging**: Comprehensive logging throughout all flows
- **Error Handling**: Graceful failure handling with detailed error messages

#### Accessing Prefect UI from Local Machine

**Option 1: SSH Port Forwarding (Recommended)**
```bash
# From your local machine
ssh -L 4200:localhost:4200 user@your-remote-server

# Then open http://localhost:4200 in your local browser
```

**Option 2: Use the helper script**
```bash
# From your local machine
./scripts/connect_prefect_ui.sh user@your-remote-server
```

**Option 3: Configure Prefect for remote access**
```bash
# On remote server, start Prefect with:
prefect server start --host 0.0.0.0 --port 4200

# Then access via: http://your-server-ip:4200
# (requires firewall/security group configuration)
```

## 🔧 Configuration Options

### Token Management
```python
# In .env file
TOKEN_REFRESH_BUFFER_MINUTES=10  # Refresh 10 minutes before expiry
```

### Data Extraction
```python
# Customize in flow parameters
max_pages=100                    # Maximum API pages to fetch
after_date="2024-01-01"         # Filter activities after date
before_date="2024-12-31"        # Filter activities before date
```

### Database Operations
```python
# Customize in flow parameters
table_name="activities"          # Target table name
if_exists="append"              # append, replace, or fail
remove_duplicates=True          # Remove duplicate activities
```

## 🚨 Troubleshooting

### Permission Issues (SSH/Remote Workspace)
```bash
# If you get "Permission denied" when activating virtual environment
./fix_permissions.sh

# If the above doesn't work, manually fix permissions:
chmod +x .venv/bin/*
chmod +x scripts/*.py
chmod +x *.sh

# Then activate:
source .venv/bin/activate
```

### Token Issues
```bash
# Check token status
python -c "from src.utils import load_tokens, is_token_expired; tokens = load_tokens(); print(f'Expired: {is_token_expired(tokens[\"expires_at\"])}')"

# Force token refresh
python -c "from src.flows.token_management import token_refresh_flow; print(token_refresh_flow(force_refresh=True))"
```

### Database Connection
```bash
# Test database connection
python -c "from src.flows.database_operations import create_database_connection; create_database_connection()"
```

### Flow Debugging
```bash
# Run flows with detailed logging
PREFECT_LOGGING_LEVEL=DEBUG python -m src.flows.main_pipeline
```

## 📊 Data Schema

The transformed data includes:

| Column | Type | Description |
|--------|------|-------------|
| activity_id | Int64 | Unique activity identifier |
| activity_name | Categorical | Activity name |
| distance_km | Float | Distance in kilometers |
| moving_time_hr | Float | Moving time in hours |
| sport_type | Categorical | Type of activity |
| start_date_local | Datetime | Local start time |
| activity_hour | Int | Hour of day (0-23) |
| activity_weekday | Int | Day of week (1-7) |
| activity_year | Int | Year |
| activity_month | Int | Month |

## 🔮 Future Enhancements

- **Data Quality Monitoring**: Automated data quality checks
- **Advanced Analytics**: Real-time insights and trend analysis
- **Notification System**: Alerts for pipeline failures or interesting patterns
- **API Rate Limiting**: Intelligent rate limiting for API calls
- **Data Versioning**: Track data changes over time
