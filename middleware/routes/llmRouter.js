/**
 * LLM Router
 * Routes for LLM/RAG query endpoints
 */

const express = require('express');
const router = express.Router();
const llmController = require('../controllers/llmController');
const validateInput = require('../middleware/validateInput');

/**
 * @route   POST /ask
 * @desc    Process LLM/RAG query
 * @access  Public
 * @body    { query: string, mode: string }
 */
router.post('/ask', validateInput.query, llmController.ask);

/**
 * @route   POST /agent
 * @desc    Query ReAct agent (alias for /ask)
 * @access  Public
 * @body    { query: string, mode: string, max_iterations: number }
 */
router.post('/agent', validateInput.query, llmController.ask);

module.exports = router;
