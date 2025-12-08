/**
 * Conversation History Router
 * Handles conversation storage and retrieval
 */

const express = require('express');
const axios = require('axios');
const config = require('../config/env');
const logger = require('../config/logger');
const Joi = require('joi');

const router = express.Router();

// ==========================================
// VALIDATION SCHEMAS
// ==========================================

const saveConversationSchema = Joi.object({
  session_id: Joi.string().required(),
  title: Joi.string().required().max(200),
  messages: Joi.array().items(Joi.object()).required(),
  user_id: Joi.string().default('anonymous')
});

const listConversationsSchema = Joi.object({
  user_id: Joi.string().default('anonymous'),
  limit: Joi.number().integer().min(1).max(100).default(20)
});

const getConversationSchema = Joi.object({
  session_id: Joi.string().required(),
  user_id: Joi.string().default('anonymous')
});

const deleteConversationSchema = Joi.object({
  session_id: Joi.string().required(),
  user_id: Joi.string().default('anonymous')
});

// ==========================================
// ROUTES
// ==========================================

/**
 * POST /api/conversations/save
 * Save or update a conversation
 */
router.post('/api/conversations/save', async (req, res, next) => {
  try {
    logger.info('📝 Saving conversation...');
    
    const startTime = Date.now();
    
    // Forward to FastAPI backend
    const response = await axios.post(
      `${config.FASTAPI_URL}/conversations/save`,
      req.body,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: config.REQUEST_TIMEOUT
      }
    );
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    logger.info(`✅ Conversation saved in ${duration}s`);
    
    res.json(response.data);
    
  } catch (error) {
    logger.error('❌ Save conversation error:', error.message);
    next(error);
  }
});

/**
 * POST /api/conversations/list
 * Get user's conversation list
 */
router.post('/api/conversations/list', async (req, res, next) => {
  try {
    logger.info('📋 Fetching conversation list...');
    
    const startTime = Date.now();
    
    // Forward to FastAPI backend
    const response = await axios.post(
      `${config.FASTAPI_URL}/conversations/list`,
      req.body,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: config.REQUEST_TIMEOUT
      }
    );
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    const count = response.data?.data?.count || 0;
    logger.info(`✅ Retrieved ${count} conversations in ${duration}s`);
    
    res.json(response.data);
    
  } catch (error) {
    logger.error('❌ List conversations error:', error.message);
    next(error);
  }
});

/**
 * POST /api/conversations/get
 * Get a specific conversation
 */
router.post('/api/conversations/get', async (req, res, next) => {
  try {
    logger.info(`📖 Fetching conversation: ${req.body.session_id}`);
    
    const startTime = Date.now();
    
    // Forward to FastAPI backend
    const response = await axios.post(
      `${config.FASTAPI_URL}/conversations/get`,
      req.body,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: config.REQUEST_TIMEOUT
      }
    );
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    logger.info(`✅ Conversation retrieved in ${duration}s`);
    
    res.json(response.data);
    
  } catch (error) {
    logger.error('❌ Get conversation error:', error.message);
    next(error);
  }
});

/**
 * POST /api/conversations/delete
 * Delete a conversation
 */
router.post('/api/conversations/delete', async (req, res, next) => {
  try {
    logger.info(`🗑️ Deleting conversation: ${req.body.session_id}`);
    
    const startTime = Date.now();
    
    // Forward to FastAPI backend
    const response = await axios.post(
      `${config.FASTAPI_URL}/conversations/delete`,
      req.body,
      {
        headers: { 'Content-Type': 'application/json' },
        timeout: config.REQUEST_TIMEOUT
      }
    );
    
    const duration = ((Date.now() - startTime) / 1000).toFixed(2);
    logger.info(`✅ Conversation deleted in ${duration}s`);
    
    res.json(response.data);
    
  } catch (error) {
    logger.error('❌ Delete conversation error:', error.message);
    next(error);
  }
});

module.exports = router;
