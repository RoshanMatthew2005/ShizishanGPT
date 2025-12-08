/**
 * Translation Controller
 * Handles text translation requests
 */

const { apiService, formatError } = require('../services/apiClient');
const { formatTranslationResponse } = require('../services/formatter');
const logger = require('../config/logger');

/**
 * Translate text to target language
 * @route POST /translate
 */
async function translate(req, res, next) {
  try {
    const { text, target_lang, source_lang } = req.body;
    
    logger.info('Processing translation:', { 
      textLength: text.length,
      targetLang: target_lang,
      sourceLang: source_lang 
    });

    // Call FastAPI backend
    const result = await apiService.translateText(text, target_lang, source_lang);
    
    // Format and send response
    res.json(formatTranslationResponse(result));
    
  } catch (error) {
    logger.error('Translation failed:', error);
    
    // Format error and pass to error handler
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  translate
};
