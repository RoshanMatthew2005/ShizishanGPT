/**
 * RAG Router
 * Routes for RAG document retrieval
 */

const express = require('express');
const router = express.Router();
const ragController = require('../controllers/ragController');
const validateInput = require('../middleware/validateInput');

/**
 * @route   POST /rag
 * @desc    Retrieve documents using RAG
 * @access  Public
 * @body    { query: string, top_k: number }
 */
router.post('/rag', validateInput.rag, ragController.retrieve);

module.exports = router;
