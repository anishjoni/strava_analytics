#!/usr/bin/env python3
"""Deploy flows to local Prefect server."""

import os
import sys

def main():
    """Deploy flows to local Prefect server."""
    print("🏠 Deploying to Local Prefect Server")
    print("=" * 40)
    
    # Set environment for local server
    os.environ['PREFECT_API_URL'] = 'http://localhost:4200/api'
    os.environ['PREFECT_UI_URL'] = 'http://localhost:4200'
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    print("🔧 Environment configured for local server")
    print("📋 Deploying all flows from prefect.yaml...")
    print("-" * 40)
    
    # Deploy using os.system to avoid encoding issues
    result = os.system('prefect deploy --all')
    
    if result == 0:
        print("\n✅ Deployment successful!")
        print("\n📋 Next Steps:")
        print("1. Make sure Prefect server is running: prefect server start")
        print("2. Start worker: python worker_venv.py")
        print("3. Monitor at: http://localhost:4200")
        print("\n🧪 Test a deployment:")
        print("   prefect deployment run 'token-management-hourly'")
    else:
        print("\n❌ Deployment failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Prefect server is running: prefect server start")
        print("2. Check environment variables are set correctly")
        print("3. Verify you're in the project directory")

if __name__ == "__main__":
    main()
