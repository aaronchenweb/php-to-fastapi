#!/usr/bin/env python3
"""Quick test script for Gemini API configuration."""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_api():
    """Test Gemini API configuration."""
    
    # Get configuration
    api_key = os.getenv('LLM_API_KEY')
    model = os.getenv('LLM_MODEL', 'gemini-2.0-flash')
    base_url = os.getenv('LLM_BASE_URL', 'https://generativelanguage.googleapis.com/v1beta')
    
    print("=== Gemini API Configuration Test ===")
    print(f"API Key: {'✓ Set' if api_key else '✗ Missing'}")
    print(f"Model: {model}")
    print(f"Base URL: {base_url}")
    
    if not api_key:
        print("❌ API key is missing!")
        return False
    
    # Clean base URL if needed
    if '/models/' in base_url and ':generateContent' in base_url:
        print("⚠️  Base URL contains model path, cleaning...")
        base_url = base_url.split('/models/')[0]
        print(f"Cleaned Base URL: {base_url}")
    
    # Construct test URL
    url = f'{base_url}/models/{model}:generateContent'
    print(f"Test URL: {url}")
    
    # Prepare test payload
    payload = {
        'contents': [{
            'role': 'user',
            'parts': [{'text': 'Say "Hello, API test successful!" if you can read this.'}]
        }],
        'generationConfig': {
            'maxOutputTokens': 100,
            'temperature': 0.1
        }
    }
    
    params = {'key': api_key}
    
    try:
        print("\n🔄 Testing API connection...")
        response = requests.post(url, params=params, json=payload, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and data['candidates']:
                content = data['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ API Test Successful!")
                print(f"Response: {content}")
                return True
            else:
                print(f"❌ No response generated: {data}")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False

def suggest_fixes():
    """Suggest common fixes for Gemini API issues."""
    print("\n=== Suggested Fixes ===")
    print("1. Make sure your .env file contains:")
    print("   LLM_API_KEY=your_actual_api_key")
    print("   LLM_PROVIDER=gemini")
    print("   LLM_MODEL=gemini-2.0-flash")
    print("   LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta")
    print()
    print("2. Verify your API key at: https://makersuite.google.com/app/apikey")
    print("3. Make sure the Gemini API is enabled in your Google Cloud Console")
    print("4. Check your API quotas and billing settings")

if __name__ == "__main__":
    success = test_gemini_api()
    
    if not success:
        suggest_fixes()
    
    print(f"\n{'✅ Configuration OK' if success else '❌ Configuration needs fixing'}")