"""
Training Script for New Agricultural Models
Trains irrigation scheduling and crop nutrient recommendation models
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

def train_irrigation_model():
    """Train irrigation scheduling model from Model5 data."""
    print("\n" + "="*70)
    print("TRAINING IRRIGATION SCHEDULING MODEL")
    print("="*70)
    
    # Check if data exists
    data_path = Path("Model5/Model5/Irrigation Scheduling.csv")
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        print("ℹ️  Please ensure Model5/Model5/Irrigation Scheduling.csv exists")
        return False
    
    # Load data
    print("Loading data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} samples")
    print(f"Columns: {list(df.columns)}")
    
    # Prepare features and target
    # Expected columns: CropType, CropDays, SoilMoisture, temperature, Humidity, SoilType, Irrigation (target)
    
    # Encode categorical variables
    le_crop = LabelEncoder()
    le_soil = LabelEncoder()
    
    df['CropType_encoded'] = le_crop.fit_transform(df['CropType'])
    df['SoilType_encoded'] = le_soil.fit_transform(df['SoilType'])
    
    # Features
    X = df[['CropType_encoded', 'CropDays', 'SoilMoisture', 'temperature', 'Humidity', 'SoilType_encoded']]
    y = df['Irrigation']  # 0 = No irrigation, 1 = Irrigate
    
    print(f"Features shape: {X.shape}")
    print(f"Target distribution: {y.value_counts().to_dict()}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest with GridSearch
    print("\nTraining Random Forest classifier...")
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [10, 20, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
    grid_search.fit(X_train_scaled, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"✓ Best parameters: {grid_search.best_params_}")
    
    # Evaluate
    y_pred = best_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✓ Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['No Irrigation', 'Irrigate']))
    
    # Save model
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'crop_encoder': le_crop,
        'soil_encoder': le_soil,
        'feature_names': ['CropType', 'CropDays', 'SoilMoisture', 'temperature', 'Humidity', 'SoilType'],
        'accuracy': accuracy
    }
    
    model_path = models_dir / "irrigation_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n✓ Model saved to {model_path}")
    print("="*70)
    return True


def train_crop_nutrient_model():
    """Train crop nutrient recommendation model from Model-4 data."""
    print("\n" + "="*70)
    print("TRAINING CROP NUTRIENT RECOMMENDATION MODEL")
    print("="*70)
    
    # Check if data exists
    data_path = Path("Model-4/Model-4/dataset.csv")
    if not data_path.exists():
        print(f"❌ Data file not found: {data_path}")
        print("ℹ️  Please ensure Model-4/Model-4/dataset.csv exists")
        return False
    
    # Load data
    print("Loading data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} samples")
    print(f"Columns: {list(df.columns)}")
    
    # Prepare features and target
    # Expected columns: N, P, K, pH, EC, S, Cu, Fe, Mn, Zn, B, Crop (target)
    
    # Features (11 soil parameters)
    feature_cols = ['N', 'P', 'K', 'pH', 'EC', 'S', 'Cu', 'Fe', 'Mn', 'Zn', 'B']
    X = df[feature_cols]
    y = df['Crop']
    
    print(f"Features shape: {X.shape}")
    print(f"Number of crops: {y.nunique()}")
    print(f"Crop distribution: {y.value_counts().to_dict()}")
    
    # Encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest with GridSearch
    print("\nTraining Random Forest classifier...")
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [15, 25, None],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    
    rf = RandomForestClassifier(random_state=42)
    grid_search = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', n_jobs=-1, verbose=1)
    grid_search.fit(X_train_scaled, y_train)
    
    best_model = grid_search.best_estimator_
    print(f"✓ Best parameters: {grid_search.best_params_}")
    
    # Evaluate
    y_pred = best_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✓ Model Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Save model
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'label_encoder': le,
        'feature_names': feature_cols,
        'accuracy': accuracy
    }
    
    model_path = models_dir / "crop_nutrient_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n✓ Model saved to {model_path}")
    print("="*70)
    return True


if __name__ == "__main__":
    print("\n" + "="*70)
    print("NEW AGRICULTURAL MODELS TRAINING SCRIPT")
    print("="*70)
    print("\nThis script will train:")
    print("1. Irrigation Scheduling Model (Model5)")
    print("2. Crop Nutrient Recommendation Model (Model-4)")
    print("\nMake sure the CSV files exist in the respective folders.")
    print("="*70)
    
    input("\nPress Enter to start training...")
    
    # Train irrigation model
    irrigation_success = train_irrigation_model()
    
    # Train crop nutrient model
    crop_nutrient_success = train_crop_nutrient_model()
    
    # Summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    print(f"Irrigation Model: {'✓ Success' if irrigation_success else '❌ Failed'}")
    print(f"Crop Nutrient Model: {'✓ Success' if crop_nutrient_success else '❌ Failed'}")
    
    if irrigation_success and crop_nutrient_success:
        print("\n🎉 All models trained successfully!")
        print("You can now use these models in your queries:")
        print("  - 'When should I irrigate my wheat?'")
        print("  - 'Which crop is best for my soil with NPK 150-40-250?'")
    else:
        print("\n⚠️ Some models failed to train. Check the errors above.")
    
    print("="*70)
