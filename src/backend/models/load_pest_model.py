"""
Pest Model Loader
Loads and manages the pest/disease detection model
"""

import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from pathlib import Path
import json
import logging
import io
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PestModel:
    """
    Wrapper for pest detection model (ResNet18)
    """
    
    def __init__(self, model_path: str, classes_path: str):
        self.model_path = Path(model_path)
        self.classes_path = Path(classes_path)
        self.model = None
        self.class_names = []
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def load(self):
        """Load the pest detection model"""
        try:
            # Load class names
            if self.classes_path.exists():
                with open(self.classes_path, 'r') as f:
                    class_data = json.load(f)
                    # Handle different JSON formats
                    if 'classes' in class_data:
                        self.class_names = class_data['classes']
                    elif isinstance(class_data, dict) and all(k.isdigit() for k in class_data.keys()):
                        # Handle numbered class format {"0": "class1", "1": "class2", ...}
                        self.class_names = [class_data[str(i)] for i in sorted(int(k) for k in class_data.keys())]
                    else:
                        self.class_names = list(class_data.values()) if isinstance(class_data, dict) else class_data
                logger.info(f"✓ Loaded {len(self.class_names)} class names")
            else:
                logger.warning(f"Classes file not found: {self.classes_path}")
                # Use default class names
                self.class_names = [
                    "Pepper__bell___Bacterial_spot",
                    "Pepper__bell___healthy",
                    "Potato___Early_blight",
                    "Potato___healthy",
                    "Potato___Late_blight",
                    "Tomato__Target_Spot",
                    "Tomato__Tomato_mosaic_virus",
                    "Tomato__Tomato_YellowLeaf__Curl_Virus",
                    "Tomato_Bacterial_spot"
                ]
            
            # Load model
            if self.model_path.exists():
                # Create ResNet18 model
                self.model = models.resnet18(weights=None)
                num_classes = len(self.class_names)
                self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)
                
                # Load weights
                checkpoint = torch.load(self.model_path, map_location=self.device)
                
                # Handle different checkpoint formats
                if isinstance(checkpoint, dict):
                    if 'model_state_dict' in checkpoint:
                        self.model.load_state_dict(checkpoint['model_state_dict'])
                    elif 'state_dict' in checkpoint:
                        self.model.load_state_dict(checkpoint['state_dict'])
                    else:
                        self.model.load_state_dict(checkpoint)
                else:
                    self.model.load_state_dict(checkpoint)
                
                self.model.to(self.device)
                self.model.eval()
                
                self.loaded = True
                logger.info(f"✓ Pest model loaded from {self.model_path}")
                logger.info(f"✓ Device: {self.device}")
                return True
            else:
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
                
        except Exception as e:
            logger.error(f"Failed to load pest model: {e}")
            self.loaded = False
            return False
    
    def predict(self, image_input, top_k: int = 3) -> Dict[str, Any]:
        """
        Predict pest/disease from image
        
        Args:
            image_input: PIL Image object, file path string, or bytes
            top_k: Number of top predictions to return
        
        Returns:
            Dictionary with predictions and metadata
        """
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        try:
            # Load and preprocess image
            if isinstance(image_input, Image.Image):
                image = image_input.convert('RGB')
            elif isinstance(image_input, (str, bytes)):
                if isinstance(image_input, bytes):
                    image = Image.open(io.BytesIO(image_input)).convert('RGB')
                else:
                    image = Image.open(image_input).convert('RGB')
            else:
                raise ValueError(f"Unsupported image_input type: {type(image_input)}")
            
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # Get top-k predictions
            top_probs, top_indices = torch.topk(probabilities, min(top_k, len(self.class_names)))
            
            # Format results
            all_predictions = []
            for i in range(len(top_indices[0])):
                idx = top_indices[0][i].item()
                prob = top_probs[0][i].item()
                
                disease_name = self.class_names[idx] if idx < len(self.class_names) else f"Class_{idx}"
                
                all_predictions.append({
                    "class": disease_name,  # Changed from "disease" to match service expectations
                    "confidence": float(prob)
                })
            
            # Get recommendations based on top prediction
            top_disease = all_predictions[0]["disease"]
            recommendations = self._get_recommendations(top_disease)
            
            result = {
                "disease": all_predictions[0]["class"],  # Use class from prediction
                "confidence": all_predictions[0]["confidence"],
                "predictions": all_predictions,  # Changed from all_predictions
                "recommendations": recommendations
            }
            
            logger.info(f"Pest detection: {top_disease} ({all_predictions[0]['confidence']:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Pest detection failed: {e}")
            raise
    
    def _get_recommendations(self, disease: str) -> List[str]:
        """
        Get treatment recommendations for detected disease
        """
        recommendations_db = {
            "healthy": [
                "Plant appears healthy",
                "Continue regular monitoring",
                "Maintain good agricultural practices"
            ],
            "Bacterial_spot": [
                "Remove infected leaves immediately",
                "Apply copper-based bactericide",
                "Improve air circulation",
                "Avoid overhead watering"
            ],
            "Early_blight": [
                "Remove infected plant debris",
                "Apply fungicide containing chlorothalonil",
                "Practice crop rotation",
                "Mulch around plants to prevent soil splash"
            ],
            "Late_blight": [
                "Remove and destroy infected plants",
                "Apply fungicide (mancozeb or chlorothalonil)",
                "Ensure good drainage",
                "Avoid watering in the evening"
            ],
            "mosaic_virus": [
                "Remove infected plants immediately",
                "Control aphid population",
                "Use virus-resistant varieties",
                "Disinfect tools between plants"
            ]
        }
        
        # Match disease name to recommendations
        for key, recs in recommendations_db.items():
            if key.lower() in disease.lower():
                return recs
        
        # Default recommendations
        return [
            "Consult with local agricultural extension service",
            "Consider laboratory diagnosis for accurate identification",
            "Isolate affected plants",
            "Monitor neighboring plants for symptoms"
        ]


def load_pest_model(model_path: str, classes_path: str) -> PestModel:
    """
    Factory function to load pest model
    """
    model = PestModel(model_path, classes_path)
    model.load()
    return model
