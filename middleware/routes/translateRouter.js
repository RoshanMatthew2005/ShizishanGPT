/**
 * Translation Router
 * Routes for text translation
 */

const express = require('express');
const router = express.Router();
const translateController = require('../controllers/translateController');
const validateInput = require('../middleware/validateInput');

/**
 * @route   POST /translate
 * @desc    Translate text to target language
 * @access  Public
 * @body    { text: string, target_lang: string, source_lang?: string }
 */
router.post('/translate', validateInput.translation, translateController.translate);

module.exports = router;
