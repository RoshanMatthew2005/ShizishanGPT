/**
 * Weather Router
 * Routes for weather analysis
 */

const express = require('express');
const router = express.Router();
const weatherController = require('../controllers/weatherController');
const validateInput = require('../middleware/validateInput');

/**
 * @route   POST /analyze_weather
 * @desc    Analyze weather impact on crops
 * @access  Public
 * @body    { query: string, temperature?: number, rainfall?: number, humidity?: number }
 */
router.post('/analyze_weather', validateInput.weather, weatherController.analyze);

module.exports = router;
