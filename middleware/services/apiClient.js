/**
 * API Client Service
 * Handles all HTTP communication with FastAPI backend
 * Includes retry logic, timeout handling, and error formatting
 */

const axios = require('axios');
const FormData = require('form-data');
const config = require('../config/env');
const logger = require('../config/logger');

/**
 * Create axios instance with default configuration
 */
const apiClient = axios.create({
  baseURL: config.FASTAPI_URL,
  timeout: config.API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});

/**
 * Request interceptor - logs outgoing requests
 */
apiClient.interceptors.request.use(
  (config) => {
    logger.info(`→ API Request: ${config.method.toUpperCase()} ${config.url}`, {
      data: config.data
    });
    return config;
  },
  (error) => {
    logger.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

/**
 * Response interceptor - logs responses and handles errors
 */
apiClient.interceptors.response.use(
  (response) => {
    logger.info(`← API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      logger.error(`← API Error Response: ${error.response.status} ${error.config.url}`, {
        data: error.response.data
      });
    } else if (error.request) {
      // Request made but no response received
      logger.error('← API No Response:', {
        url: error.config?.url,
        message: error.message
      });
    } else {
      // Error in request setup
      logger.error('← API Request Setup Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Retry wrapper for API calls
 * @param {Function} apiCall - The API call function
 * @param {number} retries - Number of retry attempts
 * @returns {Promise} - API response
 */
async function withRetry(apiCall, retries = config.API_RETRY_COUNT) {
  for (let i = 0; i < retries; i++) {
    try {
      return await apiCall();
    } catch (error) {
      // Don't retry on 4xx errors (client errors)
      if (error.response && error.response.status >= 400 && error.response.status < 500) {
        throw error;
      }
      
      // Last attempt - throw error
      if (i === retries - 1) {
        throw error;
      }
      
      // Wait before retry (exponential backoff)
      const delay = Math.min(1000 * Math.pow(2, i), 5000);
      logger.warn(`Retrying API call (attempt ${i + 2}/${retries}) after ${delay}ms`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
}

/**
 * Format error for client response
 * @param {Error} error - Axios error object
 * @returns {Object} - Formatted error object
 */
function formatError(error) {
  if (error.response) {
    // Server responded with error
    return {
      success: false,
      error: error.response.data?.error || error.response.data?.message || 'Backend error',
      status: error.response.status,
      details: error.response.data?.details || null
    };
  } else if (error.request) {
    // No response received
    return {
      success: false,
      error: 'Backend service unavailable',
      status: 503,
      details: 'Could not connect to FastAPI backend'
    };
  } else {
    // Request setup error
    return {
      success: false,
      error: error.message || 'Request failed',
      status: 500,
      details: null
    };
  }
}

/**
 * API Service Methods
 */
const apiService = {
  /**
   * Send query to LLM/RAG system (now using Gemma 2 via Agent)
   */
  async queryLLM(query, mode = 'auto') {
    return withRetry(async () => {
      const response = await apiClient.post('/api/agent', { query, mode });
      return response.data;
    });
  },

  /**
   * Retrieve documents using RAG
   */
  async retrieveRAG(query, top_k = 3) {
    return withRetry(async () => {
      const response = await apiClient.post('/api/rag', { query, top_k });
      return response.data;
    });
  },

  /**
   * Predict crop yield
   */
  async predictYield(params) {
    return withRetry(async () => {
      const response = await apiClient.post('/api/predict_yield', params);
      return response.data;
    });
  },

  /**
   * Analyze weather impact
   */
  async analyzeWeather(params) {
    return withRetry(async () => {
      const response = await apiClient.post('/api/analyze_weather', params);
      return response.data;
    });
  },

  /**
   * Detect pest/disease from image
   */
  async detectPest(file, topK = 3) {
    return withRetry(async () => {
      // Create FormData for file upload
      const formData = new FormData();
      
      // Append file buffer with proper options
      formData.append('file', file.buffer, {
        filename: file.originalname,
        contentType: file.mimetype,
        knownLength: file.size
      });
      
      // Append top_k parameter
      formData.append('top_k', topK.toString());
      
      logger.info('Sending pest detection to backend:', {
        filename: file.originalname,
        size: file.size,
        mimetype: file.mimetype,
        topK: topK
      });
      
      // Send multipart request with proper headers and extended timeout
      const response = await apiClient.post('/api/detect_pest', formData, {
        headers: {
          ...formData.getHeaders()
          // Let axios calculate Content-Length automatically
        },
        timeout: 30000, // 30 seconds for image processing
        maxContentLength: Infinity,
        maxBodyLength: Infinity
      });
      
      logger.info('Pest detection response received:', {
        success: response.data?.success,
        predictions: response.data?.predictions?.length
      });
      
      return response.data;
    });
  },

  /**
   * Translate text
   */
  async translateText(text, targetLang, sourceLang = 'auto') {
    return withRetry(async () => {
      const response = await apiClient.post('/api/translate', {
        text,
        target_lang: targetLang,
        source_lang: sourceLang
      });
      return response.data;
    });
  },

  /**
   * Tavily web search
   */
  async tavilySearch(params) {
    return withRetry(async () => {
      const response = await apiClient.post('/api/tavily_search', params);
      return response.data;
    });
  },

  /**
   * Agricultural-optimized Tavily search
   */
  async tavilySearchAgricultural(params) {
    return withRetry(async () => {
      const response = await apiClient.post('/api/tavily_search/agricultural', params);
      return response.data;
    });
  }
};

module.exports = {
  apiClient,
  apiService,
  formatError
};
