"""
Test Translation Feature
Tests the Google Translate integration for input/output translation
"""

import requests
import json

# Configuration
MIDDLEWARE_URL = "http://localhost:5000"

def test_translate_api():
    """Test the translate API endpoint"""
    print("\n" + "="*50)
    print("🌐 Testing Translation API")
    print("="*50)
    
    test_cases = [
        {
            "text": "मेरी फसल में कीड़े लग गए हैं",
            "source_lang": "hi",
            "target_lang": "en",
            "description": "Hindi to English"
        },
        {
            "text": "What are the best crops for monsoon season?",
            "source_lang": "en",
            "target_lang": "hi",
            "description": "English to Hindi"
        },
        {
            "text": "నా పంట దిగుబడి ఎంత ఉంటుంది?",
            "source_lang": "te",
            "target_lang": "en",
            "description": "Telugu to English"
        },
        {
            "text": "How can I improve soil quality?",
            "source_lang": "en",
            "target_lang": "ta",
            "description": "English to Tamil"
        },
        {
            "text": "ಮಳೆಗಾಲದಲ್ಲಿ ಯಾವ ಬೆಳೆಗಳು ಉತ್ತಮ?",
            "source_lang": "kn",
            "target_lang": "en",
            "description": "Kannada to English"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test_case['description']}")
        print(f"   Original: {test_case['text']}")
        
        try:
            response = requests.post(
                f"{MIDDLEWARE_URL}/translate",
                json={
                    "text": test_case["text"],
                    "source_lang": test_case["source_lang"],
                    "target_lang": test_case["target_lang"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    translated = data["data"]["translated_text"]
                    detected = data["data"].get("detected_language", "unknown")
                    print(f"   ✅ Translated: {translated}")
                    print(f"   🔍 Detected Language: {detected}")
                else:
                    print(f"   ❌ Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print()


def test_multilingual_conversation():
    """Test a complete multilingual conversation flow"""
    print("\n" + "="*50)
    print("💬 Testing Multilingual Conversation Flow")
    print("="*50)
    
    # Simulate user asking question in Hindi
    user_query_hindi = "मेरी गेहूं की फसल का उत्पादन कैसे बढ़ाएं?"
    print(f"\n👤 User (Hindi): {user_query_hindi}")
    
    # Step 1: Translate to English
    print("\n🔄 Step 1: Translating to English...")
    try:
        translate_response = requests.post(
            f"{MIDDLEWARE_URL}/translate",
            json={
                "text": user_query_hindi,
                "source_lang": "hi",
                "target_lang": "en"
            },
            timeout=10
        )
        
        if translate_response.status_code == 200:
            data = translate_response.json()
            if data.get("success"):
                english_query = data["data"]["translated_text"]
                print(f"   ✅ English: {english_query}")
                
                # Step 2: Query the agent with English text
                print(f"\n🤖 Step 2: Querying AI Agent...")
                agent_response = requests.post(
                    f"{MIDDLEWARE_URL}/agent",
                    json={
                        "query": english_query,
                        "mode": "auto",
                        "max_iterations": 5
                    },
                    timeout=30
                )
                
                if agent_response.status_code == 200:
                    agent_data = agent_response.json()
                    if agent_data.get("success"):
                        english_answer = agent_data.get("final_answer") or agent_data.get("answer", "")
                        print(f"   ✅ Response (English): {english_answer[:200]}...")
                        
                        # Step 3: Translate response back to Hindi
                        print(f"\n🔄 Step 3: Translating response to Hindi...")
                        translate_back = requests.post(
                            f"{MIDDLEWARE_URL}/translate",
                            json={
                                "text": english_answer,
                                "source_lang": "en",
                                "target_lang": "hi"
                            },
                            timeout=10
                        )
                        
                        if translate_back.status_code == 200:
                            back_data = translate_back.json()
                            if back_data.get("success"):
                                hindi_answer = back_data["data"]["translated_text"]
                                print(f"   ✅ Response (Hindi): {hindi_answer[:200]}...")
                                print(f"\n🎉 Complete multilingual flow successful!")
                            else:
                                print(f"   ❌ Translation back failed: {back_data.get('error')}")
                        else:
                            print(f"   ❌ HTTP {translate_back.status_code}")
                    else:
                        print(f"   ❌ Agent error: {agent_data.get('error')}")
                else:
                    print(f"   ❌ HTTP {agent_response.status_code}")
            else:
                print(f"   ❌ Translation failed: {data.get('error')}")
        else:
            print(f"   ❌ HTTP {translate_response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")


def test_supported_languages():
    """Test multiple supported Indian languages"""
    print("\n" + "="*50)
    print("🇮🇳 Testing Supported Indian Languages")
    print("="*50)
    
    languages = {
        "hi": "नमस्ते, मुझे कृषि में सहायता चाहिए",  # Hindi
        "te": "నమస్కారం, నాకు వ్యవసాయంలో సహాయం కావాలి",  # Telugu
        "ta": "வணக்கம், எனக்கு விவசாயத்தில் உதவி தேவை",  # Tamil
        "kn": "ನಮಸ್ಕಾರ, ನನಗೆ ಕೃಷಿಯಲ್ಲಿ ಸಹಾಯ ಬೇಕು",  # Kannada
        "ml": "നമസ്കാരം, എനിക്ക് കൃഷിയിൽ സഹായം വേണം",  # Malayalam
        "mr": "नमस्कार, मला शेतीत मदत हवी आहे",  # Marathi
        "bn": "নমস্কার, আমার কৃষিতে সাহায্য দরকার",  # Bengali
        "gu": "નમસ્તે, મને ખેતીમાં મદદ જોઈએ છે",  # Gujarati
        "pa": "ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਮੈਨੂੰ ਖੇਤੀ ਵਿੱਚ ਮਦਦ ਦੀ ਲੋੜ ਹੈ",  # Punjabi
    }
    
    for lang_code, greeting in languages.items():
        print(f"\n🌐 Testing {lang_code.upper()}: {greeting}")
        
        try:
            response = requests.post(
                f"{MIDDLEWARE_URL}/translate",
                json={
                    "text": greeting,
                    "source_lang": lang_code,
                    "target_lang": "en"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    translated = data["data"]["translated_text"]
                    print(f"   ✅ English: {translated}")
                else:
                    print(f"   ❌ Error: {data.get('error')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")


def main():
    """Run all translation tests"""
    print("\n" + "="*70)
    print("🌍 ShizishanGPT - Translation Feature Test Suite")
    print("="*70)
    print("\nThis test suite validates:")
    print("  1. ✅ Translation API endpoint functionality")
    print("  2. ✅ Support for multiple Indian languages")
    print("  3. ✅ Bidirectional translation (to/from English)")
    print("  4. ✅ Complete multilingual conversation flow")
    print("\n" + "="*70)
    
    try:
        # Test 1: Basic translation API
        test_translate_api()
        
        # Test 2: Supported languages
        test_supported_languages()
        
        # Test 3: Complete conversation flow
        test_multilingual_conversation()
        
        print("\n" + "="*70)
        print("✅ All translation tests completed!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test suite failed: {str(e)}")


if __name__ == "__main__":
    main()
