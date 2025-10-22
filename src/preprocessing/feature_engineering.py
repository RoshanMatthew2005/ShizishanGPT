"""
Feature engineering utilities for agricultural data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from typing import List, Tuple


class FeatureEngineer:
    """Feature engineering for agricultural datasets"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def engineer_yield_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create additional features for yield prediction
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        df = df.copy()
        
        # NPK ratio
        if all(col in df.columns for col in ['nitrogen', 'phosphorus', 'potassium']):
            df['npk_sum'] = df['nitrogen'] + df['phosphorus'] + df['potassium']
            df['npk_ratio'] = df['nitrogen'] / (df['phosphorus'] + df['potassium'] + 1)
        
        # Temperature-rainfall interaction
        if 'temperature' in df.columns and 'rainfall' in df.columns:
            df['temp_rain_interaction'] = df['temperature'] * df['rainfall']
        
        # pH category
        if 'ph' in df.columns:
            df['ph_category'] = pd.cut(df['ph'], 
                                       bins=[0, 5.5, 7.5, 14], 
                                       labels=['acidic', 'neutral', 'alkaline'])
        
        return df
    
    def scale_features(self, X_train: pd.DataFrame, X_test: pd.DataFrame = None) -> Tuple:
        """
        Scale numerical features
        
        Args:
            X_train: Training features
            X_test: Test features (optional)
            
        Returns:
            Scaled train and test sets
        """
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        if X_test is not None:
            X_test_scaled = self.scaler.transform(X_test)
            return X_train_scaled, X_test_scaled
        
        return X_train_scaled
    
    def encode_categorical(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Encode categorical variables
        
        Args:
            df: Input DataFrame
            columns: List of categorical columns
            
        Returns:
            DataFrame with encoded columns
        """
        df = df.copy()
        
        for col in columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
                df[col] = self.label_encoders[col].fit_transform(df[col])
            else:
                df[col] = self.label_encoders[col].transform(df[col])
        
        return df


if __name__ == "__main__":
    # Example usage
    engineer = FeatureEngineer()
    print("FeatureEngineer initialized successfully!")
