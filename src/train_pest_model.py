"""
Train Pest/Disease Detection Model using ResNet18 and PlantVillage dataset.
Identifies crop leaf diseases from images using transfer learning.
"""
import os
import sys
import json
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, models, transforms
import time
import copy
from tqdm import tqdm


def get_data_transforms():
    """
    Define data augmentation and normalization transforms.
    Uses ImageNet normalization values for pretrained models.
    """
    data_transforms = {
        'train': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(10),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ]),
        'val': transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    }
    return data_transforms


def load_dataset(data_dir: Path, batch_size: int = 32):
    """
    Load images using ImageFolder and split into train/validation sets.
    
    Args:
        data_dir: Path to directory containing image folders
        batch_size: Batch size for DataLoader
        
    Returns:
        dataloaders, dataset_sizes, class_names
    """
    print("\n" + "="*70)
    print("LOADING DATASET")
    print("="*70)
    
    print(f"Loading images from: {data_dir}")
    
    # Get transforms
    data_transforms = get_data_transforms()
    
    # Load full dataset with training transforms initially
    full_dataset = datasets.ImageFolder(
        root=str(data_dir),
        transform=data_transforms['train']
    )
    
    # Get class names
    class_names = full_dataset.classes
    num_classes = len(class_names)
    
    print(f"\nFound {len(full_dataset)} images")
    print(f"Number of classes: {num_classes}")
    print(f"\nClasses: {class_names}")
    
    # Calculate split sizes (80% train, 20% validation)
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    
    print(f"\nSplit: {train_size} training, {val_size} validation")
    
    # Split dataset
    train_dataset, val_dataset = random_split(
        full_dataset, 
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    # Apply different transforms to validation set
    # Create a copy for validation with validation transforms
    val_dataset_transformed = datasets.ImageFolder(
        root=str(data_dir),
        transform=data_transforms['val']
    )
    
    # Use the same indices from the split
    val_indices = val_dataset.indices
    val_subset = torch.utils.data.Subset(val_dataset_transformed, val_indices)
    
    # Create dataloaders
    dataloaders = {
        'train': DataLoader(train_dataset, batch_size=batch_size, 
                          shuffle=True, num_workers=0, pin_memory=True),
        'val': DataLoader(val_subset, batch_size=batch_size, 
                        shuffle=False, num_workers=0, pin_memory=True)
    }
    
    dataset_sizes = {'train': train_size, 'val': val_size}
    
    return dataloaders, dataset_sizes, class_names


def build_model(num_classes: int, device):
    """
    Build ResNet18 model with pretrained weights.
    Replace final layer to match number of disease classes.
    
    Args:
        num_classes: Number of output classes
        device: Device to load model on (cuda/cpu)
        
    Returns:
        model, criterion, optimizer
    """
    print("\n" + "="*70)
    print("BUILDING MODEL")
    print("="*70)
    
    # Load pretrained ResNet18
    print("Loading ResNet18 with pretrained ImageNet weights...")
    model = models.resnet18(pretrained=True)
    
    # Freeze early layers (optional - comment out for full fine-tuning)
    # for param in model.parameters():
    #     param.requires_grad = False
    
    # Replace final fully connected layer
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, num_classes)
    
    print(f"Modified final layer: {num_features} -> {num_classes} classes")
    
    # Move model to device
    model = model.to(device)
    
    # Define loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.1)
    
    print(f"✓ Model loaded on: {device}")
    print(f"✓ Total parameters: {sum(p.numel() for p in model.parameters()):,}")
    print(f"✓ Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}")
    
    return model, criterion, optimizer, scheduler


def train_model(model, dataloaders, dataset_sizes, criterion, optimizer, 
                scheduler, device, num_epochs=10):
    """
    Train the model and track best weights.
    
    Args:
        model: PyTorch model
        dataloaders: Dict of train/val dataloaders
        dataset_sizes: Dict of train/val sizes
        criterion: Loss function
        optimizer: Optimizer
        scheduler: Learning rate scheduler
        device: Device for training
        num_epochs: Number of epochs to train
        
    Returns:
        model with best weights, training history
    """
    print("\n" + "="*70)
    print("TRAINING MODEL")
    print("="*70)
    
    since = time.time()
    
    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    
    history = {
        'train_loss': [], 'train_acc': [],
        'val_loss': [], 'val_acc': []
    }
    
    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch + 1}/{num_epochs}')
        print('-' * 70)
        
        # Each epoch has training and validation phase
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()
            
            running_loss = 0.0
            running_corrects = 0
            
            # Progress bar
            pbar = tqdm(dataloaders[phase], 
                       desc=f'{phase.capitalize():5s}',
                       leave=True)
            
            # Iterate over data
            for inputs, labels in pbar:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                # Zero parameter gradients
                optimizer.zero_grad()
                
                # Forward pass
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)
                    
                    # Backward + optimize only in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                
                # Statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data)
                
                # Update progress bar
                pbar.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'acc': f'{(torch.sum(preds == labels.data).double() / inputs.size(0)):.4f}'
                })
            
            if phase == 'train':
                scheduler.step()
            
            epoch_loss = running_loss / dataset_sizes[phase]
            epoch_acc = running_corrects.double() / dataset_sizes[phase]
            
            print(f'{phase.capitalize():5s} Loss: {epoch_loss:.4f} Acc: {epoch_acc:.4f}')
            
            # Save history
            history[f'{phase}_loss'].append(epoch_loss)
            history[f'{phase}_acc'].append(epoch_acc.item())
            
            # Deep copy the model if best validation accuracy
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())
                print(f'✓ New best validation accuracy: {best_acc:.4f}')
    
    time_elapsed = time.time() - since
    print('\n' + '='*70)
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'Best validation accuracy: {best_acc:.4f}')
    print('='*70)
    
    # Load best model weights
    model.load_state_dict(best_model_wts)
    return model, history


def save_model(model, class_names, save_dir: Path):
    """
    Save trained model and class labels.
    
    Args:
        model: Trained PyTorch model
        class_names: List of class names
        save_dir: Directory to save model and labels
    """
    print("\n" + "="*70)
    print("SAVING MODEL")
    print("="*70)
    
    # Create directory if it doesn't exist
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model
    model_path = save_dir / "pest_model.pt"
    torch.save(model.state_dict(), model_path)
    print(f"✓ Model saved to: {model_path}")
    
    # Verify file size
    file_size = model_path.stat().st_size / (1024 * 1024)
    print(f"✓ Model file size: {file_size:.2f} MB")
    
    # Save class labels
    labels_path = save_dir / "class_labels.json"
    class_mapping = {i: name for i, name in enumerate(class_names)}
    
    with open(labels_path, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    print(f"✓ Class labels saved to: {labels_path}")
    print(f"✓ Number of classes: {len(class_names)}")


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("PEST/DISEASE DETECTION MODEL TRAINING")
    print("="*70)
    
    # Define paths
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "Data" / "images" / "PlantVillage" / "PlantVillage"
    save_dir = project_root / "models" / "trained_models"
    
    # Check if data directory exists
    if not data_dir.exists():
        print(f"❌ Error: Data directory not found at {data_dir}")
        print("Please ensure images are in Data/images/PlantVillage/PlantVillage/")
        sys.exit(1)
    
    # Set device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    print(f"\nUsing device: {device}")
    if torch.cuda.is_available():
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    # Hyperparameters
    batch_size = 32
    num_epochs = 10
    
    # Step 1: Load dataset
    dataloaders, dataset_sizes, class_names = load_dataset(data_dir, batch_size)
    
    # Step 2: Build model
    num_classes = len(class_names)
    model, criterion, optimizer, scheduler = build_model(num_classes, device)
    
    # Step 3: Train model
    model, history = train_model(
        model, dataloaders, dataset_sizes, 
        criterion, optimizer, scheduler, 
        device, num_epochs
    )
    
    # Step 4: Save model
    save_model(model, class_names, save_dir)
    
    # Final summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    print(f"✓ Dataset: {sum(dataset_sizes.values())} images")
    print(f"✓ Classes: {num_classes}")
    print(f"✓ Architecture: ResNet18 (pretrained)")
    print(f"✓ Epochs trained: {num_epochs}")
    print(f"✓ Best validation accuracy: {max(history['val_acc']):.4f}")
    print(f"✓ Final training accuracy: {history['train_acc'][-1]:.4f}")
    print(f"✓ Model saved: {save_dir / 'pest_model.pt'}")
    print(f"✓ Labels saved: {save_dir / 'class_labels.json'}")
    print("\n✅ Pest/Disease Detection Model training complete!")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Training interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
