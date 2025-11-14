"""
Train Weather Impact Model using the same crop yield dataset.
Features: Annual_Rainfall, Fertilizer, Pesticide
Target: Yield
Also computes correlation coefficients between rainfall and yield.
"""
import os
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import warnings

warnings.filterwarnings('ignore')


def load_data(csv_path: str) -> pd.DataFrame:
    """Load crop yield dataset from CSV file."""
    print(f"Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Dataset shape: {df.shape}")
    print(f"\nFirst 5 rows:\n{df.head()}")
    print(f"\nDataset columns: {df.columns.tolist()}")
    return df


def preprocess_data(df: pd.DataFrame) -> tuple:
    """
    Preprocess the dataset for weather impact analysis:
    - Handle missing values
    - Select weather-related features
    - Prepare features and target
    """
    print("\n" + "="*70)
    print("PREPROCESSING DATA FOR WEATHER IMPACT ANALYSIS")
    print("="*70)
    
    # Create a copy
    df_clean = df.copy()
    
    # Handle missing values - drop rows with missing target
    df_clean = df_clean.dropna(subset=['Yield'])
    
    # Fill missing values in features with median
    weather_features = ['Annual_Rainfall', 'Fertilizer', 'Pesticide']
    for col in weather_features:
        if col in df_clean.columns:
            df_clean[col].fillna(df_clean[col].median(), inplace=True)
    
    print(f"After cleaning, dataset shape: {df_clean.shape}")
    print(f"Missing values after cleaning:\n{df_clean[weather_features + ['Yield']].isnull().sum()}")
    
    # Define features and target
    X = df_clean[weather_features]
    y = df_clean['Yield']
    
    print(f"\nFeatures shape: {X.shape}")
    print(f"Target shape: {y.shape}")
    print(f"Feature columns: {weather_features}")
    
    return X, y, df_clean


def analyze_correlations(df: pd.DataFrame):
    """
    Compute and display correlation coefficients between weather factors and yield.
    """
    print("\n" + "="*70)
    print("CORRELATION ANALYSIS")
    print("="*70)
    
    # Correlation matrix for weather features and yield
    weather_cols = ['Annual_Rainfall', 'Fertilizer', 'Pesticide', 'Yield']
    corr_matrix = df[weather_cols].corr()
    
    print("\nCorrelation Matrix:")
    print(corr_matrix)
    
    # Extract correlations with Yield
    yield_corr = corr_matrix['Yield'].drop('Yield')
    
    print("\n" + "="*70)
    print("CORRELATIONS WITH YIELD")
    print("="*70)
    for feature, corr_value in yield_corr.items():
        print(f"{feature:20s}: {corr_value:+.4f}")
    
    # Generate insight message
    rainfall_corr = yield_corr['Annual_Rainfall']
    fertilizer_corr = yield_corr['Fertilizer']
    
    insight = f"Rainfall has a {rainfall_corr:+.2f} correlation with Yield."
    if abs(fertilizer_corr) > 0.3:
        insight += f" Fertilizer shows {'strong positive' if fertilizer_corr > 0 else 'negative'} correlation ({fertilizer_corr:+.2f})."
    
    print(f"\n📊 INSIGHT: {insight}")
    
    return yield_corr, insight


def train_model(X: pd.DataFrame, y: pd.Series) -> tuple:
    """
    Train RandomForest Regressor for weather impact prediction.
    Returns trained model and test metrics.
    """
    print("\n" + "="*70)
    print("TRAINING WEATHER IMPACT MODEL")
    print("="*70)
    
    # Split dataset (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"Training set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    
    # Train RandomForest Regressor
    print("\nTraining RandomForest Regressor...")
    model = RandomForestRegressor(
        n_estimators=80,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    print("✓ Model training complete")
    
    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    print("\n" + "="*70)
    print("MODEL PERFORMANCE METRICS")
    print("="*70)
    print(f"Training R² Score:   {train_r2:.4f}")
    print(f"Test R² Score:       {test_r2:.4f}")
    print(f"Training RMSE:       {train_rmse:.4f}")
    print(f"Test RMSE:           {test_rmse:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\nFeature Importance:")
    print(feature_importance)
    
    return model, test_r2, test_rmse


def save_model(model, correlations: pd.Series, insight: str, save_path: str):
    """Save trained weather model, correlations, and insights to disk."""
    print("\n" + "="*70)
    print("SAVING WEATHER IMPACT MODEL")
    print("="*70)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save model, correlations, and insight together
    model_package = {
        'model': model,
        'correlations': correlations.to_dict(),
        'insight': insight,
        'feature_names': ['Annual_Rainfall', 'Fertilizer', 'Pesticide']
    }
    
    joblib.dump(model_package, save_path)
    print(f"✓ Model saved to: {save_path}")
    
    # Verify file size
    file_size = os.path.getsize(save_path) / (1024 * 1024)
    print(f"✓ Model file size: {file_size:.2f} MB")


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("WEATHER IMPACT MODEL TRAINING")
    print("="*70)
    
    # Define paths
    project_root = Path(__file__).parent.parent
    csv_path = project_root / "Data" / "csv" / "crop_yield.csv"
    model_save_path = project_root / "models" / "trained_models" / "weather_model.pkl"
    
    # Step 1: Load data
    df = load_data(str(csv_path))
    
    # Step 2: Preprocess data
    X, y, df_clean = preprocess_data(df)
    
    # Step 3: Analyze correlations
    correlations, insight = analyze_correlations(df_clean)
    
    # Step 4: Train model
    model, test_r2, test_rmse = train_model(X, y)
    
    # Step 5: Save model
    save_model(model, correlations, insight, str(model_save_path))
    
    # Final summary
    print("\n" + "="*70)
    print("TRAINING SUMMARY")
    print("="*70)
    print(f"✓ Dataset loaded: {len(df)} rows")
    print(f"✓ Features used: {X.shape[1]} (weather-related)")
    print(f"✓ Model: RandomForest Regressor")
    print(f"✓ Test R² Score: {test_r2:.4f}")
    print(f"✓ Test RMSE: {test_rmse:.4f}")
    print(f"✓ Rainfall-Yield Correlation: {correlations['Annual_Rainfall']:+.4f}")
    print(f"✓ Model saved: {model_save_path}")
    print(f"\n📊 {insight}")
    print("\n✅ Weather Impact Model training complete!")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during training: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
