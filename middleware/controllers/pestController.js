/**
 * Pest Controller
 * Handles pest/disease detection requests
 */

const { apiService, formatError } = require('../services/apiClient');
const { formatPestResponse } = require('../services/formatter');
const logger = require('../config/logger');

/**
 * Detect pest/disease from uploaded image
 * @route POST /detect_pest
 */
async function detect(req, res, next) {
  try {
    // Check if file was uploaded
    if (!req.file) {
      return res.status(400).json({
        success: false,
        error: 'No image file uploaded',
        message: 'Please upload an image file'
      });
    }

    const topK = parseInt(req.body.top_k) || 3;
    
    logger.info('Processing pest detection:', { 
      filename: req.file.originalname,
      size: req.file.size,
      mimetype: req.file.mimetype,
      topK: topK
    });

    // Call FastAPI backend with file data
    const result = await apiService.detectPest(req.file, topK);
    
    // Format and send response
    res.json(formatPestResponse(result));
    
  } catch (error) {
    logger.error('Pest detection failed:', error);
    
    // Handle multer errors
    if (error.message === 'Only image files are allowed') {
      return res.status(400).json({
        success: false,
        error: 'Invalid file type',
        message: 'Please upload an image file (JPG, PNG, etc.)'
      });
    }
    
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(400).json({
        success: false,
        error: 'File too large',
        message: 'Image must be smaller than 10MB'
      });
    }
    
    // Format error and pass to error handler
    const formattedError = formatError(error);
    res.status(formattedError.status).json(formattedError);
  }
}

module.exports = {
  detect
};
