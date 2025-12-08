/**
 * Conversation Controller
 * Handles conversation history operations
 */

const { apiService, formatError } = require('../services/apiClient');
const logger = require('../config/logger');

/**
 * Save conversation
 */
async function save(req, res, next) {
  try {
    const { session_id, title, messages, user_id } = req.body;
    
    logger.info('Saving conversation:', { session_id, title, user_id });

    // For now, return success (backend conversations not implemented)
    res.json({
      success: true,
      message: 'Conversation saved successfully',
      data: { session_id, title }
    });
    
  } catch (error) {
    logger.error('Save conversation failed:', error);
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

/**
 * List conversations
 */
async function list(req, res, next) {
  try {
    const { user_id, limit } = req.body;
    
    logger.info('Loading conversation list:', { user_id, limit });

    // For now, return empty array (backend conversations not implemented)
    res.json({
      success: true,
      message: 'Conversations retrieved successfully',
      data: { conversations: [] }
    });
    
  } catch (error) {
    logger.error('List conversations failed:', error);
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

/**
 * Get specific conversation
 */
async function get(req, res, next) {
  try {
    const { session_id, user_id } = req.body;
    
    logger.info('Getting conversation:', { session_id, user_id });

    // For now, return empty conversation (backend conversations not implemented)
    res.json({
      success: true,
      message: 'Conversation retrieved successfully',
      data: { conversation: null }
    });
    
  } catch (error) {
    logger.error('Get conversation failed:', error);
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

/**
 * Delete conversation
 */
async function deleteConversation(req, res, next) {
  try {
    const { session_id, user_id } = req.body;
    
    logger.info('Deleting conversation:', { session_id, user_id });

    // For now, return success (backend conversations not implemented)
    res.json({
      success: true,
      message: 'Conversation deleted successfully',
      data: { session_id }
    });
    
  } catch (error) {
    logger.error('Delete conversation failed:', error);
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  save,
  list,
  get,
  delete: deleteConversation
};