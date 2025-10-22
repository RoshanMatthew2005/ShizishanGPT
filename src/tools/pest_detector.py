"""
Pest and Disease Detection Model
CNN-based image classification for crop diseases
"""

import torch
import torch.nn as nn
import torchvision.models as models
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import yaml
import os


class PestDetector:
    """
    CNN-based Pest and Disease Detection Model
    Uses ResNet architecture for image classification
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize Pest Detector
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model_config = self.config['pest_model']
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.class_names = []
        
        # Image transforms
        self.transform = transforms.Compose([
            transforms.Resize(tuple(self.model_config['image_size'])),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def build_model(self, num_classes: int):
        """
        Build ResNet model
        
        Args:
            num_classes: Number of disease classes
        """
        print(f"🐛 Building {self.model_config['architecture']} model...")
        
        if self.model_config['architecture'] == 'resnet50':
            self.model = models.resnet50(pretrained=True)
        elif self.model_config['architecture'] == 'resnet18':
            self.model = models.resnet18(pretrained=True)
        
        # Modify final layer for our classes
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, num_classes)
        
        self.model = self.model.to(self.device)
        print(f"✅ Model built on {self.device}")
    
    def train(self, train_loader, val_loader, class_names: list):
        """
        Train the pest detection model
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            class_names: List of disease class names
        """
        self.class_names = class_names
        
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(
            self.model.parameters(), 
            lr=self.model_config['learning_rate']
        )
        
        print(f"🚀 Training for {self.model_config['epochs']} epochs...")
        
        # Training loop would go here
        # This is a placeholder - implement full training loop
        
        print("✅ Training completed!")
    
    def predict(self, image_path: str) -> dict:
        """
        Predict disease from image
        
        Args:
            image_path: Path to crop image
            
        Returns:
            Dictionary with predicted class and confidence
        """
        if self.model is None:
            raise ValueError("Model not built! Call build_model() first.")
        
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probabilities, 1)
        
        predicted_class = self.class_names[predicted.item()]
        confidence_score = confidence.item()
        
        return {
            'disease': predicted_class,
            'confidence': confidence_score
        }
    
    def save_model(self, filepath: str = None):
        """
        Save trained model
        
        Args:
            filepath: Path to save model
        """
        if filepath is None:
            filepath = self.config['models']['pest_detector']
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'class_names': self.class_names
        }, filepath)
        
        print(f"💾 Model saved to {filepath}")
    
    def load_model(self, filepath: str = None):
        """
        Load trained model
        
        Args:
            filepath: Path to load model from
        """
        if filepath is None:
            filepath = self.config['models']['pest_detector']
        
        checkpoint = torch.load(filepath, map_location=self.device)
        self.class_names = checkpoint['class_names']
        
        self.build_model(len(self.class_names))
        self.model.load_state_dict(checkpoint['model_state_dict'])
        
        print(f"✅ Model loaded from {filepath}")


def main():
    """Example usage of PestDetector"""
    detector = PestDetector()
    print("🐛 Pest Detector initialized!")
    print("⚠️ Note: Train with image dataset or load pre-trained model")


if __name__ == "__main__":
    main()
