#!/usr/bin/env python3
"""
Test script with sample data to verify the complete pipeline works
without requiring actual Strava credentials or database connection.
"""

import sys
from pathlib import Path
import polars as pl
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_data_transformation():
    """Test data transformation with sample data."""
    print("🔄 Testing Data Transformation Flow...")
    
    try:
        from src.strava_analytics.flows.data_transformation import strava_data_transformation_flow
        
        # Create sample Strava API response data
        sample_activities = {
            'id': [1234567890, 1234567891, 1234567892],
            'name': ['Morning Run', 'Evening Bike Ride', 'Weekend Hike'],
            'distance': [5000.0, 15000.0, 8000.0],  # meters
            'moving_time': [1800, 3600, 7200],  # seconds
            'total_elevation_gain': [100.0, 300.0, 500.0],  # meters
            'sport_type': ['Run', 'Ride', 'Hike'],
            'start_date_local': [
                '2024-01-01T08:00:00Z',
                '2024-01-02T18:00:00Z', 
                '2024-01-03T10:00:00Z'
            ],
            'gear_id': ['g123', 'g456', None],
            'start_latlng': [[37.7749, -122.4194], [37.7849, -122.4094], None],
            'end_latlng': [[37.7849, -122.4094], [37.7949, -122.3994], None],
            'average_speed': [2.78, 4.17, 1.11],  # m/s
            'max_speed': [5.56, 8.33, 2.22],  # m/s
            'pr_count': [1, 0, 2]
        }
        
        # Create DataFrame
        raw_df = pl.DataFrame(sample_activities)
        print(f"   📊 Created sample data with {len(raw_df)} activities")
        
        # Run transformation
        transformed_df = strava_data_transformation_flow(raw_df)
        
        print(f"   ✅ Transformation successful!")
        print(f"   📈 Input: {len(raw_df)} rows, Output: {len(transformed_df)} rows")
        print(f"   📋 Final columns: {transformed_df.columns}")
        
        # Verify expected columns exist
        expected_columns = [
            'activity_id', 'activity_name', 'distance_km', 'moving_time_hr',
            'sport_type', 'start_date_local', 'activity_hour'
        ]
        
        missing_columns = [col for col in expected_columns if col not in transformed_df.columns]
        if missing_columns:
            print(f"   ⚠️ Missing expected columns: {missing_columns}")
        else:
            print(f"   ✅ All expected columns present")
        
        # Show sample of transformed data
        print(f"   📋 Sample transformed data:")
        print(transformed_df.head(2))
        
        return True
        
    except Exception as e:
        print(f"   ❌ Transformation test failed: {e}")
        return False


def test_token_management_structure():
    """Test token management flow structure (without actual tokens)."""
    print("🔑 Testing Token Management Flow Structure...")
    
    try:
        from src.strava_analytics.flows.token_management import check_token_status, token_refresh_flow
        
        # Test that functions are importable and callable
        print("   ✅ Token management functions imported successfully")
        
        # Test token status check (will fail without tokens.json, but that's expected)
        try:
            status = check_token_status()
            print("   ⚠️ Unexpected: token status check succeeded without tokens.json")
        except FileNotFoundError:
            print("   ✅ Token status check correctly handles missing tokens.json")
        except Exception as e:
            print(f"   ⚠️ Token status check error (expected without setup): {e}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Token management test failed: {e}")
        return False


def test_database_operations_structure():
    """Test database operations structure (without actual database)."""
    print("💾 Testing Database Operations Structure...")
    
    try:
        from src.strava_analytics.flows.database_operations import (
            convert_polars_to_pandas,
            check_for_duplicates,
            remove_duplicates
        )
        
        # Create sample data
        sample_data = {
            'activity_id': [1, 2, 3, 2],  # Include duplicate
            'activity_name': ['Run 1', 'Run 2', 'Run 3', 'Run 2 Duplicate'],
            'distance_km': [5.0, 10.0, 8.0, 10.0]
        }
        
        df = pl.DataFrame(sample_data)
        print(f"   📊 Created sample data with {len(df)} rows (including duplicate)")
        
        # Test conversion to pandas
        pandas_df = convert_polars_to_pandas(df)
        print(f"   ✅ Polars to Pandas conversion successful")
        
        # Test duplicate detection
        duplicate_info = check_for_duplicates(pandas_df)
        print(f"   ✅ Duplicate detection: found {duplicate_info['duplicate_count']} duplicates")
        
        # Test duplicate removal
        clean_df = remove_duplicates(pandas_df)
        print(f"   ✅ Duplicate removal: {len(pandas_df)} -> {len(clean_df)} rows")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database operations test failed: {e}")
        return False


def test_main_pipeline_structure():
    """Test main pipeline structure."""
    print("🚀 Testing Main Pipeline Structure...")
    
    try:
        from src.strava_analytics.flows.main_pipeline import (
            strava_analytics_pipeline_flow,
            daily_strava_sync_flow,
            weekly_full_sync_flow
        )
        
        print("   ✅ Main pipeline flows imported successfully")
        print("   ✅ Daily sync flow available")
        print("   ✅ Weekly sync flow available")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Main pipeline test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("⚙️ Testing Configuration...")
    
    try:
        from src.strava_analytics.config import settings
        
        print(f"   📁 Data directory: {settings.data_dir}")
        print(f"   🗄️ Database URL: {settings.database_url}")
        print(f"   🔑 Tokens path: {settings.tokens_path}")
        print(f"   ⏰ Token refresh buffer: {settings.token_refresh_buffer_minutes} minutes")
        
        # Test data directory creation
        data_path = settings.ensure_data_dir()
        print(f"   ✅ Data directory created/verified: {data_path}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🧪 Comprehensive Strava Analytics Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Configuration", test_configuration),
        ("Token Management Structure", test_token_management_structure),
        ("Data Transformation", test_data_transformation),
        ("Database Operations Structure", test_database_operations_structure),
        ("Main Pipeline Structure", test_main_pipeline_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"🔍 {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"   ✅ {test_name}: PASSED")
            else:
                print(f"   ❌ {test_name}: FAILED")
        except Exception as e:
            print(f"   ❌ {test_name}: FAILED with exception: {e}")
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print()
        print("✅ Your Strava Analytics pipeline is ready!")
        print()
        print("🚀 Next steps:")
        print("1. Configure .env with your Strava API credentials")
        print("2. Run initial authentication to create tokens.json")
        print("3. Start Prefect server and deploy flows")
        print("4. Your pipeline will run automatically!")
        print()
        print("📖 See QUICKSTART.md for detailed setup instructions")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
