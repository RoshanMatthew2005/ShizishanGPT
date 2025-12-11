"""
Comprehensive Training Script for All Agricultural Models
Trains 4 models: Irrigation (soil moisture), Crop Nutrient, Crop Climate, Soil Fertility
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import warnings
warnings.filterwarnings('ignore')

print("\n" + "="*80)
print(" " * 15 + "AGRICULTURAL MODELS TRAINING SUITE")
print("="*80)
print("\nThis will train 4 production-ready models:")
print("  1. Soil Moisture Classification (IoT sensor data)")
print("  2. Crop Nutrient Recommendation (11 soil parameters)")
print("  3. Crop Climate Recommendation (NPK + weather)")
print("  4. Soil Fertility Classification (fertility rating)")
print("="*80)

def train_soil_moisture_model():
    """Train soil moisture classification model (IoT sensor data)."""
    print("\n" + "="*80)
    print("MODEL 1: SOIL MOISTURE CLASSIFICATION")
    print("="*80)
    
    data_path = Path("Model5/Model5/Irrigation Scheduling.csv")
    if not data_path.exists():
        print(f"❌ Data not found: {data_path}")
        return False
    
    print("📊 Loading IoT sensor data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} sensor readings")
    print(f"Columns: {list(df.columns)}")
    
    # Features: temperature, pressure, altitude, soilmoisture
    # Target: class (Very Dry, Dry, Wet, Very Wet)
    X = df[['temperature', 'pressure', 'altitude', 'soilmiosture']]  # Note: typo in dataset
    y = df['class']
    
    print(f"\n📈 Data Info:")
    print(f"  Features: {X.shape[1]} (temperature, pressure, altitude, soil moisture)")
    print(f"  Samples: {len(df)}")
    print(f"  Classes: {y.unique().tolist()}")
    print(f"  Distribution: {dict(y.value_counts())}")
    
    # Encode target
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train
    print("\n🔧 Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = rf.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Training Complete!")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))
    
    # Save
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    model_data = {
        'model': rf,
        'scaler': scaler,
        'label_encoder': le,
        'feature_names': ['temperature', 'pressure', 'altitude', 'soil_moisture'],
        'accuracy': accuracy,
        'classes': le.classes_.tolist()
    }
    
    model_path = models_dir / "soil_moisture_model.pkl"
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n💾 Model saved: {model_path}")
    print("="*80)
    return True


def train_crop_nutrient_model():
    """Train crop recommendation based on soil nutrients (11 parameters)."""
    print("\n" + "="*80)
    print("MODEL 2: CROP NUTRIENT RECOMMENDATION")
    print("="*80)
    
    data_path = Path("Model-4/Model-4/dataset.csv")
    if not data_path.exists():
        print(f"❌ Data not found: {data_path}")
        return False
    
    print("📊 Loading soil nutrient data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} samples")
    
    # Features: 11 soil parameters
    feature_cols = ['N', 'P', 'K', 'ph', 'EC', 'S', 'Cu', 'Fe', 'Mn', 'Zn', 'B']
    X = df[feature_cols]
    y = df['label']  # Target crop
    
    print(f"\n📈 Data Info:")
    print(f"  Features: {X.shape[1]} soil parameters")
    print(f"  Samples: {len(df)}")
    print(f"  Crops: {y.nunique()} different crops")
    print(f"  Top 5 crops: {dict(y.value_counts().head())}")
    
    # Encode
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train with GridSearch
    print("\n🔧 Training with GridSearchCV...")
    param_grid = {
        'n_estimators': [150, 200],
        'max_depth': [20, 25],
        'min_samples_split': [2, 5]
    }
    
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    grid = GridSearchCV(rf, param_grid, cv=3, scoring='accuracy', verbose=1)
    grid.fit(X_train_scaled, y_train)
    
    best_model = grid.best_estimator_
    print(f"✓ Best params: {grid.best_params_}")
    
    # Evaluate
    y_pred = best_model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Training Complete!")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"\n📊 Top 10 Feature Importances:")
    importances = sorted(zip(feature_cols, best_model.feature_importances_), 
                        key=lambda x: x[1], reverse=True)
    for feat, imp in importances[:10]:
        print(f"  {feat}: {imp:.4f}")
    
    # Save
    model_data = {
        'model': best_model,
        'scaler': scaler,
        'label_encoder': le,
        'feature_names': feature_cols,
        'accuracy': accuracy,
        'classes': le.classes_.tolist()
    }
    
    model_path = Path("models/crop_nutrient_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n💾 Model saved: {model_path}")
    print("="*80)
    return True


def train_crop_climate_model():
    """Train crop recommendation based on climate (NPK + weather)."""
    print("\n" + "="*80)
    print("MODEL 3: CROP CLIMATE RECOMMENDATION")
    print("="*80)
    
    data_path = Path("Model1/Model1/Crop_recommendation.csv")
    if not data_path.exists():
        print(f"❌ Data not found: {data_path}")
        return False
    
    print("📊 Loading climate data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} samples")
    
    # Features: NPK + weather
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[feature_cols]
    y = df['label']
    
    print(f"\n📈 Data Info:")
    print(f"  Features: {X.shape[1]} (NPK + climate parameters)")
    print(f"  Samples: {len(df)}")
    print(f"  Crops: {y.nunique()} different crops")
    print(f"  Crops list: {y.unique().tolist()}")
    
    # Encode
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train
    print("\n🔧 Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=25,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = rf.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Training Complete!")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"\n📊 Feature Importances:")
    importances = sorted(zip(feature_cols, rf.feature_importances_), 
                        key=lambda x: x[1], reverse=True)
    for feat, imp in importances:
        print(f"  {feat}: {imp:.4f}")
    
    # Save
    model_data = {
        'model': rf,
        'scaler': scaler,
        'label_encoder': le,
        'feature_names': feature_cols,
        'accuracy': accuracy,
        'classes': le.classes_.tolist()
    }
    
    model_path = Path("models/crop_climate_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n💾 Model saved: {model_path}")
    print("="*80)
    return True


def train_soil_fertility_model():
    """Train soil fertility classification (Low/Medium/High)."""
    print("\n" + "="*80)
    print("MODEL 4: SOIL FERTILITY CLASSIFICATION")
    print("="*80)
    
    data_path = Path("Model5/Model5/dataset1.csv")
    if not data_path.exists():
        print(f"❌ Data not found: {data_path}")
        return False
    
    print("📊 Loading soil fertility data...")
    df = pd.read_csv(data_path)
    print(f"✓ Loaded {len(df)} samples")
    
    # Features: 12 soil parameters
    feature_cols = ['N', 'P', 'K', 'pH', 'EC', 'OC', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'B']
    X = df[feature_cols]
    y = df['Output']  # 0, 1, 2 (Low, Medium, High)
    
    print(f"\n📈 Data Info:")
    print(f"  Features: {X.shape[1]} soil parameters")
    print(f"  Samples: {len(df)}")
    print(f"  Classes: {sorted(y.unique())}")
    print(f"  Distribution: {dict(y.value_counts().sort_index())}")
    
    # Map to labels
    fertility_map = {0: 'Low', 1: 'Medium', 2: 'High'}
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train
    print("\n🔧 Training Random Forest...")
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    rf.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = rf.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n✓ Training Complete!")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"\n📊 Classification Report:")
    print(classification_report(y_test, y_pred, 
                                target_names=[fertility_map[i] for i in sorted(fertility_map.keys())]))
    
    # Save
    model_data = {
        'model': rf,
        'scaler': scaler,
        'feature_names': feature_cols,
        'accuracy': accuracy,
        'fertility_map': fertility_map
    }
    
    model_path = Path("models/soil_fertility_model.pkl")
    with open(model_path, 'wb') as f:
        pickle.dump(model_data, f)
    
    print(f"\n💾 Model saved: {model_path}")
    print("="*80)
    return True


if __name__ == "__main__":
    print("\n🚀 Starting comprehensive model training...")
    print("This will take several minutes. Please wait...\n")
    
    results = {}
    
    # Train all models
    results['soil_moisture'] = train_soil_moisture_model()
    results['crop_nutrient'] = train_crop_nutrient_model()
    results['crop_climate'] = train_crop_climate_model()
    results['soil_fertility'] = train_soil_fertility_model()
    
    # Final summary
    print("\n" + "="*80)
    print(" " * 30 + "TRAINING SUMMARY")
    print("="*80)
    print(f"\n{'Model':<35} {'Status':<15} {'File':<30}")
    print("-"*80)
    print(f"{'1. Soil Moisture Classification':<35} {'✓ Success' if results['soil_moisture'] else '❌ Failed':<15} {'soil_moisture_model.pkl':<30}")
    print(f"{'2. Crop Nutrient Recommendation':<35} {'✓ Success' if results['crop_nutrient'] else '❌ Failed':<15} {'crop_nutrient_model.pkl':<30}")
    print(f"{'3. Crop Climate Recommendation':<35} {'✓ Success' if results['crop_climate'] else '❌ Failed':<15} {'crop_climate_model.pkl':<30}")
    print(f"{'4. Soil Fertility Classification':<35} {'✓ Success' if results['soil_fertility'] else '❌ Failed':<15} {'soil_fertility_model.pkl':<30}")
    print("="*80)
    
    success_count = sum(results.values())
    if success_count == 4:
        print("\n🎉 ALL MODELS TRAINED SUCCESSFULLY!")
        print("\n📝 Next Steps:")
        print("  1. Restart your backend server")
        print("  2. Test with queries like:")
        print("     • 'What's the soil moisture status? Temperature 30°C, moisture 350'")
        print("     • 'Which crop for soil with N=150, P=40, K=250, pH=6.5?'")
        print("     • 'Recommend crop for 25°C, 80% humidity, rainfall 200mm'")
        print("     • 'Check soil fertility with N=200, P=50, pH=7.0'")
    else:
        print(f"\n⚠️  {success_count}/4 models trained successfully")
        print("Check the errors above for failed models.")
    
    print("\n" + "="*80)
