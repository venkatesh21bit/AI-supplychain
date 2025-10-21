"""
Quick verification script to check if all configurations are properly set.
Run this to verify your Google Cloud and Composio setup.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def print_status(check_name, status, message=""):
    """Print colored status messages."""
    symbols = {"✅": "PASS", "⚠️": "WARN", "❌": "FAIL"}
    status_symbol = "✅" if status == "pass" else "⚠️" if status == "warn" else "❌"
    print(f"{status_symbol} {check_name}: {message}")

def verify_environment_variables():
    """Check if all required environment variables are set."""
    print("\n" + "="*60)
    print("🔍 CHECKING ENVIRONMENT VARIABLES")
    print("="*60)
    
    required_vars = {
        'GOOGLE_CLOUD_API_KEY': os.getenv('GOOGLE_CLOUD_API_KEY'),
        'GOOGLE_CLOUD_PROJECT_ID': os.getenv('GOOGLE_CLOUD_PROJECT_ID'),
        'COMPOSIO_API_KEY': os.getenv('COMPOSIO_API_KEY'),
        'GOOGLE_SHEET_ID': os.getenv('GOOGLE_SHEET_ID'),
    }
    
    all_set = True
    for var_name, var_value in required_vars.items():
        if var_value:
            masked_value = var_value[:8] + "..." if len(var_value) > 8 else var_value
            print_status(var_name, "pass", f"Set ({masked_value})")
        else:
            print_status(var_name, "fail", "NOT SET")
            all_set = False
    
    return all_set

def verify_google_cloud_api():
    """Test Google Cloud API connectivity."""
    print("\n" + "="*60)
    print("🌐 TESTING GOOGLE CLOUD API")
    print("="*60)
    
    try:
        from google.cloud import translate_v2 as translate
        
        api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID')
        
        if not api_key:
            print_status("Google Cloud API", "fail", "API key not found")
            return False
        
        # Test translation API
        translate_client = translate.Client(api_key=api_key)
        result = translate_client.translate('Hello', target_language='es')
        
        print_status("Translation API", "pass", f"Working! Test: '{result['translatedText']}'")
        print_status("Project ID", "pass", f"{project_id}")
        return True
        
    except Exception as e:
        print_status("Google Cloud API", "fail", f"Error: {str(e)}")
        return False

def verify_composio_api():
    """Test Composio API connectivity."""
    print("\n" + "="*60)
    print("🔗 TESTING COMPOSIO API")
    print("="*60)
    
    try:
        import requests
        
        api_key = os.getenv('COMPOSIO_API_KEY')
        if not api_key:
            print_status("Composio API", "fail", "API key not found")
            return False
        
        # Test Composio API
        url = "https://backend.composio.dev/api/v1/apps"
        headers = {"X-API-KEY": api_key}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            apps = response.json()
            app_count = len(apps.get('items', []))
            print_status("Composio API", "pass", f"Connected! {app_count} apps available")
            return True
        else:
            print_status("Composio API", "fail", f"Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print_status("Composio API", "fail", f"Error: {str(e)}")
        return False

def verify_google_sheets():
    """Check Google Sheets configuration."""
    print("\n" + "="*60)
    print("📊 CHECKING GOOGLE SHEETS CONFIGURATION")
    print("="*60)
    
    sheet_id = os.getenv('GOOGLE_SHEET_ID')
    
    if sheet_id:
        sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/edit"
        print_status("Sheet ID", "pass", f"Configured")
        print(f"   📎 URL: {sheet_url}")
        print(f"   ⚠️  Remember to share this sheet with your service account!")
        return True
    else:
        print_status("Sheet ID", "warn", "Not configured (optional)")
        return False

def verify_ai_config():
    """Load and validate ai_config.py."""
    print("\n" + "="*60)
    print("🤖 CHECKING AI CONFIGURATION")
    print("="*60)
    
    try:
        import ai_config
        
        config = ai_config.validate_ai_configuration()
        
        print_status("Configuration Valid", "pass" if config['valid'] else "fail", "")
        
        if config['errors']:
            for error in config['errors']:
                print_status("Error", "fail", error)
        
        if config['warnings']:
            for warning in config['warnings']:
                print_status("Warning", "warn", warning)
        
        print("\n📋 Available Features:")
        for feature, available in config['features_available'].items():
            status = "pass" if available else "warn"
            feature_name = feature.replace('_', ' ').title()
            print_status(f"   {feature_name}", status, "Available" if available else "Unavailable")
        
        return config['valid']
        
    except Exception as e:
        print_status("AI Config", "fail", f"Error loading: {str(e)}")
        return False

def verify_database():
    """Check database configuration."""
    print("\n" + "="*60)
    print("💾 CHECKING DATABASE")
    print("="*60)
    
    db_path = project_root / "db.sqlite3"
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        print_status("Database File", "pass", f"Found (Size: {size_mb:.2f} MB)")
        return True
    else:
        print_status("Database File", "warn", "Not found - run migrations")
        return False

def main():
    """Run all verification checks."""
    print("\n" + "="*70)
    print("🚀 LOGI-BOT CONFIGURATION VERIFICATION")
    print("="*70)
    print(f"📁 Project: {project_root}")
    print(f"📅 Date: October 20, 2025\n")
    
    results = {
        'Environment Variables': verify_environment_variables(),
        'Google Cloud API': verify_google_cloud_api(),
        'Composio API': verify_composio_api(),
        'Google Sheets': verify_google_sheets(),
        'AI Configuration': verify_ai_config(),
        'Database': verify_database(),
    }
    
    # Summary
    print("\n" + "="*70)
    print("📊 VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for check, result in results.items():
        status = "pass" if result else "warn"
        print_status(check, status, "")
    
    print(f"\n✅ Passed: {passed}/{total} checks")
    
    if passed == total:
        print("\n🎉 ALL CHECKS PASSED! Your system is ready to go!")
        print("\n📋 Next Steps:")
        print("   1. Start backend: python manage.py runserver")
        print("   2. Start frontend: cd Vendor-frontend && npm run dev")
        print("   3. Visit: http://localhost:3000")
    else:
        print("\n⚠️  Some checks failed. Please review the configuration.")
        print("   See MANUAL_CONFIGURATION_CHECKLIST.md for details.")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
