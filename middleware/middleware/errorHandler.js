/**
 * Error Handler Middleware
 * Centralized error handling for all routes
 */

const logger = require('../config/logger');
const { formatError } = require('../services/formatter');

/**
 * Global error handling middleware
 * Should be registered last in middleware chain
 */
function errorHandler(err, req, res, next) {
  // Log the error
  logger.error('Error occurred:', {
    message: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method
  });

  // Determine error status code
  const statusCode = err.statusCode || err.status || 500;
  
  // Determine error message
  let errorMessage = err.message || 'Internal server error';
  
  // Don't expose internal errors in production
  if (statusCode === 500 && process.env.NODE_ENV === 'production') {
    errorMessage = 'Internal server error';
  }

  // Extract additional details if available
  const details = err.details || err.data || null;

  // Send formatted error response
  res.status(statusCode).json(formatError(errorMessage, statusCode, details));
}

/**
 * 404 Not Found handler
 */
function notFoundHandler(req, res, next) {
  logger.warn(`404 Not Found: ${req.method} ${req.path}`);
  res.status(404).json(formatError('Route not found', 404, {
    path: req.path,
    method: req.method
  }));
}

module.exports = {
  errorHandler,
  notFoundHandler
};
