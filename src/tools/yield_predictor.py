"""
Yield Prediction Model
Predicts crop yield based on soil nutrients, weather, and environmental factors
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import yaml
import os
from pathlib import Path


class YieldPredictor:
    """
    Random Forest based Yield Prediction Model
    Predicts crop yield based on agricultural features
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize Yield Predictor
        
        Args:
            config_path: Path to configuration file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model_config = self.config['yield_model']
        self.model = None
        self.feature_names = self.model_config['features']
        self.target_name = self.model_config['target']
        
    def train(self, data: pd.DataFrame):
        """
        Train the yield prediction model
        
        Args:
            data: DataFrame containing features and target
        """
        print("🌾 Training Yield Prediction Model...")
        
        # Prepare features and target
        X = data[self.feature_names]
        y = data[self.target_name]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=self.model_config['test_size'],
            random_state=self.model_config['random_state']
        )
        
        # Initialize and train model
        if self.model_config['algorithm'] == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                random_state=self.model_config['random_state'],
                n_jobs=-1
            )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"✅ Model Trained Successfully!")
        print(f"   📊 RMSE: {rmse:.4f}")
        print(f"   📊 MAE: {mae:.4f}")
        print(f"   📊 R² Score: {r2:.4f}")
        
        return {
            'rmse': rmse,
            'mae': mae,
            'r2_score': r2
        }
    
    def predict(self, input_data: dict) -> float:
        """
        Predict yield for given input
        
        Args:
            input_data: Dictionary with feature values
            
        Returns:
            Predicted yield value
        """
        if self.model is None:
            raise ValueError("Model not trained! Call train() first or load a trained model.")
        
        # Convert input to DataFrame
        input_df = pd.DataFrame([input_data])
        
        # Ensure correct feature order
        input_df = input_df[self.feature_names]
        
        # Predict
        prediction = self.model.predict(input_df)[0]
        
        return prediction
    
    def save_model(self, filepath: str = None):
        """
        Save trained model to disk
        
        Args:
            filepath: Path to save model (default from config)
        """
        if filepath is None:
            filepath = self.config['models']['yield_predictor']
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        joblib.dump(self.model, filepath)
        print(f"💾 Model saved to {filepath}")
    
    def load_model(self, filepath: str = None):
        """
        Load trained model from disk
        
        Args:
            filepath: Path to load model from (default from config)
        """
        if filepath is None:
            filepath = self.config['models']['yield_predictor']
        
        self.model = joblib.load(filepath)
        print(f"✅ Model loaded from {filepath}")
    
    def get_feature_importance(self) -> pd.DataFrame:
        """
        Get feature importance from trained model
        
        Returns:
            DataFrame with feature names and importance scores
        """
        if self.model is None:
            raise ValueError("Model not trained!")
        
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df


def main():
    """Example usage of YieldPredictor"""
    
    # Initialize predictor
    predictor = YieldPredictor()
    
    # Example input
    sample_input = {
        'nitrogen': 90,
        'phosphorus': 42,
        'potassium': 43,
        'rainfall': 202.9,
        'temperature': 26.8,
        'ph': 6.5
    }
    
    print("\n📋 Sample Input:")
    for key, value in sample_input.items():
        print(f"   {key}: {value}")
    
    print("\n⚠️ Note: Train the model first with actual data!")
    print("   Example: predictor.train(your_dataframe)")


if __name__ == "__main__":
    main()
