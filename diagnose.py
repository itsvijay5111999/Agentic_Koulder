#!/usr/bin/env python3
"""
Diagnostic script to check if your setup is correct before deploying to Render.
Run with: python diagnose.py
"""

import os
import sys

def check_files():
    """Check if required files exist."""
    print("=" * 60)
    print("📁 CHECKING FILES")
    print("=" * 60)
    
    required_files = [
        "backend.py",
        "langgraph_chatbot.py",
        "stream_resume_bot_test.py",
        "requirements.txt",
    ]
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_imports():
    """Check if all imports work."""
    print("\n" + "=" * 60)
    print("📦 CHECKING IMPORTS")
    print("=" * 60)
    
    imports_ok = True
    
    # Check basic imports
    basic_imports = [
        ("streamlit", "Streamlit"),
        ("langchain", "LangChain"),
        ("langgraph", "LangGraph"),
        ("dotenv", "Python-dotenv"),
    ]
    
    for module, name in basic_imports:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError as e:
            print(f"✗ {name}: {e}")
            imports_ok = False
    
    # Check backend import
    print("\nChecking backend imports...")
    try:
        from backend import chatbot, retrieve_all_threads
        print("✓ backend.chatbot")
        print("✓ backend.retrieve_all_threads")
    except ImportError as e:
        print(f"✗ Backend import failed: {e}")
        imports_ok = False
    
    return imports_ok

def check_api_keys():
    """Check if API keys are set."""
    print("\n" + "=" * 60)
    print("🔑 CHECKING API KEYS")
    print("=" * 60)
    
    required_keys = {
        "GROQ_API_KEY": "Groq LLM (REQUIRED)",
        "SERPAPI_API_KEY": "SerpAPI Search (REQUIRED)",
    }
    
    optional_keys = {
        "YOUTUBE_API_KEY": "YouTube Search (optional)",
        "TAVILY_API_KEY": "Tavily Search (optional)",
    }
    
    missing_required = []
    
    print("\nRequired:")
    for key, desc in required_keys.items():
        has_key = os.getenv(key)
        status = "✓" if has_key else "✗"
        print(f"{status} {key}: {desc}")
        if not has_key:
            missing_required.append(key)
    
    print("\nOptional:")
    for key, desc in optional_keys.items():
        has_key = os.getenv(key)
        status = "✓" if has_key else "⊘"
        print(f"{status} {key}: {desc}")
    
    return len(missing_required) == 0, missing_required

def main():
    print("\n🔍 CHATBOT DEPLOYMENT DIAGNOSTIC\n")
    
    files_ok = check_files()
    imports_ok = check_imports()
    keys_ok, missing_keys = check_api_keys()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    all_good = files_ok and imports_ok and keys_ok
    
    if all_good:
        print("✓ Everything looks good! Ready to deploy.")
    else:
        print("✗ Issues found:\n")
        
        if not files_ok:
            print("  - Missing required files. Check current directory.")
        
        if not imports_ok:
            print("  - Missing Python dependencies. Run: pip install -r requirements.txt")
        
        if not keys_ok:
            print(f"  - Missing API keys: {', '.join(missing_keys)}")
            print("\n    To fix on Render:")
            print("    1. Go to your Render service → Environment")
            print("    2. Add the missing keys")
            print("    3. Redeploy")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
