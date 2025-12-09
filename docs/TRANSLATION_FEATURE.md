# 🌍 Google Translate Integration - ShizishanGPT

## Overview

ShizishanGPT now includes **Google Translate** integration to support multilingual farmers across India and beyond. Users can interact with the AI assistant in their native language, with automatic translation of both input queries and output responses.

## ✨ Features

### 1. **Language Selection**
- Choose from 10+ supported languages including major Indian languages
- Visual language indicator in the chat header
- Persistent language preference

### 2. **Auto-Translate Input**
- Automatically translate user queries from their selected language to English
- Seamless processing by the AI backend
- Visual indicator showing when translation occurred

### 3. **Auto-Translate Output**
- Automatically translate AI responses from English back to user's language
- Maintains context and accuracy
- Shows translation status on messages

### 4. **Supported Languages**

| Language | Code | Example |
|----------|------|---------|
| English | `en` | Hello, how are you? |
| हिन्दी (Hindi) | `hi` | नमस्ते, आप कैसे हैं? |
| తెలుగు (Telugu) | `te` | నమస్కారం, మీరు ఎలా ఉన్నారు? |
| தமிழ் (Tamil) | `ta` | வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்? |
| ಕನ್ನಡ (Kannada) | `kn` | ನಮಸ್ಕಾರ, ನೀವು ಹೇಗಿದ್ದೀರಿ? |
| മലയാളം (Malayalam) | `ml` | നമസ്കാരം, സുഖമാണോ? |
| मराठी (Marathi) | `mr` | नमस्कार, तुम्ही कसे आहात? |
| বাংলা (Bengali) | `bn` | নমস্কার, আপনি কেমন আছেন? |
| ગુજરાતી (Gujarati) | `gu` | નમસ્તે, તમે કેવા છો? |
| ਪੰਜਾਬੀ (Punjabi) | `pa` | ਸਤ ਸ੍ਰੀ ਅਕਾਲ, ਤੁਸੀਂ ਕਿਵੇਂ ਹੋ? |

## 🚀 How to Use

### Frontend (React UI)

1. **Open Settings**
   - Click the "Settings" button in the sidebar
   - Or use the settings icon in the header

2. **Select Your Language**
   - Choose your preferred language from the dropdown
   - The interface will show your selected language code

3. **Enable Auto-Translation**
   - Toggle "Auto-translate Input" to translate your messages to English
   - Toggle "Auto-translate Output" to receive responses in your language
   - Both can be enabled independently

4. **Start Chatting**
   - Type your query in your native language
   - Watch the translation indicator when enabled
   - Receive responses in your preferred language

### Visual Indicators

- **Language Badge**: Shows current language in header (when not English)
- **Translation Icon**: Appears on translated messages
- **Pulsing Dot**: Indicates auto-translation is active
- **Translating Status**: Shows when translation is in progress

## 📡 API Usage

### Translation Endpoint

**POST** `/translate`

#### Request Body
```json
{
  "text": "मेरी फसल में कीड़े लग गए हैं",
  "source_lang": "hi",
  "target_lang": "en"
}
```

#### Response
```json
{
  "success": true,
  "data": {
    "translated_text": "My crop has been infested with insects",
    "original_text": "मेरी फसल में कीड़े लग गए हैं",
    "source_lang": "hi",
    "target_lang": "en",
    "detected_language": "hi",
    "execution_time": 0.45
  },
  "timestamp": "2025-12-08T09:30:00Z"
}
```

#### Example with cURL
```bash
curl -X POST http://localhost:5000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "How to improve crop yield?",
    "source_lang": "en",
    "target_lang": "hi"
  }'
```

### JavaScript Example
```javascript
import * as api from './services/api';

// Translate text
const result = await api.translateText(
  "मेरी गेहूं की फसल का उत्पादन कैसे बढ़ाएं?",
  "hi",  // source language
  "en"   // target language
);

console.log(result.data.translated_text);
// Output: "How to increase the yield of my wheat crop?"
```

### Python Example
```python
import requests

response = requests.post(
    "http://localhost:5000/translate",
    json={
        "text": "Best crops for monsoon season",
        "source_lang": "en",
        "target_lang": "te"
    }
)

data = response.json()
print(data["data"]["translated_text"])
# Output: "వర్షాకాలం కోసం ఉత్తమ పంటలు"
```

## 🔄 Translation Workflow

### Input Translation Flow
```
User types in Hindi
    ↓
[Auto-translate enabled?]
    ↓ Yes
Translate to English
    ↓
Send to AI Agent
    ↓
Process query
    ↓
Generate response
```

### Output Translation Flow
```
AI generates response (English)
    ↓
[Auto-translate output enabled?]
    ↓ Yes
Translate to user's language
    ↓
Display translated response
    ↓
Show translation indicator
```

## 🎯 Use Cases

### 1. **Multilingual Farmer Support**
```
User (Hindi): "मेरी टमाटर की फसल में पीले पत्ते आ रहे हैं"
↓ Translated to English
Bot processes: "My tomato crop is getting yellow leaves"
↓ Response generated
Bot (English): "Yellow leaves on tomato plants can indicate..."
↓ Translated back to Hindi
User receives: "टमाटर के पौधों पर पीले पत्ते संकेत कर सकते हैं..."
```

### 2. **Regional Language Support**
```
User (Telugu): "వర్షాకాలంలో ఏ పంటలు బాగా పండుతాయి?"
↓ Auto-translated
Bot understands: "Which crops grow well in monsoon season?"
↓ AI responds with crop recommendations
User receives response in Telugu
```

### 3. **Cross-Language Knowledge Access**
```
User asks in Kannada about pest control
↓ Query translated to English
AI accesses English knowledge base
↓ Provides comprehensive answer
Response translated to Kannada
User gets accurate information in their language
```

## 🧪 Testing

Run the translation test suite:

```bash
# Start backend and middleware first
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
node middleware/server.js

# Run translation tests
python test_translation_feature.py
```

### Test Coverage
- ✅ Basic translation API
- ✅ Multiple Indian languages
- ✅ Bidirectional translation
- ✅ Complete conversation flow
- ✅ Error handling

## ⚙️ Configuration

### Backend Setup

The translation service is already configured in `src/backend/services/translate_service.py`:

```python
from googletrans import Translator

translator = Translator()
result = translator.translate(
    text="Hello",
    src="en",
    dest="hi"
)
```

### Middleware Setup

Translation route is configured in `middleware/routes/translateRouter.js`:

```javascript
router.post('/translate', 
  validateInput.translation, 
  translateController.translate
);
```

## 🐛 Troubleshooting

### Common Issues

1. **Translation fails**
   - Check if `googletrans==4.0.0rc1` is installed
   - Verify internet connection (Google Translate API requires connectivity)
   - Check backend logs for errors

2. **Language not working**
   - Ensure language code is correct (use ISO 639-1 codes)
   - Check if language is supported by Google Translate
   - Verify middleware is running

3. **Slow translation**
   - Google Translate API may have rate limits
   - Consider caching frequent translations
   - Check network latency

### Debug Mode

Enable translation logging:
```javascript
// In AgriChatbot.jsx
console.log('🌐 Translated input:', processedText);
console.log('🌐 Translated output:', translatedOutput);
```

## 📊 Performance

- **Average Translation Time**: 0.3-0.8 seconds
- **Supported Characters**: Up to 5000 per request
- **Accuracy**: High for major Indian languages
- **Cache**: Not implemented (future enhancement)

## 🔮 Future Enhancements

1. **Translation Cache**
   - Cache common translations
   - Reduce API calls
   - Improve response time

2. **Offline Support**
   - Download language models
   - Local translation for common phrases
   - Fallback mechanism

3. **Voice Input**
   - Speech-to-text in native language
   - Auto-translate spoken queries
   - Voice output in user's language

4. **Custom Vocabulary**
   - Agricultural terms database
   - Context-aware translations
   - Domain-specific improvements

## 📚 Resources

- [Google Translate API Documentation](https://cloud.google.com/translate/docs)
- [googletrans Python Library](https://pypi.org/project/googletrans/)
- [Language Codes (ISO 639-1)](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)

## 🤝 Contributing

To add new languages:

1. Add language to `selectedLanguage` dropdown in `AgriChatbot.jsx`
2. Use ISO 639-1 language code
3. Test translation accuracy
4. Update documentation

---

**Created**: December 8, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
