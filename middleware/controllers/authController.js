/**
 * Authentication Controller
 * Handles authentication logic and proxies to FastAPI backend
 */

const axios = require('axios');
const logger = require('../config/logger');

// FastAPI backend URL
const BACKEND_URL = process.env.FASTAPI_BACKEND_URL || 'http://localhost:8000';

/**
 * Register new user
 */
exports.register = async (req, res, next) => {
  try {
    logger.info('📝 Register request received');
    
    const response = await axios.post(`${BACKEND_URL}/api/auth/register`, req.body);
    
    res.status(201).json(response.data);
  } catch (error) {
    logger.error('❌ Registration error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};

/**
 * Login user
 */
exports.login = async (req, res, next) => {
  try {
    logger.info('🔐 Login request received');
    
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, req.body);
    
    res.json(response.data);
  } catch (error) {
    logger.error('❌ Login error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};

/**
 * Get current user info
 */
exports.getCurrentUser = async (req, res, next) => {
  try {
    const token = req.headers.authorization;
    
    if (!token) {
      return res.status(401).json({ detail: 'Authorization token required' });
    }
    
    logger.info('👤 Get current user request');
    
    const response = await axios.get(`${BACKEND_URL}/api/auth/me`, {
      headers: { Authorization: token }
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error('❌ Get current user error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};

/**
 * Update current user
 */
exports.updateCurrentUser = async (req, res, next) => {
  try {
    const token = req.headers.authorization;
    
    if (!token) {
      return res.status(401).json({ detail: 'Authorization token required' });
    }
    
    logger.info('✏️ Update current user request');
    
    const response = await axios.put(`${BACKEND_URL}/api/auth/me`, req.body, {
      headers: { Authorization: token }
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error('❌ Update user error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};

/**
 * Get all users (Admin only)
 */
exports.getAllUsers = async (req, res, next) => {
  try {
    const token = req.headers.authorization;
    
    if (!token) {
      return res.status(401).json({ detail: 'Authorization token required' });
    }
    
    const { skip = 0, limit = 100 } = req.query;
    
    logger.info('📋 Get all users request');
    
    const response = await axios.get(`${BACKEND_URL}/api/auth/users`, {
      params: { skip, limit },
      headers: { Authorization: token }
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error('❌ Get users error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};

/**
 * Get user by ID (Admin only)
 */
exports.getUserById = async (req, res, next) => {
  try {
    const token = req.headers.authorization;
    
    if (!token) {
      return res.status(401).json({ detail: 'Authorization token required' });
    }
    
    const { userId } = req.params;
    
    logger.info(`🔍 Get user ${userId} request`);
    
    const response = await axios.get(`${BACKEND_URL}/api/auth/users/${userId}`, {
      headers: { Authorization: token }
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error('❌ Get user error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};

/**
 * Manage user (Admin only)
 */
exports.manageUser = async (req, res, next) => {
  try {
    const token = req.headers.authorization;
    
    if (!token) {
      return res.status(401).json({ detail: 'Authorization token required' });
    }
    
    const { userId } = req.params;
    
    logger.info(`⚙️ Manage user ${userId} - Action: ${req.body.action}`);
    
    const response = await axios.post(
      `${BACKEND_URL}/api/auth/users/${userId}/manage`,
      req.body,
      { headers: { Authorization: token } }
    );
    
    res.json(response.data);
  } catch (error) {
    logger.error('❌ Manage user error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};

/**
 * Delete user (Admin only)
 */
exports.deleteUser = async (req, res, next) => {
  try {
    const token = req.headers.authorization;
    
    if (!token) {
      return res.status(401).json({ detail: 'Authorization token required' });
    }
    
    const { userId } = req.params;
    
    logger.info(`🗑️ Delete user ${userId} request`);
    
    const response = await axios.delete(`${BACKEND_URL}/api/auth/users/${userId}`, {
      headers: { Authorization: token }
    });
    
    res.json(response.data);
  } catch (error) {
    logger.error('❌ Delete user error:', error.response?.data || error.message);
    
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      next(error);
    }
  }
};
