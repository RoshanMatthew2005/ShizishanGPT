#!/usr/bin/env python3
"""Test pest model loading"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from backend.models.load_pest_model import load_pest_model
from backend.config import settings

def test_pest_model():
    try:
        print("Testing pest model loading...")
        
        pest_model = load_pest_model(settings.PEST_MODEL_PATH, settings.PEST_CLASSES_PATH)
        
        if pest_model and pest_model.loaded:
            print(f"✅ Pest model loaded successfully")
            print(f"✅ Number of classes: {len(pest_model.class_names)}")
            print(f"✅ Classes: {pest_model.class_names[:3]}...")
            print(f"✅ Device: {pest_model.device}")
            return True
        else:
            print("❌ Pest model failed to load")
            return False
            
    except Exception as e:
        print(f"❌ Error loading pest model: {e}")
        return False

if __name__ == "__main__":
    success = test_pest_model()
    print(f"\n{'✅ Test passed' if success else '❌ Test failed'}")