/**
 * Environment Configuration Module
 * Loads and validates environment variables
 */

require('dotenv').config();

const config = {
  // Server Configuration
  PORT: process.env.PORT || 5000,
  NODE_ENV: process.env.NODE_ENV || 'development',
  
  // FastAPI Backend URL
  FASTAPI_URL: process.env.FASTAPI_URL || 'http://localhost:8000',
  
  // CORS Configuration
  CORS_ORIGIN: process.env.CORS_ORIGIN || 'http://localhost:3000',
  
  // API Configuration
  API_TIMEOUT: parseInt(process.env.API_TIMEOUT) || 30000, // 30 seconds
  API_RETRY_COUNT: parseInt(process.env.API_RETRY_COUNT) || 3,
  
  // Request Limits
  REQUEST_SIZE_LIMIT: process.env.REQUEST_SIZE_LIMIT || '10mb',
  RATE_LIMIT_WINDOW: parseInt(process.env.RATE_LIMIT_WINDOW) || 15 * 60 * 1000, // 15 minutes
  RATE_LIMIT_MAX_REQUESTS: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100,
  
  // Logging
  LOG_LEVEL: process.env.LOG_LEVEL || 'info',
  LOG_FILE: process.env.LOG_FILE || 'logs/middleware.log',
};

/**
 * Validate required environment variables
 */
function validateConfig() {
  const required = ['FASTAPI_URL'];
  const missing = required.filter(key => !config[key]);
  
  if (missing.length > 0) {
    console.warn(`⚠️  Warning: Missing environment variables: ${missing.join(', ')}`);
    console.warn('⚠️  Using default values. Check .env file.');
  }
}

validateConfig();

module.exports = config;
