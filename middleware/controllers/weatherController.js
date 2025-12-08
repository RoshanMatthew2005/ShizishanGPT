/**
 * Weather Controller
 * Handles weather analysis requests
 */

const { apiService, formatError } = require('../services/apiClient');
const { formatWeatherResponse } = require('../services/formatter');
const logger = require('../config/logger');

/**
 * Analyze weather impact on crops
 * @route POST /analyze_weather
 */
async function analyze(req, res, next) {
  try {
    const params = req.body;
    
    logger.info('Processing weather analysis:', params);

    // Call FastAPI backend
    const result = await apiService.analyzeWeather(params);
    
    // Format and send response
    res.json(formatWeatherResponse(result));
    
  } catch (error) {
    logger.error('Weather analysis failed:', error);
    
    // Format error and pass to error handler
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  analyze
};
