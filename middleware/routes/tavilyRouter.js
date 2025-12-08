/**
 * Tavily Search Router
 * Routes for real-time web search
 */

const express = require('express');
const router = express.Router();
const tavilyController = require('../controllers/tavilyController');

// Tavily search endpoints
router.post('/api/tavily_search', tavilyController.search);
router.post('/api/tavily_search/agricultural', tavilyController.searchAgricultural);

module.exports = router;
