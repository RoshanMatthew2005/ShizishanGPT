"""
Data loading utilities for CSV, PDF, and image files
"""

import pandas as pd
import os
from pathlib import Path
from typing import Union, List
import yaml


class DataLoader:
    """Load and manage various data formats for ShizishanGPT"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize DataLoader with configuration
        
        Args:
            config_path: Path to config.yaml file
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.data_paths = self.config['data']
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """
        Load CSV file from data/raw/csvs/
        
        Args:
            filename: Name of CSV file
            
        Returns:
            DataFrame containing the data
        """
        csv_path = os.path.join(self.data_paths['csvs'], filename)
        return pd.read_csv(csv_path)
    
    def load_all_csvs(self) -> dict:
        """
        Load all CSV files from data/raw/csvs/
        
        Returns:
            Dictionary with filename as key and DataFrame as value
        """
        csv_dir = self.data_paths['csvs']
        csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
        
        data = {}
        for csv_file in csv_files:
            data[csv_file] = self.load_csv(csv_file)
        
        return data
    
    def save_processed_data(self, df: pd.DataFrame, filename: str):
        """
        Save processed data to data/processed/
        
        Args:
            df: DataFrame to save
            filename: Name for the saved file
        """
        processed_path = os.path.join(self.data_paths['processed'], filename)
        df.to_csv(processed_path, index=False)
        print(f"✅ Saved processed data to {processed_path}")


if __name__ == "__main__":
    # Example usage
    loader = DataLoader()
    print("DataLoader initialized successfully!")
