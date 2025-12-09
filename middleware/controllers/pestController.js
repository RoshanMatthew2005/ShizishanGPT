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
      logger.warn('No file uploaded in request');
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
      topK: topK,
      bufferSize: req.file.buffer ? req.file.buffer.length : 0
    });

    // Validate file buffer
    if (!req.file.buffer || req.file.buffer.length === 0) {
      logger.error('File buffer is empty');
      return res.status(400).json({
        success: false,
        error: 'Invalid file',
        message: 'Uploaded file is empty or corrupted'
      });
    }

    // Call FastAPI backend with file data
    const result = await apiService.detectPest(req.file, topK);
    
    logger.info('Pest detection successful:', {
      predictions: result.predictions?.length || 0
    });
    
    // Format and send response
    res.json(formatPestResponse(result));
    
  } catch (error) {
    logger.error('Pest detection failed:', {
      message: error.message,
      stack: error.stack,
      response: error.response?.data
    });
    
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

    // Handle backend errors
    if (error.response?.data) {
      return res.status(error.response.status || 500).json({
        success: false,
        error: error.response.data.detail || error.response.data.error || 'Backend error',
        message: error.response.data.message || 'Failed to process image'
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
