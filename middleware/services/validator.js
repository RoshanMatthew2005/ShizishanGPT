/**
 * Input Validator Service
 * Validates request data before sending to backend
 */

const Joi = require('joi');

/**
 * Validation schemas for different endpoints
 */
const schemas = {
  // LLM/RAG query validation
  query: Joi.object({
    query: Joi.string().min(1).max(5000).required(),
    mode: Joi.string().valid('auto', 'react', 'direct', 'pipeline').default('auto')
  }),

  // RAG retrieval validation
  rag: Joi.object({
    query: Joi.string().min(1).max(5000).required(),
    top_k: Joi.number().integer().min(1).max(10).default(3)
  }),

  // Yield prediction validation
  yield: Joi.object({
    crop_encoded: Joi.number().integer().min(0).max(100).required(),
    season_encoded: Joi.number().integer().min(0).max(10).required(),
    state_encoded: Joi.number().integer().min(0).max(50).required(),
    annual_rainfall: Joi.number().min(0).max(5000).required(),
    fertilizer: Joi.number().min(0).required(),
    pesticide: Joi.number().min(0).required(),
    area: Joi.number().min(0).required()
  }),

  // Weather analysis validation
  weather: Joi.object({
    query: Joi.string().min(1).max(1000).required(),
    temperature: Joi.number().min(-50).max(60).optional(),
    rainfall: Joi.number().min(0).max(5000).optional(),
    humidity: Joi.number().min(0).max(100).optional()
  }),

  // Pest detection validation
  pest: Joi.object({
    image_path: Joi.string().min(1).max(500).required(),
    top_k: Joi.number().integer().min(1).max(5).default(3)
  }),

  // Translation validation
  translation: Joi.object({
    text: Joi.string().min(1).max(10000).required(),
    target_lang: Joi.string().length(2).required(),
    source_lang: Joi.string().length(2).default('auto')
  })
};

/**
 * Generic validation function
 * @param {Object} data - Data to validate
 * @param {Joi.Schema} schema - Joi validation schema
 * @returns {Object} - { valid: boolean, data: Object, error: String }
 */
function validate(data, schema) {
  const { error, value } = schema.validate(data, {
    abortEarly: false,
    stripUnknown: true
  });

  if (error) {
    const errorMessages = error.details.map(detail => detail.message).join(', ');
    return {
      valid: false,
      error: errorMessages,
      data: null
    };
  }

  return {
    valid: true,
    data: value,
    error: null
  };
}

/**
 * Validation functions for each endpoint
 */
const validator = {
  /**
   * Validate LLM query
   */
  validateQuery(data) {
    return validate(data, schemas.query);
  },

  /**
   * Validate RAG retrieval
   */
  validateRAG(data) {
    return validate(data, schemas.rag);
  },

  /**
   * Validate yield prediction
   */
  validateYield(data) {
    return validate(data, schemas.yield);
  },

  /**
   * Validate weather analysis
   */
  validateWeather(data) {
    return validate(data, schemas.weather);
  },

  /**
   * Validate pest detection
   */
  validatePest(data) {
    return validate(data, schemas.pest);
  },

  /**
   * Validate translation
   */
  validateTranslation(data) {
    return validate(data, schemas.translation);
  }
};

module.exports = validator;
