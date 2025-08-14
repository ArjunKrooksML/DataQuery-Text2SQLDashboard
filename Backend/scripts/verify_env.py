#!/usr/bin/env python3
"""
Simple script to verify environment variables are loaded correctly.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

print("🔍 Environment Variable Verification")
print("=" * 50)
print(f"📁 Current working directory: {os.getcwd()}")
print(f"📁 Script location: {Path(__file__).parent}")
print(f"📁 Expected .env location: {Path(__file__).parent / '.env'}")

# Check if .env file exists
env_file = Path(__file__).parent / '.env'
print(f"📁 .env file exists: {env_file.exists()}")

if env_file.exists():
    print(f"📁 .env file size: {env_file.stat().st_size} bytes")
    
    # Show first few lines of .env (without sensitive data)
    with open(env_file, 'r') as f:
        lines = f.readlines()
        print(f"📁 .env file has {len(lines)} lines")
        for i, line in enumerate(lines[:5]):  # Show first 5 lines
            if line.strip() and not line.strip().startswith('#'):
                key = line.split('=')[0] if '=' in line else 'unknown'
                print(f"   Line {i+1}: {key}=***")
else:
    print("❌ .env file not found!")

print("\n🔧 Testing Settings Import:")
print("-" * 30)

try:
    from app.core.config import settings
    print(f"✅ Settings imported successfully")
    print(f"✅ DATABASE_URL: {settings.DATABASE_URL[:50]}...")
    print(f"✅ OPENAI_API_KEY: {'Set' if settings.OPENAI_API_KEY else 'Not set'}")
    print(f"✅ MONGODB_DATABASE: {settings.MONGODB_DATABASE}")
except Exception as e:
    print(f"❌ Error importing settings: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("✅ Environment verification completed!") 