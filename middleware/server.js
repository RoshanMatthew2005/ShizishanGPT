/**
 * ShizishanGPT Middleware Server
 * Node.js + Express API Gateway
 * Connects React Frontend → Node.js → FastAPI Backend
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const rateLimit = require('express-rate-limit');

// Import configurations
const config = require('./config/env');
const logger = require('./config/logger');

// Import middleware
const requestLogger = require('./middleware/requestLogger');
const { errorHandler, notFoundHandler } = require('./middleware/errorHandler');

// Import routers
const llmRouter = require('./routes/llmRouter');
const ragRouter = require('./routes/ragRouter');
const yieldRouter = require('./routes/yieldRouter');
const weatherRouter = require('./routes/weatherRouter');
const pestRouter = require('./routes/pestRouter');
const translateRouter = require('./routes/translateRouter');
const conversationRouter = require('./routes/conversationRouter');
const tavilyRouter = require('./routes/tavilyRouter');  // Tavily Search
const authRouter = require('./routes/authRouter');  // Authentication

// Initialize Express app
const app = express();

// ==========================================
// SECURITY MIDDLEWARE
// ==========================================

// Helmet - Security headers (relaxed for development)
app.use(helmet({
  contentSecurityPolicy: false, // Disable CSP for development
  crossOriginEmbedderPolicy: false
}));

// CORS - Cross-Origin Resource Sharing (permissive for development)
app.use(cors({
  origin: ['http://localhost:3000', 'http://127.0.0.1:3000', 'http://localhost:3001', '*'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'HEAD'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With', 'Accept', 'Origin'],
  exposedHeaders: ['Content-Length', 'X-Foo', 'X-Bar'],
  optionsSuccessStatus: 200
}));

// Handle preflight OPTIONS requests
app.options('*', cors());

// Rate limiting - Prevent abuse
const limiter = rateLimit({
  windowMs: config.RATE_LIMIT_WINDOW,
  max: config.RATE_LIMIT_MAX_REQUESTS,
  message: {
    success: false,
    error: 'Too many requests from this IP, please try again later',
    status: 429
  },
  standardHeaders: true,
  legacyHeaders: false
});
app.use(limiter);

// ==========================================
// PARSING MIDDLEWARE
// ==========================================

// Compression - Reduce response size
app.use(compression());

// Body parser - Parse JSON requests
app.use(express.json({ limit: config.REQUEST_SIZE_LIMIT }));
app.use(express.urlencoded({ extended: true, limit: config.REQUEST_SIZE_LIMIT }));

// ==========================================
// LOGGING MIDDLEWARE
// ==========================================

app.use(requestLogger);

// ==========================================
// HEALTH CHECK ROUTE
// ==========================================

app.get('/health', (req, res) => {
  res.json({
    success: true,
    message: 'ShizishanGPT Middleware is running',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    environment: config.NODE_ENV
  });
});

app.get('/', (req, res) => {
  res.json({
    success: true,
    message: 'Welcome to ShizishanGPT API Gateway',
    version: '1.0.0',
    endpoints: {
      llm: 'POST /ask',
      rag: 'POST /rag',
      yield: 'POST /predict_yield',
      weather: 'POST /analyze_weather',
      pest: 'POST /detect_pest',
      translation: 'POST /translate',
      conversations: 'POST /api/conversations/*',
      health: 'GET /health'
    },
    documentation: 'See README.md for API documentation'
  });
});

// ==========================================
// API ROUTES
// ==========================================

// Register all routers
app.use('/', llmRouter);          // POST /ask
app.use('/', ragRouter);          // POST /rag
app.use('/', yieldRouter);        // POST /predict_yield
app.use('/', weatherRouter);      // POST /analyze_weather
app.use('/', pestRouter);         // POST /detect_pest
app.use('/', translateRouter);    // POST /translate
app.use('/', conversationRouter); // Conversation history
app.use('/', tavilyRouter);       // POST /api/tavily_search
app.use('/api/auth', authRouter); // Authentication endpoints

// ==========================================
// ERROR HANDLING
// ==========================================

// 404 handler - Route not found
app.use(notFoundHandler);

// Global error handler
app.use(errorHandler);

// ==========================================
// START SERVER
// ==========================================

const PORT = config.PORT;

app.listen(PORT, () => {
  logger.info('========================================');
  logger.info('🚀 ShizishanGPT Middleware Started');
  logger.info('========================================');
  logger.info(`📡 Server running on port ${PORT}`);
  logger.info(`🌍 Environment: ${config.NODE_ENV}`);
  logger.info(`🔗 FastAPI Backend: ${config.FASTAPI_URL}`);
  logger.info(`🌐 CORS Origin: ${config.CORS_ORIGIN}`);
  logger.info(`📝 Log Level: ${config.LOG_LEVEL}`);
  logger.info('========================================');
  logger.info('Available Routes:');
  logger.info('  POST /ask              - LLM/RAG Query');
  logger.info('  POST /rag              - RAG Retrieval');
  logger.info('  POST /predict_yield    - Yield Prediction');
  logger.info('  POST /analyze_weather  - Weather Analysis');
  logger.info('  POST /detect_pest      - Pest Detection');
  logger.info('  POST /translate        - Translation');
  logger.info('  GET  /health           - Health Check');
  logger.info('========================================');
  
  console.log(`\n✅ Node.js middleware running on http://localhost:${PORT}`);
  console.log(`✅ Ready to receive requests from React frontend\n`);
});

// Graceful shutdown handler
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT signal received: closing HTTP server');
  process.exit(0);
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', error);
  process.exit(1);
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection at:', promise, 'reason:', reason);
  process.exit(1);
});

module.exports = app;
