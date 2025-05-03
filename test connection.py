# Importing libraries
from sqlalchemy import create_engine

# Create SQLAlchemy engine
connection_string = 'mysql+mysqlconnector://strava_db_user:StravaConnect@localhost:3306/strava_db'
engine = create_engine(connection_string, echo=True)

# Test connection to the database
try:
    with engine.connect() as conn:
        print("✅ Connected successfully!")
except Exception as e:
    print(f"❌ Connection failed: {e}")

# Push data from Strava to the database

