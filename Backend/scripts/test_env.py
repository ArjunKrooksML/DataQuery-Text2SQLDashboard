#!/usr/bin/env python3
"""
Test script to verify environment variables are loaded correctly.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

print("🔍 Environment Variable Test")
print("=" * 50)
print(f"📁 Environment file path: {env_path}")
print(f"📁 Environment file exists: {env_path.exists()}")

print("\n📋 Environment Variables:")
print("-" * 30)

# Check key environment variables
env_vars = [
    'DATABASE_URL',
    'DATABASE_URL_ASYNC', 
    'MONGODB_URL',
    'MONGODB_DATABASE',
    'SECRET_KEY',
    'OPENAI_API_KEY',
    'REDIS_URL'
]

for var in env_vars:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'KEY' in var or 'SECRET' in var:
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: Not set")

print("\n🔧 Testing Settings Import:")
print("-" * 30)

try:
    from app.core.config import settings
    print(f"✅ Settings imported successfully")
    print(f"✅ DATABASE_URL from settings: {settings.DATABASE_URL}")
    print(f"✅ MONGODB_DATABASE from settings: {settings.MONGODB_DATABASE}")
except Exception as e:
    print(f"❌ Error importing settings: {e}")

print("\n" + "=" * 50)
print("✅ Environment test completed!") 