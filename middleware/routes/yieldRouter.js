/**
 * Yield Router
 * Routes for crop yield prediction
 */

const express = require('express');
const router = express.Router();
const yieldController = require('../controllers/yieldController');
const validateInput = require('../middleware/validateInput');

/**
 * @route   POST /predict_yield
 * @desc    Predict crop yield based on parameters
 * @access  Public
 * @body    { crop_encoded, season_encoded, state_encoded, annual_rainfall, fertilizer, pesticide, area }
 */
router.post('/predict_yield', validateInput.yield, yieldController.predict);

module.exports = router;
