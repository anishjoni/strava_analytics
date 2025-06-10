#!/usr/bin/env python3
"""Prefect worker startup that ensures virtual environment is active."""

import os
import sys
import subprocess

def find_prefect():
    """Find the prefect executable."""
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        # We're in a virtual environment
        if sys.platform == 'win32':
            prefect_path = os.path.join(sys.prefix, 'Scripts', 'prefect.exe')
        else:
            prefect_path = os.path.join(sys.prefix, 'bin', 'prefect')
        
        if os.path.exists(prefect_path):
            return prefect_path
    
    # Try to find prefect in PATH
    try:
        result = subprocess.run(['where', 'prefect'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except:
        pass
    
    return None

def main():
    """Start Prefect worker."""
    print("🚀 Starting Prefect Worker (Virtual Environment)")
    print("=" * 45)
    
    # Set environment for UTF-8
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['PYTHONLEGACYWINDOWSSTDIO'] = '1'
    
    # Clear any Prefect environment overrides
    os.environ.pop('PREFECT_API_URL', None)
    os.environ.pop('PREFECT_UI_URL', None)
    
    print("🔧 Environment configured")
    
    # Find prefect executable
    prefect_exe = find_prefect()
    if not prefect_exe:
        print("❌ Could not find prefect executable")
        print("📋 Make sure you're in the virtual environment:")
        print("   .\\venv\\Scripts\\Activate.ps1")
        return False
    
    print(f"✅ Found prefect at: {prefect_exe}")
    print("📋 Starting worker for 'default-agent-pool'")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 45)
    
    # Start the worker
    try:
        subprocess.run([prefect_exe, 'worker', 'start', '--pool', 'default-agent-pool'])
    except KeyboardInterrupt:
        print("\n⏹️  Worker stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
