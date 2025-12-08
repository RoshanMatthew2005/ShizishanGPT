/**
 * Pest Router
 * Routes for pest/disease detection
 */

const express = require('express');
const router = express.Router();
const multer = require('multer');
const pestController = require('../controllers/pestController');

// Configure multer for file uploads (in-memory storage)
const upload = multer({
  storage: multer.memoryStorage(),
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    // Accept images only
    if (!file.mimetype.startsWith('image/')) {
      cb(new Error('Only image files are allowed'), false);
    } else {
      cb(null, true);
    }
  }
});

/**
 * @route   POST /detect_pest
 * @desc    Detect pest/disease from uploaded image
 * @access  Public
 * @body    multipart/form-data with 'file' field
 */
router.post('/detect_pest', upload.single('file'), pestController.detect);

module.exports = router;
