/**
 * Tavily Search Controller
 * Handles web search requests from frontend
 */

const { apiService, formatError } = require('../services/apiClient');
const logger = require('../config/logger');

/**
 * Execute Tavily search
 * @route POST /api/tavily_search
 */
async function search(req, res, next) {
  try {
    const { query, search_depth = 'basic', max_results = 5, include_domains } = req.body;
    
    if (!query || query.length < 3) {
      return res.status(400).json({
        success: false,
        error: 'Query must be at least 3 characters'
      });
    }
    
    logger.info('🔍 Tavily search request:', { query, search_depth, max_results });
    
    // Call FastAPI backend
    const result = await apiService.tavilySearch({
      query,
      search_depth,
      max_results,
      include_domains
    });
    
    logger.info(`✓ Tavily search completed: ${result.results_count} results in ${result.response_time}s`);
    res.json(result);
    
  } catch (error) {
    logger.error('Tavily search failed:', error);
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

/**
 * Agricultural-optimized search
 * @route POST /api/tavily_search/agricultural
 */
async function searchAgricultural(req, res, next) {
  try {
    const { query, max_results = 5 } = req.body;
    
    if (!query) {
      return res.status(400).json({
        success: false,
        error: 'Query is required'
      });
    }
    
    logger.info('🌾 Agricultural search:', { query, max_results });
    
    const result = await apiService.tavilySearchAgricultural({
      query,
      max_results
    });
    
    res.json(result);
    
  } catch (error) {
    logger.error('Agricultural search failed:', error);
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  search,
  searchAgricultural
};
