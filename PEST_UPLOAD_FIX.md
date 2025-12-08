# Pest Detection - Image Upload Fix

## ✅ Issue Fixed

**Problem**: "Validation failed" error when uploading images for pest detection

**Root Cause**: Mismatch between frontend/middleware expectations and backend implementation:
- **Middleware expected**: JSON with `image_path` string
- **Backend expected**: Multipart form data with actual file upload
- **Frontend sent**: Image file upload

## 🔧 Changes Made

### 1. **middleware/routes/pestRouter.js**
- ✅ Added `multer` middleware for handling file uploads
- ✅ Configured in-memory storage (no disk writes)
- ✅ Added 10MB file size limit
- ✅ Added image file type validation

### 2. **middleware/controllers/pestController.js**
- ✅ Updated to handle `req.file` instead of `req.body`
- ✅ Added file validation checks
- ✅ Added proper error handling for file upload errors
- ✅ Extracts `top_k` from request body

### 3. **middleware/services/apiClient.js**
- ✅ Updated `detectPest()` to send multipart/form-data
- ✅ Creates FormData with file buffer
- ✅ Forwards file to FastAPI backend correctly

### 4. **middleware/package.json**
- ✅ Added `multer@^1.4.5-lts.1` for file uploads
- ✅ Added `form-data@^4.0.0` for multipart data

## 🚀 How to Use Now

### Frontend (React)
```javascript
// Create FormData with image file
const formData = new FormData();
formData.append('file', selectedImageFile); // File object from input
formData.append('top_k', 3); // Optional, defaults to 3

// Send to middleware
const response = await fetch('http://localhost:5000/detect_pest', {
  method: 'POST',
  body: formData
  // Don't set Content-Type header - browser will set it automatically
});

const result = await response.json();
console.log(result);
```

### Example with File Input
```html
<input type="file" id="imageInput" accept="image/*" />
<button onclick="detectPest()">Detect Disease</button>

<script>
async function detectPest() {
  const fileInput = document.getElementById('imageInput');
  const file = fileInput.files[0];
  
  if (!file) {
    alert('Please select an image');
    return;
  }
  
  const formData = new FormData();
  formData.append('file', file);
  formData.append('top_k', 3);
  
  try {
    const response = await fetch('http://localhost:5000/detect_pest', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (result.success) {
      console.log('Top Prediction:', result.data.top_prediction);
      console.log('Confidence:', result.data.confidence);
      console.log('All Predictions:', result.data.all_predictions);
    } else {
      console.error('Error:', result.error);
    }
  } catch (error) {
    console.error('Request failed:', error);
  }
}
</script>
```

## 📊 Expected Response

### Success Response:
```json
{
  "success": true,
  "data": {
    "top_prediction": "Tomato_Bacterial_spot",
    "confidence": 0.945,
    "all_predictions": [
      {
        "disease": "Tomato_Bacterial_spot",
        "confidence": 0.945,
        "percentage": "94.50%"
      },
      {
        "disease": "Tomato__Target_Spot",
        "confidence": 0.042,
        "percentage": "4.20%"
      },
      {
        "disease": "Pepper__bell___Bacterial_spot",
        "confidence": 0.013,
        "percentage": "1.30%"
      }
    ],
    "execution_time": 0.75,
    "image_info": {
      "size": [224, 224],
      "mode": "RGB"
    }
  },
  "message": "Pest detection complete"
}
```

### Error Response (No File):
```json
{
  "success": false,
  "error": "No image file uploaded",
  "message": "Please upload an image file"
}
```

### Error Response (Invalid File Type):
```json
{
  "success": false,
  "error": "Invalid file type",
  "message": "Please upload an image file (JPG, PNG, etc.)"
}
```

### Error Response (File Too Large):
```json
{
  "success": false,
  "error": "File too large",
  "message": "Image must be smaller than 10MB"
}
```

## 🧪 Testing

### 1. Restart Middleware
```bash
cd middleware
node server.js
```

### 2. Test with cURL
```bash
curl -X POST http://localhost:5000/detect_pest \
  -F "file=@path/to/your/plant_image.jpg" \
  -F "top_k=3"
```

### 3. Test with Postman
- Method: POST
- URL: `http://localhost:5000/detect_pest`
- Body: form-data
  - Key: `file` (type: File) → Select image
  - Key: `top_k` (type: Text) → Value: `3`

## 🔍 Validation Rules

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| `file` | File | ✅ Yes | Must be image (jpg, png, etc.) |
| `file` size | Number | ✅ Yes | Max 10MB |
| `top_k` | Integer | ❌ No | 1-5, default: 3 |

## 🎯 Complete Flow

1. **Frontend** → User selects image file
2. **Frontend** → Creates FormData with file
3. **Frontend** → Sends POST to `http://localhost:5000/detect_pest`
4. **Middleware** → Receives file via multer
5. **Middleware** → Validates file type and size
6. **Middleware** → Forwards file to FastAPI backend
7. **Backend** → Processes image with ResNet18 model
8. **Backend** → Returns predictions
9. **Middleware** → Formats and returns response to frontend
10. **Frontend** → Displays results to user

## ⚠️ Important Notes

1. **Don't set Content-Type header** in frontend - Browser will automatically set it with proper boundary
2. **File size limit**: 10MB (configurable in pestRouter.js)
3. **Supported formats**: JPG, JPEG, PNG, BMP, TIFF
4. **Model classes**: Only detects 9 plant diseases (Tomato, Potato, Pepper)
5. **In-memory processing**: Files are not saved to disk (using multer.memoryStorage())

## 🐛 Troubleshooting

### Issue: Still getting "Validation failed"
**Solution**: Make sure you're sending `file` field, not `image` or `image_path`

### Issue: "File too large"
**Solution**: Reduce image size before upload or increase limit in pestRouter.js:
```javascript
limits: { fileSize: 20 * 1024 * 1024 } // 20MB
```

### Issue: "Backend service unavailable"
**Solution**: Ensure FastAPI backend is running on port 8000:
```bash
python -m uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

**Status**: ✅ Fixed and Tested  
**Ready for**: Image uploads from frontend  
**Next Step**: Update frontend React component to send FormData instead of JSON
