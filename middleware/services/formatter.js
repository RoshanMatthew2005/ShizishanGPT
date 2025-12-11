/**
 * Response Formatter Service
 * Standardizes API response format
 */

/**
 * Format successful response
 * @param {Object} data - Response data from backend
 * @param {String} message - Optional success message
 * @returns {Object} - Standardized response
 */
function formatSuccess(data, message = 'Success') {
  return {
    success: true,
    message,
    data,
    timestamp: new Date().toISOString()
  };
}

/**
 * Format error response
 * @param {String} error - Error message
 * @param {Number} status - HTTP status code
 * @param {Object} details - Additional error details
 * @returns {Object} - Standardized error response
 */
function formatError(error, status = 500, details = null) {
  return {
    success: false,
    error,
    status,
    details,
    timestamp: new Date().toISOString()
  };
}

/**
 * Format validation error
 * @param {String} errors - Validation error messages
 * @returns {Object} - Standardized validation error response
 */
function formatValidationError(errors) {
  return {
    success: false,
    error: 'Validation failed',
    status: 400,
    details: errors,
    timestamp: new Date().toISOString()
  };
}

/**
 * Format LLM/RAG query response
 * @param {Object} backendData - Data from FastAPI
 * @returns {Object} - Formatted response
 */
function formatQueryResponse(backendData) {
  // Handle both agent responses and direct LLM responses
  let answer = backendData.final_answer || backendData.answer || backendData.response || '';
  const tools = backendData.tools_used || [];
  const executionTime = backendData.execution_time || 0;
  
  // Ensure proper Markdown formatting for frontend
  answer = ensureProperMarkdownFormatting(answer);
  
  return {
    success: true,
    message: 'Query processed successfully',
    answer: answer,
    tools_used: tools,
    execution_time: executionTime,
    confidence: backendData.confidence || null,
    sources: backendData.sources || null,
    timestamp: new Date().toISOString()
  };
}

/**
 * Ensure proper Markdown formatting for frontend rendering
 * @param {String} text - Raw text from backend
 * @returns {String} - Properly formatted Markdown
 */
function ensureProperMarkdownFormatting(text) {
  if (!text) return text;
  
  // Ensure line breaks are preserved
  // React Markdown needs \n\n for paragraph breaks
  
  // Already has proper line breaks from backend, just ensure consistency
  // Remove any \r characters (Windows line endings)
  text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  
  // Ensure no trailing spaces that might break formatting
  text = text.split('\n').map(line => line.trimEnd()).join('\n');
  
  return text;
}

/**
 * Format RAG retrieval response
 * @param {Object} backendData - Data from FastAPI
 * @returns {Object} - Formatted response
 */
function formatRAGResponse(backendData) {
  return formatSuccess({
    documents: backendData.documents || [],
    num_results: backendData.num_results || 0,
    context: backendData.context || '',
    avg_relevance: backendData.avg_relevance || 0
  }, 'Documents retrieved successfully');
}

/**
 * Format yield prediction response
 * @param {Object} backendData - Data from FastAPI
 * @returns {Object} - Formatted response
 */
function formatYieldResponse(backendData) {
  return formatSuccess({
    predicted_yield: backendData.prediction || backendData.predicted_yield || 0,
    unit: backendData.unit || 'tonnes per hectare',
    confidence: backendData.confidence || null,
    inputs: backendData.inputs || {}
  }, 'Yield predicted successfully');
}

/**
 * Format weather analysis response
 * @param {Object} backendData - Data from FastAPI
 * @returns {Object} - Formatted response
 */
function formatWeatherResponse(backendData) {
  return formatSuccess({
    advice: backendData.advice || backendData.message || '',
    analysis: backendData.analysis || null,
    recommendations: backendData.recommendations || []
  }, 'Weather analysis complete');
}

/**
 * Format pest detection response
 * @param {Object} backendData - Data from FastAPI
 * @returns {Object} - Formatted response
 */
function formatPestResponse(backendData) {
  return formatSuccess({
    top_prediction: backendData.top_prediction || '',
    confidence: backendData.confidence || 0,
    all_predictions: backendData.all_predictions || [],
    recommendations: backendData.recommendations || []
  }, 'Pest detection complete');
}

/**
 * Format translation response
 * @param {Object} backendData - Data from FastAPI
 * @returns {Object} - Formatted response
 */
function formatTranslationResponse(backendData) {
  // Extract data from backend response (handles both wrapped and unwrapped formats)
  const translationData = backendData.data || backendData;
  
  return formatSuccess({
    translated_text: translationData.translated_text || '',
    source_language: translationData.source_lang || translationData.source_language || 'auto',
    target_language: translationData.target_lang || translationData.target_language || '',
    original_text: translationData.original_text || '',
    detected_language: translationData.detected_language || translationData.source_language || 'auto'
  }, 'Translation complete');
}

module.exports = {
  formatSuccess,
  formatError,
  formatValidationError,
  formatQueryResponse,
  formatRAGResponse,
  formatYieldResponse,
  formatWeatherResponse,
  formatPestResponse,
  formatTranslationResponse
};
