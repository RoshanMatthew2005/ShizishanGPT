/**
 * Yield Controller
 * Handles crop yield prediction requests
 */

const { apiService, formatError } = require('../services/apiClient');
const { formatYieldResponse } = require('../services/formatter');
const logger = require('../config/logger');

/**
 * Predict crop yield
 * @route POST /predict_yield
 */
async function predict(req, res, next) {
  try {
    const params = req.body;
    
    logger.info('Processing yield prediction:', params);

    // Call FastAPI backend
    const result = await apiService.predictYield(params);
    
    // Format and send response
    res.json(formatYieldResponse(result));
    
  } catch (error) {
    logger.error('Yield prediction failed:', error);
    
    // Format error and pass to error handler
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  predict
};
