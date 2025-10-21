"""
Environment configuration for Advanced LOGI-BOT AI Features.

Set up your Google Cloud API credentials and other advanced features here.
"""

import os

# ===================== GOOGLE CLOUD CONFIGURATION =====================
# Set your Google Cloud API key
# You can get this from: https://console.cloud.google.com/apis/credentials

# Method 1: Set as environment variable (recommended for production)
GOOGLE_CLOUD_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY', '')

# Method 2: Set directly here (for development only - don't commit to git!)
# GOOGLE_CLOUD_API_KEY = "your-google-cloud-api-key-here"

# Google Cloud Project Configuration
GOOGLE_CLOUD_PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'leadership-board-api')
GOOGLE_CLOUD_REGION = os.getenv('GOOGLE_CLOUD_REGION', 'us-central1')

# Google Sheets Configuration
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID', '1qcdOOAGJ50HfWJFlrQ3WUcrq0kjSUauVt5eBQAtGkHw')

# ===================== COMPOSIO CONFIGURATION =====================
# Composio API key for tool integrations
COMPOSIO_API_KEY = os.getenv('COMPOSIO_API_KEY', '')

# Tool-specific configurations
ASANA_WORKSPACE_ID = os.getenv('ASANA_WORKSPACE_ID', '')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
OUTLOOK_ACCOUNT = os.getenv('OUTLOOK_ACCOUNT', '')

# ===================== AI FEATURES CONFIGURATION =====================
# Enable/disable specific AI features
ENABLE_MULTILINGUAL_COMMUNICATION = True
ENABLE_DOCUMENT_INTELLIGENCE = True
ENABLE_VOICE_COMMANDS = True
ENABLE_SENTIMENT_ANALYSIS = True
ENABLE_PREDICTIVE_ANALYTICS = True
ENABLE_SMART_DOCUMENT_GENERATION = True
ENABLE_INTELLIGENT_WORKFLOWS = True

# Supported languages for multilingual features
SUPPORTED_LANGUAGES = [
    'es',  # Spanish
    'fr',  # French
    'de',  # German
    'zh',  # Chinese (Simplified)
    'ja',  # Japanese
    'it',  # Italian
    'pt',  # Portuguese
    'ko',  # Korean
    'ar',  # Arabic
    'hi',  # Hindi
]

# Voice command configuration
VOICE_COMMAND_LANGUAGE = 'en-US'
VOICE_RESPONSE_VOICE = 'en-US-Neural2-F'  # Google Text-to-Speech voice

# Document processing settings
MAX_DOCUMENT_SIZE_MB = 10
SUPPORTED_DOCUMENT_FORMATS = ['jpg', 'jpeg', 'png', 'pdf', 'tiff']

# Predictive analytics settings
DEFAULT_PREDICTION_TIMEFRAME_DAYS = 30
MAX_PREDICTION_TIMEFRAME_DAYS = 365

# ===================== SETUP INSTRUCTIONS =====================
"""
SETUP INSTRUCTIONS FOR ADVANCED AI FEATURES:

1. GOOGLE CLOUD SETUP:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing one
   - Enable the following APIs:
     * Cloud Translation API
     * Cloud Vision API  
     * Cloud Text-to-Speech API
     * Cloud Speech-to-Text API
     * Natural Language AI API
   - Create API credentials:
     * Go to APIs & Services > Credentials
     * Click "Create Credentials" > "API Key"
     * Copy the API key

2. SET ENVIRONMENT VARIABLES:
   # Windows (PowerShell):
   $env:GOOGLE_CLOUD_API_KEY="your-api-key-here"
   $env:GOOGLE_CLOUD_PROJECT_ID="your-project-id"
   
   # Linux/Mac:
   export GOOGLE_CLOUD_API_KEY="your-api-key-here"
   export GOOGLE_CLOUD_PROJECT_ID="your-project-id"

3. COMPOSIO SETUP (Optional):
   - Sign up at https://composio.dev/
   - Get your API key from dashboard
   - Set: $env:COMPOSIO_API_KEY="your-composio-key"

4. TEST THE SETUP:
   - Run: python test_ai_features.py
   - Check that all APIs are accessible

5. AVAILABLE AI FEATURES:

   🌍 MULTILINGUAL COMMUNICATION:
   POST /api/agent/ai/multilingual-alert/
   - Send supplier alerts in multiple languages
   - Auto-translate emergency communications
   - Support for 10+ languages

   📄 DOCUMENT INTELLIGENCE:
   POST /api/agent/ai/analyze-document/
   - OCR for invoices, contracts, shipping docs
   - Extract key data automatically
   - AI-powered content analysis

   🎤 VOICE COMMANDS:
   POST /api/agent/ai/voice-command/
   - "Check stock for steel rods"
   - "Create alert for limestone shortage" 
   - "Schedule emergency meeting"

   📊 PREDICTIVE ANALYTICS:
   GET /api/agent/ai/predictive-analytics/
   - Demand forecasting
   - Supply chain risk analysis
   - Inventory optimization recommendations

   📋 SMART DOCUMENT GENERATION:
   POST /api/agent/ai/generate-document/
   - Auto-generate supplier contracts
   - Create purchase orders
   - Executive summary reports

   ⚡ INTELLIGENT WORKFLOWS:
   POST /api/agent/ai/create-workflow/
   - Self-adapting automation
   - Cross-platform orchestration
   - AI-powered decision making

6. FRONTEND INTEGRATION:
   
   // Voice Command Example
   const audioBlob = await recordAudio();
   const audioBase64 = await blobToBase64(audioBlob);
   
   const response = await fetch('/api/agent/ai/voice-command/', {
     method: 'POST',
     headers: {
       'Authorization': `Bearer ${token}`,
       'Content-Type': 'application/json'
     },
     body: JSON.stringify({
       audio_data: audioBase64,
       context: { location: 'warehouse_A' }
     })
   });

   // Document Analysis Example  
   const fileReader = new FileReader();
   fileReader.onload = async () => {
     const imageBase64 = fileReader.result.split(',')[1];
     
     const response = await fetch('/api/agent/ai/analyze-document/', {
       method: 'POST',
       body: JSON.stringify({
         image_data: imageBase64,
         document_type: 'invoice',
         metadata: { supplier: 'ABC Corp' }
       })
     });
   };

7. COST CONSIDERATIONS:
   - Google Cloud APIs have usage-based pricing
   - Translation: ~$20 per 1M characters
   - Vision OCR: ~$1.50 per 1,000 images
   - Text-to-Speech: ~$4 per 1M characters
   - Start with free tier limits for testing

8. SECURITY NOTES:
   - Never commit API keys to version control
   - Use environment variables in production
   - Restrict API keys to specific services
   - Monitor usage in Google Cloud Console
"""

# ===================== VALIDATION =====================
def validate_ai_configuration():
    """Validate that AI features are properly configured."""
    errors = []
    warnings = []
    
    if not GOOGLE_CLOUD_API_KEY:
        errors.append("GOOGLE_CLOUD_API_KEY is not set")
    
    if not GOOGLE_CLOUD_PROJECT_ID:
        warnings.append("GOOGLE_CLOUD_PROJECT_ID is not set - using default")
    
    if not COMPOSIO_API_KEY:
        warnings.append("COMPOSIO_API_KEY is not set - some integrations will be limited")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'features_available': {
            'google_cloud': bool(GOOGLE_CLOUD_API_KEY),
            'composio_tools': bool(COMPOSIO_API_KEY),
            'multilingual': ENABLE_MULTILINGUAL_COMMUNICATION and bool(GOOGLE_CLOUD_API_KEY),
            'document_ai': ENABLE_DOCUMENT_INTELLIGENCE and bool(GOOGLE_CLOUD_API_KEY),
            'voice_commands': ENABLE_VOICE_COMMANDS and bool(GOOGLE_CLOUD_API_KEY),
            'predictive_analytics': ENABLE_PREDICTIVE_ANALYTICS,
        }
    }

if __name__ == "__main__":
    # Test configuration when run directly
    config = validate_ai_configuration()
    print("AI Features Configuration Status:")
    print(f"Valid: {config['valid']}")
    if config['errors']:
        print(f"Errors: {config['errors']}")
    if config['warnings']:
        print(f"Warnings: {config['warnings']}")
    print(f"Available Features: {config['features_available']}")