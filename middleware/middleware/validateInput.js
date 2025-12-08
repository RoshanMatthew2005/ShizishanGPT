/**
 * Input Validation Middleware
 * Validates request data before processing
 */

const validator = require('../services/validator');
const { formatValidationError } = require('../services/formatter');
const logger = require('../config/logger');

/**
 * Create validation middleware for specific validator function
 * @param {Function} validatorFn - Validator function from validator service
 * @returns {Function} - Express middleware
 */
function createValidationMiddleware(validatorFn) {
  return (req, res, next) => {
    const { valid, data, error } = validatorFn(req.body);
    
    if (!valid) {
      logger.warn('Validation failed:', {
        path: req.path,
        errors: error
      });
      return res.status(400).json(formatValidationError(error));
    }
    
    // Replace request body with validated and sanitized data
    req.body = data;
    next();
  };
}

/**
 * Validation middlewares for each endpoint
 */
const validateInput = {
  // Validate LLM query
  query: createValidationMiddleware(validator.validateQuery),
  
  // Validate RAG retrieval
  rag: createValidationMiddleware(validator.validateRAG),
  
  // Validate yield prediction
  yield: createValidationMiddleware(validator.validateYield),
  
  // Validate weather analysis
  weather: createValidationMiddleware(validator.validateWeather),
  
  // Validate pest detection
  pest: createValidationMiddleware(validator.validatePest),
  
  // Validate translation
  translation: createValidationMiddleware(validator.validateTranslation)
};

module.exports = validateInput;
