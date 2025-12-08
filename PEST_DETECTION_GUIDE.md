# Pest Detection - User Guide

## 📸 How Pest Detection Works

The pest detection tool uses a **trained ResNet18 deep learning model** to identify 9 different plant diseases from leaf images.

### Detected Diseases:
1. Pepper Bell - Bacterial Spot
2. Pepper Bell - Healthy
3. Potato - Early Blight
4. Potato - Late Blight
5. Potato - Healthy
6. Tomato - Bacterial Spot
7. Tomato - Target Spot
8. Tomato - Tomato Mosaic Virus
9. Tomato - Yellow Leaf Curl Virus

---

## ✅ What Queries Work

### 1. **Sample Image Analysis** (For Testing)

Use these queries to test with pre-loaded sample images:

```
✅ "Analyze sample tomato disease image"
✅ "Show me sample potato late blight detection"
✅ "Test pest detection with pepper sample"
✅ "Detect disease in sample tomato bacterial spot"
✅ "Check sample potato healthy plant"
```

**How it works**: The tool automatically finds a relevant sample image from the database.

### 2. **Image Upload via Web Interface** (Production)

**Frontend Flow**:
1. User uploads image through React UI
2. Image is saved to server (e.g., `/uploads/temp_12345.jpg`)
3. Backend receives image path
4. Model processes and returns prediction

**Query example after upload**:
```
✅ "What disease is this?" (with image already uploaded)
✅ "Analyze this leaf image" (with image context)
```

### 3. **Direct File Path** (Development/Testing)

If you have access to the file system:

```
✅ tool.run(image_path="Data/images/PlantVillage/Tomato_Bacterial_spot/image001.jpg")
✅ tool.run(query="", image_path="D:/myplant.jpg")
```

---

## ❌ What Queries DON'T Work

### Without Image or Sample Keyword:

```
❌ "Detect plant disease" 
   → No image, no sample keyword → Provides guidance

❌ "What's wrong with my tomato plant?"
   → No image provided → Provides guidance

❌ "How to treat pepper disease?"
   → This is a question, not detection request → Use RAG instead
```

**What happens**: The tool responds with helpful guidance:
```
"Image required for pest detection. You can:
1. Upload an image through the web interface
2. Request a sample analysis: 'Analyze sample tomato disease image'
3. Provide an image path: 'Detect disease in Data/images/...'"
```

---

## 🎯 Query Examples & Expected Results

### Example 1: Sample Tomato Analysis
```python
Query: "Analyze sample tomato bacterial spot image"

✓ Selected sample image from: tomato_bacterial_spot
✓ Result:
  - Top Prediction: Tomato_Bacterial_spot
  - Confidence: 94.5%
  - All Predictions:
    1. Tomato_Bacterial_spot - 94.50%
    2. Tomato__Target_Spot - 4.20%
    3. Pepper__bell___Bacterial_spot - 1.30%
```

### Example 2: Sample Pepper Analysis
```python
Query: "Test pest detection with pepper sample"

✓ Selected sample image from: pepper_bacterial_spot
✓ Result:
  - Top Prediction: Pepper__bell___Bacterial_spot
  - Confidence: 99.67%
```

### Example 3: No Image Provided
```python
Query: "Detect plant disease"

❌ Result:
  - Error: No image provided
  - Guidance: [Shows 3 options above]
  - Sample Categories: [tomato_bacterial_spot, potato_late_blight, ...]
```

---

## 🔄 Integration with ReAct Agent

The ReAct agent automatically:
1. **Detects** when user wants pest detection
2. **Parses** query for sample keywords
3. **Finds** appropriate sample image
4. **Executes** detection
5. **Returns** formatted result

### ReAct Agent Example:

```python
from src.orchestration.react_agent import ReActAgent

agent = ReActAgent(verbose=True)

# This will work!
result = agent.run("Analyze sample tomato bacterial spot")

print(result['final_answer'])
# Output: "Detected: Tomato_Bacterial_spot (94% confidence)"
```

---

## 🚀 How to Use in Production

### Option 1: Web Interface (Recommended)

**Frontend (React)**:
```javascript
// User uploads image
const formData = new FormData();
formData.append('image', selectedFile);
formData.append('query', 'What disease is this?');

// Send to backend
fetch('/api/pest-detection', {
  method: 'POST',
  body: formData
})
```

**Backend (FastAPI)**:
```python
@app.post("/api/pest-detection")
async def detect_pest(file: UploadFile, query: str):
    # Save uploaded file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Run detection
    tool = PestTool()
    result = tool.run(image_path=file_path)
    
    return result
```

### Option 2: Direct API Call

```python
import requests

# Upload image
files = {'image': open('my_plant.jpg', 'rb')}
data = {'query': 'Detect disease'}

response = requests.post('http://localhost:8000/api/pest-detection', 
                        files=files, data=data)
print(response.json())
```

### Option 3: Command Line Testing

```bash
# Test with sample
python -c "from src.model_tools.pest_tool import PestTool; tool = PestTool(); print(tool.run(query='sample tomato'))"

# Test with your image
python -c "from src.model_tools.pest_tool import PestTool; tool = PestTool(); print(tool.run(image_path='path/to/image.jpg'))"
```

---

## 📊 Understanding Results

### Success Response:
```json
{
  "success": true,
  "tool": "pest_detection",
  "image": "Data/images/.../image.jpg",
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
    }
  ]
}
```

### Error Response:
```json
{
  "success": false,
  "error": "No image provided",
  "tool": "pest_detection",
  "guidance": {
    "message": "Pest detection requires an image...",
    "options": ["1. Upload...", "2. Request sample...", "3. Provide path..."],
    "sample_categories": ["tomato_bacterial_spot", ...]
  }
}
```

---

## 🎨 Sample Categories Available

You can request samples from these categories:

| Category | Description |
|----------|-------------|
| `tomato_bacterial_spot` | Tomato with bacterial spot disease |
| `tomato_yellow_leaf_curl` | Tomato with yellow leaf curl virus |
| `tomato_mosaic_virus` | Tomato with mosaic virus |
| `tomato_target_spot` | Tomato with target spot disease |
| `potato_early_blight` | Potato with early blight disease |
| `potato_late_blight` | Potato with late blight disease |
| `potato_healthy` | Healthy potato plant |
| `pepper_bacterial_spot` | Pepper with bacterial spot |
| `pepper_healthy` | Healthy pepper plant |

---

## 🔧 Troubleshooting

### Issue: "Model not found"
**Solution**: Run the model training script first:
```bash
python src/train_pest_model.py
```

### Issue: "Image file not found"
**Solution**: Check the file path is correct and file exists:
```python
from pathlib import Path
print(Path("your/image/path.jpg").exists())
```

### Issue: Low confidence predictions
**Possible reasons**:
- Image quality is poor
- Disease not in training dataset (9 classes only)
- Multiple diseases present
- Not a leaf image

**Solution**: Try with a clear, well-lit leaf image showing disease symptoms

### Issue: Wrong predictions
**Model Limitations**:
- Trained on only 9 disease classes
- Works best with tomato, potato, pepper plants
- Needs clear leaf images
- May confuse similar diseases

**Future Improvements**:
- Retrain with more disease classes
- Add data augmentation
- Use ensemble models
- Implement confidence thresholds

---

## 📈 Model Performance

- **Architecture**: ResNet18 (pretrained on ImageNet)
- **Training Dataset**: PlantVillage
- **Number of Classes**: 9
- **Input Size**: 224x224 RGB
- **Typical Accuracy**: 85-95% on test set
- **Inference Time**: ~0.5-1.0 seconds per image

---

## 💡 Best Practices

1. **Use clear, well-lit images**: Better lighting = better detection
2. **Focus on diseased areas**: Center the affected part of the leaf
3. **Single leaf images**: Works better than whole plant images
4. **Check confidence scores**: >80% = reliable, <50% = uncertain
5. **Test with samples first**: Verify system works before production use

---

## 🔗 Related Documentation

- **Model Training**: `src/train_pest_model.py`
- **Tool Implementation**: `src/model_tools/pest_tool.py`
- **API Routes**: `src/backend/routers/router_pest.py` (if exists)
- **Test Script**: `test_pest_detection.py`

---

**Status**: ✅ Fully Functional  
**Supports**: Sample images + Direct file paths + Web uploads  
**Ready for**: Development testing and production deployment
