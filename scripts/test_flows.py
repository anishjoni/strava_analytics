#!/usr/bin/env python3
"""Test script for Strava analytics flows."""

import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported."""
    print("📦 Testing Imports...")
    
    try:
        from src.flows.token_management import token_refresh_flow, check_token_status
        from src.flows.data_extraction import strava_data_extraction_flow
        from src.flows.data_transformation import strava_data_transformation_flow
        from src.flows.database_operations import strava_database_operations_flow
        from src.flows.main_pipeline import strava_analytics_pipeline_flow
        
        print("   ✅ All imports successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False


def test_configuration():
    """Test configuration loading."""
    print("⚙️ Testing Configuration...")
    
    try:
        from src.config import settings
        
        print(f"   Database URL: {settings.database_url}")
        print(f"   Tokens path: {settings.tokens_path}")
        print(f"   Data directory: {settings.data_dir}")
        
        print("   ✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False


def main():
    """Run basic tests."""
    print("🧪 Testing Strava Analytics Setup")
    print("=" * 40)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 Test Summary:")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        print("\nYou can now:")
        print("1. Set up your .env file with Strava credentials")
        print("2. Run token authentication")
        print("3. Start Prefect server and deploy flows")
        return 0
    else:
        print("⚠️ Some tests failed. Check the logs above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
