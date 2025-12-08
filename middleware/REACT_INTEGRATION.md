# React Integration Guide

## How React Frontend Connects to Node.js Middleware

This guide shows you how to integrate the React frontend with the Node.js middleware layer.

---

## Architecture

```
React App (Port 3000)
    ↓ HTTP Requests
Node.js Middleware (Port 5000)
    ↓ HTTP Requests
FastAPI Backend (Port 8000)
    ↓ Responses
Node.js Middleware
    ↓ Responses
React App
```

---

## Setup API Client in React

### 1. Install Axios in React Project

```bash
cd frontend
npm install axios
```

### 2. Create API Service File

**File:** `src/services/api.js`

```javascript
import axios from 'axios';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:5000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor - Add auth token if needed
api.interceptors.request.use(
  (config) => {
    // Add authentication token here if needed
    // const token = localStorage.getItem('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      // No response received
      console.error('Network Error:', error.message);
    } else {
      // Request setup error
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// ==========================================
// API FUNCTIONS
// ==========================================

/**
 * Query LLM/RAG System
 * @param {string} query - User question
 * @param {string} mode - Query mode (auto, react, direct, pipeline)
 * @returns {Promise} Response data
 */
export async function queryLLM(query, mode = 'auto') {
  const response = await api.post('/ask', { query, mode });
  return response.data;
}

/**
 * Retrieve documents using RAG
 * @param {string} query - Search query
 * @param {number} topK - Number of documents to retrieve
 * @returns {Promise} Documents
 */
export async function retrieveDocuments(query, topK = 3) {
  const response = await api.post('/rag', { 
    query, 
    top_k: topK 
  });
  return response.data;
}

/**
 * Predict crop yield
 * @param {Object} params - Yield prediction parameters
 * @returns {Promise} Yield prediction
 */
export async function predictYield(params) {
  const response = await api.post('/predict_yield', params);
  return response.data;
}

/**
 * Analyze weather impact
 * @param {string} query - Weather query
 * @param {Object} conditions - Weather conditions
 * @returns {Promise} Weather analysis
 */
export async function analyzeWeather(query, conditions = {}) {
  const response = await api.post('/analyze_weather', {
    query,
    ...conditions
  });
  return response.data;
}

/**
 * Detect pest/disease from image
 * @param {string} imagePath - Path to image
 * @param {number} topK - Number of predictions
 * @returns {Promise} Pest detection results
 */
export async function detectPest(imagePath, topK = 3) {
  const response = await api.post('/detect_pest', {
    image_path: imagePath,
    top_k: topK
  });
  return response.data;
}

/**
 * Translate text
 * @param {string} text - Text to translate
 * @param {string} targetLang - Target language code
 * @param {string} sourceLang - Source language code
 * @returns {Promise} Translated text
 */
export async function translateText(text, targetLang, sourceLang = 'auto') {
  const response = await api.post('/translate', {
    text,
    target_lang: targetLang,
    source_lang: sourceLang
  });
  return response.data;
}

/**
 * Check API health
 * @returns {Promise} Health status
 */
export async function checkHealth() {
  const response = await api.get('/health');
  return response.data;
}

export default api;
```

---

## React Component Examples

### Example 1: Chat Interface

**File:** `src/components/ChatInterface.jsx`

```javascript
import React, { useState } from 'react';
import { queryLLM } from '../services/api';

function ChatInterface() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const result = await queryLLM(query, 'auto');
      
      if (result.success) {
        setResponse(result.data);
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get response');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <h2>Ask ShizishanGPT</h2>
      
      <form onSubmit={handleSubmit}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask a farming question..."
          rows={4}
          disabled={loading}
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </form>
      
      {error && (
        <div className="error">
          <p>Error: {error}</p>
        </div>
      )}
      
      {response && (
        <div className="response">
          <h3>Answer:</h3>
          <p>{response.answer}</p>
          
          {response.tools_used && (
            <div className="metadata">
              <small>Tools used: {response.tools_used.join(', ')}</small>
              <small>Time: {response.execution_time}s</small>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default ChatInterface;
```

### Example 2: Yield Prediction Form

**File:** `src/components/YieldPredictor.jsx`

```javascript
import React, { useState } from 'react';
import { predictYield } from '../services/api';

function YieldPredictor() {
  const [formData, setFormData] = useState({
    crop_encoded: 5,
    season_encoded: 2,
    state_encoded: 10,
    annual_rainfall: 1200,
    fertilizer: 150,
    pesticide: 50,
    area: 100
  });
  
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: parseFloat(e.target.value)
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await predictYield(formData);
      if (result.success) {
        setPrediction(result.data);
      }
    } catch (error) {
      console.error('Prediction failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="yield-predictor">
      <h2>Crop Yield Prediction</h2>
      
      <form onSubmit={handleSubmit}>
        <input
          type="number"
          name="crop_encoded"
          value={formData.crop_encoded}
          onChange={handleChange}
          placeholder="Crop Code"
        />
        
        <input
          type="number"
          name="annual_rainfall"
          value={formData.annual_rainfall}
          onChange={handleChange}
          placeholder="Rainfall (mm)"
        />
        
        <input
          type="number"
          name="fertilizer"
          value={formData.fertilizer}
          onChange={handleChange}
          placeholder="Fertilizer (kg)"
        />
        
        <input
          type="number"
          name="area"
          value={formData.area}
          onChange={handleChange}
          placeholder="Area (hectares)"
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Predict Yield'}
        </button>
      </form>
      
      {prediction && (
        <div className="prediction-result">
          <h3>Predicted Yield:</h3>
          <p className="yield-value">
            {prediction.predicted_yield.toFixed(2)} {prediction.unit}
          </p>
        </div>
      )}
    </div>
  );
}

export default YieldPredictor;
```

### Example 3: Document Search

**File:** `src/components/DocumentSearch.jsx`

```javascript
import React, { useState } from 'react';
import { retrieveDocuments } from '../services/api';

function DocumentSearch() {
  const [query, setQuery] = useState('');
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const result = await retrieveDocuments(query, 5);
      
      if (result.success) {
        setDocuments(result.data.documents);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="document-search">
      <h2>Search Knowledge Base</h2>
      
      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search documents..."
        />
        <button type="submit" disabled={loading}>Search</button>
      </form>
      
      {documents.length > 0 && (
        <div className="results">
          <h3>Results:</h3>
          {documents.map((doc, index) => (
            <div key={index} className="document">
              <p>{doc.text}</p>
              <small>Relevance: {(doc.relevance * 100).toFixed(1)}%</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default DocumentSearch;
```

---

## Environment Configuration

### React .env File

**File:** `.env` (in React project root)

```env
# API Configuration
REACT_APP_API_URL=http://localhost:5000

# Optional: Enable debug mode
REACT_APP_DEBUG=true
```

### Production .env

```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_DEBUG=false
```

---

## Using React Hooks

### Custom Hook for API Calls

**File:** `src/hooks/useAPI.js`

```javascript
import { useState, useCallback } from 'react';

export function useAPI(apiFunction) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunction(...args);
      setData(result.data);
      return result;
    } catch (err) {
      setError(err.response?.data?.error || err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunction]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return { data, loading, error, execute, reset };
}
```

### Usage Example

```javascript
import { useAPI } from '../hooks/useAPI';
import { queryLLM } from '../services/api';

function MyComponent() {
  const { data, loading, error, execute } = useAPI(queryLLM);

  const handleQuery = async () => {
    await execute('How to grow tomatoes?', 'auto');
  };

  return (
    <div>
      <button onClick={handleQuery} disabled={loading}>
        Ask Question
      </button>
      
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      {data && <p>Answer: {data.answer}</p>}
    </div>
  );
}
```

---

## Error Handling

### Global Error Handler

**File:** `src/utils/errorHandler.js`

```javascript
export function handleAPIError(error) {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 404:
        return 'Resource not found.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Please try again later.';
      case 503:
        return 'Service unavailable. Backend is not responding.';
      default:
        return data.error || 'An error occurred';
    }
  } else if (error.request) {
    // No response received
    return 'Cannot connect to server. Please check your internet connection.';
  } else {
    // Request setup error
    return error.message || 'An unexpected error occurred';
  }
}
```

---

## Complete Example App

**File:** `src/App.jsx`

```javascript
import React, { useState, useEffect } from 'react';
import { checkHealth } from './services/api';
import ChatInterface from './components/ChatInterface';
import YieldPredictor from './components/YieldPredictor';
import DocumentSearch from './components/DocumentSearch';

function App() {
  const [apiStatus, setApiStatus] = useState(null);

  useEffect(() => {
    // Check API health on mount
    checkHealth()
      .then(data => setApiStatus('online'))
      .catch(() => setApiStatus('offline'));
  }, []);

  return (
    <div className="App">
      <header>
        <h1>ShizishanGPT</h1>
        <div className="status">
          API Status: {apiStatus === 'online' ? '🟢 Online' : '🔴 Offline'}
        </div>
      </header>

      <main>
        <ChatInterface />
        <YieldPredictor />
        <DocumentSearch />
      </main>
    </div>
  );
}

export default App;
```

---

## Testing

### Test API Connection

**File:** `src/tests/api.test.js`

```javascript
import { checkHealth, queryLLM } from '../services/api';

describe('API Integration Tests', () => {
  test('Health check should succeed', async () => {
    const result = await checkHealth();
    expect(result.success).toBe(true);
  });

  test('LLM query should return answer', async () => {
    const result = await queryLLM('Test question', 'auto');
    expect(result.success).toBe(true);
    expect(result.data).toHaveProperty('answer');
  });
});
```

---

## CORS Configuration

The Node.js middleware is already configured to accept requests from `http://localhost:3000`.

If your React app runs on a different port, update the middleware `.env` file:

```env
CORS_ORIGIN=http://localhost:3001
```

For multiple origins:

**File:** `middleware/server.js` (modify CORS config)

```javascript
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:3001'],
  credentials: true
}));
```

---

## Deployment

### Production Build

1. **Build React app:**
   ```bash
   npm run build
   ```

2. **Update API URL:**
   ```env
   REACT_APP_API_URL=https://api.yourdomain.com
   ```

3. **Deploy static files** to hosting (Netlify, Vercel, S3, etc.)

4. **Update middleware CORS:**
   ```env
   CORS_ORIGIN=https://yourdomain.com
   ```

---

## Summary

✅ Created API service with all 6 endpoints  
✅ React component examples  
✅ Custom hooks for API calls  
✅ Error handling utilities  
✅ Environment configuration  
✅ Testing examples  
✅ Production deployment guide  

Your React app is now ready to communicate with the Node.js middleware!

---

**Next Steps:**
1. Copy `api.js` to your React project
2. Create components using the examples above
3. Test the integration
4. Build and deploy!
