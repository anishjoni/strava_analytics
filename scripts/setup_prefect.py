#!/usr/bin/env python3
"""Setup script for Prefect deployments and initial configuration."""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import settings


def run_command(command: str, description: str = None):
    """Run a shell command and handle errors."""
    if description:
        print(f"🔧 {description}")
    
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        
        return result
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stdout:
            print(f"   Stdout: {e.stdout}")
        if e.stderr:
            print(f"   Stderr: {e.stderr}")
        raise


def setup_environment():
    """Setup environment and data directories."""
    print("📁 Setting up environment...")
    
    # Create data directory
    data_dir = settings.ensure_data_dir()
    print(f"   Created data directory: {data_dir}")
    
    # Check for .env file
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        print("   📝 Creating .env file from .env.example")
        print("   ⚠️ Please edit .env file with your actual credentials")
        
        with open(env_example) as f:
            content = f.read()
        
        with open(env_file, 'w') as f:
            f.write(content)


def main():
    """Main setup function."""
    print("🚀 Setting up Strava Analytics with Prefect")
    print("=" * 50)
    
    try:
        # Setup environment
        setup_environment()
        
        print("\n" + "=" * 50)
        print("✅ Basic setup completed!")
        print("\nNext steps:")
        print("1. Edit .env file with your Strava API credentials")
        print("2. Run initial authentication to create tokens.json")
        print("3. Start Prefect server: prefect server start")
        print("4. Deploy flows: prefect deploy --all")
        print("5. Start a Prefect worker: prefect worker start --pool default-agent-pool")
        print("6. View the Prefect UI at: http://localhost:4200")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
