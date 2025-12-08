/**
 * RAG Controller
 * Handles RAG document retrieval requests
 */

const { apiService, formatError } = require('../services/apiClient');
const { formatRAGResponse } = require('../services/formatter');
const logger = require('../config/logger');

/**
 * Retrieve documents using RAG
 * @route POST /rag
 */
async function retrieve(req, res, next) {
  try {
    const { query, top_k } = req.body;
    
    logger.info('Processing RAG retrieval:', { query, top_k });

    // Call FastAPI backend
    const result = await apiService.retrieveRAG(query, top_k);
    
    // Format and send response
    res.json(formatRAGResponse(result));
    
  } catch (error) {
    logger.error('RAG retrieval failed:', error);
    
    // Format error and pass to error handler
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  retrieve
};
