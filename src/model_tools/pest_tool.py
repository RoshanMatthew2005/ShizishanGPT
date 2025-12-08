"""
Pest Detection Tool
Loads the trained ResNet18 model and classifies plant diseases from images.
"""
import torch
import json
import re
import random
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image
import torchvision.transforms as transforms

# Sample images database for testing
SAMPLE_IMAGES = {
    'tomato_bacterial_spot': 'Data/images/PlantVillage/Tomato_Bacterial_spot',
    'tomato_yellow_leaf_curl': 'Data/images/PlantVillage/Tomato__Tomato_YellowLeaf__Curl_Virus',
    'tomato_mosaic_virus': 'Data/images/PlantVillage/Tomato__Tomato_mosaic_virus',
    'tomato_target_spot': 'Data/images/PlantVillage/Tomato__Target_Spot',
    'potato_early_blight': 'Data/images/PlantVillage/Potato___Early_blight',
    'potato_late_blight': 'Data/images/PlantVillage/Potato___Late_blight',
    'potato_healthy': 'Data/images/PlantVillage/Potato___healthy',
    'pepper_bacterial_spot': 'Data/images/PlantVillage/Pepper__bell___Bacterial_spot',
    'pepper_healthy': 'Data/images/PlantVillage/Pepper__bell___healthy'
}


class PestTool:
    """Tool for detecting plant pests and diseases from images."""
    
    def __init__(self, 
                 model_path: str = "models/trained_models/pest_model.pt",
                 labels_path: str = "models/trained_models/class_labels.json"):
        """
        Initialize the Pest Detection Tool.
        
        Args:
            model_path: Path to the trained pest detection model
            labels_path: Path to class labels JSON
        """
        self.name = "pest_detection"
        self.description = "Identifies plant diseases and pests from leaf images"
        self.model_path = Path(model_path)
        self.labels_path = Path(labels_path)
        self.model = None
        self.class_labels = None
        self.is_loaded = False
        
        # Define image transforms
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                std=[0.229, 0.224, 0.225])
        ])
        
    def get_sample_image(self, query: str = "") -> Optional[str]:
        """
        Find a sample image based on query keywords.
        
        Args:
            query: User query (e.g., "tomato bacterial spot")
            
        Returns:
            Path to a sample image or None
        """
        query_lower = query.lower()
        
        # Try to match query to sample categories
        for category, folder_path in SAMPLE_IMAGES.items():
            category_keywords = category.replace('_', ' ').split()
            if any(keyword in query_lower for keyword in category_keywords):
                folder = Path(folder_path)
                if folder.exists():
                    # Get first image from folder
                    images = list(folder.glob('*.jpg')) + list(folder.glob('*.JPG'))
                    if images:
                        selected = random.choice(images[:5])  # Pick from first 5
                        print(f"✓ Selected sample image from: {category}")
                        return str(selected)
        
        # If no match, return any random sample
        for folder_path in SAMPLE_IMAGES.values():
            folder = Path(folder_path)
            if folder.exists():
                images = list(folder.glob('*.jpg')) + list(folder.glob('*.JPG'))
                if images:
                    selected = random.choice(images[:3])
                    print(f"ℹ️ Using random sample image")
                    return str(selected)
        
        return None
    
    def parse_query(self, query: str) -> Optional[str]:
        """
        Parse query to extract image path or find sample image.
        
        Args:
            query: User query
            
        Returns:
            Image path or None
        """
        # Check if query contains a file path
        path_patterns = [
            r'[A-Za-z]:\\[\\\\w\\s.-]+\\.(jpg|jpeg|png|bmp)',  # Windows path
            r'/[/\\w\\s.-]+\\.(jpg|jpeg|png|bmp)',  # Unix path
            r'Data/images/[\\w/.-]+\\.(jpg|jpeg|png|bmp)'  # Relative path
        ]
        
        for pattern in path_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                path = match.group(0)
                if Path(path).exists():
                    print(f"✓ Extracted image path from query: {path}")
                    return path
        
        # Check for "sample" or "demo" keywords
        if any(word in query.lower() for word in ['sample', 'demo', 'example', 'test']):
            return self.get_sample_image(query)
        
        # If query mentions disease/crop, try to find sample
        disease_keywords = ['disease', 'spot', 'blight', 'virus', 'tomato', 'potato', 'pepper']
        if any(word in query.lower() for word in disease_keywords):
            return self.get_sample_image(query)
        
        return None
    
    def load_model(self) -> bool:
        """Load the trained model and class labels from disk."""
        try:
            # Check if files exist
            if not self.model_path.exists():
                print(f"❌ Model not found: {self.model_path}")
                return False
            
            if not self.labels_path.exists():
                print(f"❌ Labels not found: {self.labels_path}")
                return False
            
            # Load class labels
            with open(self.labels_path, 'r') as f:
                self.class_labels = json.load(f)
            
            # Load model - handle both full model and state_dict
            checkpoint = torch.load(self.model_path, map_location='cpu')
            
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                # Checkpoint format with state_dict
                from torchvision.models import resnet18
                self.model = resnet18()
                # Modify final layer to match number of classes
                num_classes = len(self.class_labels)
                self.model.fc = torch.nn.Linear(self.model.fc.in_features, num_classes)
                self.model.load_state_dict(checkpoint['model_state_dict'])
            elif isinstance(checkpoint, dict) and not hasattr(checkpoint, 'eval'):
                # Just a state_dict
                from torchvision.models import resnet18
                self.model = resnet18()
                num_classes = len(self.class_labels)
                self.model.fc = torch.nn.Linear(self.model.fc.in_features, num_classes)
                self.model.load_state_dict(checkpoint)
            else:
                # Full model
                self.model = checkpoint
            
            self.model.eval()
            
            self.is_loaded = True
            print(f"✓ Pest model loaded from {self.model_path}")
            print(f"✓ Loaded {len(self.class_labels)} disease classes")
            return True
            
        except Exception as e:
            print(f"❌ Error loading pest model: {e}")
            return False
    
    def validate_input(self, image_path: str) -> tuple[bool, Optional[str]]:
        """
        Validate input image path.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            (is_valid, error_message)
        """
        if not image_path:
            return False, "Image path cannot be empty"
        
        path = Path(image_path)
        if not path.exists():
            return False, f"Image file not found: {image_path}"
        
        # Check file extension
        valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
        if path.suffix.lower() not in valid_extensions:
            return False, f"Unsupported image format: {path.suffix}"
        
        return True, None
    
    def preprocess_image(self, image_path: str) -> Optional[torch.Tensor]:
        """
        Load and preprocess an image for model inference.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image tensor or None if failed
        """
        try:
            image = Image.open(image_path).convert('RGB')
            image_tensor = self.transform(image)
            image_tensor = image_tensor.unsqueeze(0)  # Add batch dimension
            return image_tensor
        except Exception as e:
            print(f"Error preprocessing image: {e}")
            return None
    
    def run(self, query: str = "", image_path: str = "", top_k: int = 3) -> Dict[str, Any]:
        """
        Execute pest/disease detection on an image.
        
        Args:
            query: Natural language query (will attempt to extract/find image)
            image_path: Direct path to the leaf image (optional)
            top_k: Number of top predictions to return (default: 3)
        
        Returns:
            Dictionary with detection results
        """
        try:
            # Load model if not already loaded
            if not self.is_loaded:
                if not self.load_model():
                    return {
                        "success": False,
                        "error": "Failed to load pest detection model",
                        "tool": self.name
                    }
            
            # If no image_path provided, try to extract/find from query
            if not image_path and query:
                print(f"🔍 Parsing query for image: '{query}'")
                image_path = self.parse_query(query)
            
            # If still no image, provide helpful guidance
            if not image_path:
                return {
                    "success": False,
                    "error": "No image provided",
                    "tool": self.name,
                    "guidance": {
                        "message": "Pest detection requires an image. You can:",
                        "options": [
                            "1. Upload an image through the web interface",
                            "2. Request a sample analysis: 'Analyze sample tomato disease image'",
                            "3. Provide an image path: 'Detect disease in Data/images/PlantVillage/...'"
                        ],
                        "sample_categories": list(SAMPLE_IMAGES.keys())
                    }
                }
            
            # Validate input
            is_valid, error_msg = self.validate_input(image_path)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "tool": self.name
                }
            
            # Preprocess image
            image_tensor = self.preprocess_image(image_path)
            if image_tensor is None:
                return {
                    "success": False,
                    "error": "Failed to preprocess image",
                    "tool": self.name
                }
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                top_probs, top_indices = torch.topk(probabilities, min(top_k, len(self.class_labels)))
            
            # Format predictions
            predictions = []
            for prob, idx in zip(top_probs[0], top_indices[0]):
                predictions.append({
                    "disease": self.class_labels[str(idx.item())],
                    "confidence": float(prob.item()),
                    "percentage": f"{prob.item() * 100:.2f}%"
                })
            
            return {
                "success": True,
                "tool": self.name,
                "image": str(image_path),
                "top_prediction": predictions[0]['disease'],
                "confidence": predictions[0]['confidence'],
                "all_predictions": predictions
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Pest detection failed: {str(e)}",
                "tool": self.name
            }
    
    def __call__(self, query: str = "", image_path: str = "", top_k: int = 3) -> Dict[str, Any]:
        """Allow the tool to be called directly."""
        return self.run(query=query, image_path=image_path, top_k=top_k)


# Example usage
if __name__ == "__main__":
    tool = PestTool()
    
    # Test with a sample image (update path to actual image)
    sample_image = "Data/images/PlantVillage/Pepper__bell___healthy/test_image.jpg"
    
    result = tool.run(sample_image)
    
    print("\n" + "="*70)
    print("PEST DETECTION TEST")
    print("="*70)
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Image: {result['image']}")
        print(f"Top Prediction: {result['top_prediction']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"\nAll Predictions:")
        for i, pred in enumerate(result['all_predictions'], 1):
            print(f"  {i}. {pred['disease']} - {pred['percentage']}")
    else:
        print(f"Error: {result['error']}")
    print("="*70)
