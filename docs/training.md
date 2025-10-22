# ShizishanGPT - Model Training Guide

## Phase 1: Core ML Models

### 1. Yield Prediction Model

#### Data Requirements
- CSV file with columns: nitrogen, phosphorus, potassium, rainfall, temperature, ph, yield
- Minimum 1000 samples recommended

#### Training Steps

```python
from src.tools.yield_predictor import YieldPredictor
from src.preprocessing.data_loader import DataLoader

# Load data
loader = DataLoader()
data = loader.load_csv('crop_yield_data.csv')

# Initialize and train
predictor = YieldPredictor()
metrics = predictor.train(data)

# Save model
predictor.save_model()

# Test prediction
sample = {
    'nitrogen': 90,
    'phosphorus': 42,
    'potassium': 43,
    'rainfall': 202.9,
    'temperature': 26.8,
    'ph': 6.5
}
yield_pred = predictor.predict(sample)
print(f"Predicted Yield: {yield_pred:.2f} tons/ha")
```

#### Expected Performance
- RMSE: < 0.5 tons/ha
- R² Score: > 0.85
- MAE: < 0.3 tons/ha

---

### 2. Pest Detection Model

#### Data Requirements
- Images of crop diseases organized by class
- Folder structure:
  ```
  data/raw/images/
  ├── healthy/
  ├── leaf_blight/
  ├── leaf_rust/
  └── ...
  ```

#### Training Steps

```python
from src.tools.pest_detector import PestDetector
from torch.utils.data import DataLoader
import torchvision.transforms as transforms

# Initialize detector
detector = PestDetector()

# Build model
num_classes = 10
detector.build_model(num_classes)

# Prepare data loaders (implement dataset class)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)

# Train
class_names = ['healthy', 'leaf_blight', 'leaf_rust', ...]
detector.train(train_loader, val_loader, class_names)

# Save
detector.save_model()
```

#### Expected Performance
- Accuracy: > 90%
- Precision: > 88%
- Recall: > 87%

---

### 3. Weather Impact Model

#### Data Requirements
- Time series weather data (temperature, rainfall, humidity)
- Corresponding yield data

#### Training Steps

```python
from src.tools.weather_model import WeatherModel
import numpy as np

# Prepare time series data
weather_data = np.array(...)  # shape: (samples, features)

# Initialize model
weather_model = WeatherModel()
weather_model.build_model(input_size=3)

# Train
weather_model.train(weather_data)

# Save
weather_model.save_model()
```

---

### 4. RAG Retriever

#### Data Requirements
- Agricultural PDFs, text documents
- Place in `data/raw/pdfs/`

#### Setup Steps

```python
from src.rag.rag_retriever import RAGRetriever
import PyPDF2

# Load documents
documents = []
# ... load PDFs and extract text ...

# Initialize RAG
retriever = RAGRetriever()

# Add documents
retriever.add_documents(documents)

# Save index
retriever.save_index()

# Test retrieval
results = retriever.retrieve("How to increase rice yield?")
for doc, score in results:
    print(f"Score: {score:.4f} - {doc[:100]}...")
```

---

## Model Evaluation

### Cross-Validation

```python
from sklearn.model_selection import cross_val_score

# For yield predictor
cv_scores = cross_val_score(predictor.model, X, y, cv=5, scoring='r2')
print(f"CV R² Scores: {cv_scores}")
print(f"Mean R²: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
```

### Hyperparameter Tuning

Edit `config.yaml` to adjust:
- Learning rates
- Batch sizes
- Model architectures
- Number of epochs

### Model Monitoring

Check `logs/app.log` for training progress and errors.

---

## Best Practices

1. **Data Quality**: Clean and validate data before training
2. **Train-Test Split**: Use 80-20 or 70-30 split
3. **Validation**: Always use validation set
4. **Checkpoints**: Save models after each epoch
5. **Version Control**: Track model versions and performance

---

## Troubleshooting

### Low Performance
- Check data quality and distribution
- Try different hyperparameters
- Add more training data
- Use data augmentation (for images)

### Overfitting
- Reduce model complexity
- Add dropout/regularization
- Increase training data
- Use early stopping

### Memory Issues
- Reduce batch size
- Use gradient accumulation
- Process data in chunks
- Use mixed precision training

---

## Next: Phase 2

Once all Phase 1 models are trained and performing well:
1. Document model performance
2. Create model cards
3. Move to Phase 2: Mini LLM integration
