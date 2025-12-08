/**
 * Request Logger Middleware
 * Logs all incoming HTTP requests with timing information
 */

const logger = require('../config/logger');

/**
 * Express middleware to log incoming requests
 */
function requestLogger(req, res, next) {
  // Start time for request duration calculation
  const startTime = Date.now();
  
  // Log request details
  logger.info(`→ Incoming Request: ${req.method} ${req.path}`, {
    method: req.method,
    path: req.path,
    query: req.query,
    ip: req.ip || req.connection.remoteAddress,
    userAgent: req.get('user-agent'),
    bodySize: JSON.stringify(req.body).length
  });

  // Capture original end function
  const originalEnd = res.end;

  // Override res.end to log response
  res.end = function(...args) {
    const duration = Date.now() - startTime;
    
    logger.info(`← Response Sent: ${req.method} ${req.path}`, {
      statusCode: res.statusCode,
      duration: `${duration}ms`,
      contentLength: res.get('content-length') || 0
    });

    // Call original end function
    originalEnd.apply(res, args);
  };

  next();
}

module.exports = requestLogger;
