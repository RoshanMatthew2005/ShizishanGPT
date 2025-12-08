/**
 * Authentication Routes
 * Proxies authentication requests to FastAPI backend
 */

const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');

// Public routes (no authentication required)
router.post('/register', authController.register);
router.post('/login', authController.login);

// Protected routes (require authentication token)
router.get('/me', authController.getCurrentUser);
router.put('/me', authController.updateCurrentUser);

// Admin routes (require admin or superadmin role)
router.get('/users', authController.getAllUsers);
router.get('/users/:userId', authController.getUserById);
router.post('/users/:userId/manage', authController.manageUser);
router.delete('/users/:userId', authController.deleteUser);

module.exports = router;
