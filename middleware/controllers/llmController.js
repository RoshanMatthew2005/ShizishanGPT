/**
 * LLM Controller
 * Handles LLM/RAG query requests
 */

const { apiService, formatError } = require('../services/apiClient');
const { formatQueryResponse } = require('../services/formatter');
const logger = require('../config/logger');

/**
 * Process LLM/RAG query
 * @route POST /ask
 */
async function ask(req, res, next) {
  try {
    const { query, mode } = req.body;
    
    logger.info('Processing LLM query:', { query, mode });

    // Call FastAPI backend
    const result = await apiService.queryLLM(query, mode);
    
    // Format and send response
    res.json(formatQueryResponse(result));
    
  } catch (error) {
    logger.error('LLM query failed:', error);
    
    // Format error and pass to error handler
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  ask
};
