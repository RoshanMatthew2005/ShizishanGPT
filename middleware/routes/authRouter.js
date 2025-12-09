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
router.get('/admin/users', authController.getAllUsers);
router.get('/admin/users/:userId', authController.getUserById);
router.post('/admin/users', authController.createUser);
router.put('/admin/users/:userId', authController.updateUser);
router.put('/admin/users/:userId/toggle-active', authController.toggleUserActive);
router.delete('/admin/users/:userId', authController.deleteUser);

module.exports = router;
