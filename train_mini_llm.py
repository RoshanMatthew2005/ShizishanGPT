"""
Train a Mini LLM on Agricultural Data

This script fine-tunes DistilGPT-2 on agricultural corpus and Q&A pairs.

Training approach:
1. Load DistilGPT-2 model and tokenizer
2. Prepare training data from agri_corpus.txt and qa_pairs.jsonl
3. Fine-tune using HuggingFace Trainer
4. Save model to models/mini_llm/
"""

import json
import os
from pathlib import Path
from typing import List, Dict
import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from tqdm import tqdm


# Configuration
CORPUS_FILE = Path("mini_llm/data/agri_corpus.txt")
QA_FILE = Path("mini_llm/data/qa_pairs.jsonl")
OUTPUT_DIR = Path("models/mini_llm")
CHECKPOINT_DIR = Path("models/mini_llm_checkpoints")

# Model configuration
MODEL_NAME = "distilgpt2"  # Smaller, faster GPT-2 variant
MAX_LENGTH = 256  # Maximum sequence length
BATCH_SIZE = 8  # Increased batch size for GPU
LEARNING_RATE = 5e-5
NUM_EPOCHS = 3
WARMUP_STEPS = 100
GRADIENT_ACCUMULATION_STEPS = 2  # Reduced for GPU
SAVE_STEPS = 500
LOGGING_STEPS = 50


class AgriCorpusDataset(Dataset):
    """Dataset for agricultural corpus text."""
    
    def __init__(self, corpus_file: Path, tokenizer, max_length: int = MAX_LENGTH):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []
        
        print(f"📖 Loading corpus from {corpus_file}...")
        
        with open(corpus_file, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        print(f"📝 Processing {len(paragraphs)} paragraphs...")
        
        # Tokenize and create training examples
        for paragraph in tqdm(paragraphs, desc="Tokenizing corpus"):
            # Add special tokens to mark beginning and end
            formatted_text = f"{tokenizer.bos_token}{paragraph}{tokenizer.eos_token}"
            
            # Tokenize
            encodings = tokenizer(
                formatted_text,
                truncation=True,
                max_length=max_length,
                padding=False,
                return_tensors=None
            )
            
            # Only keep examples with sufficient length
            if len(encodings['input_ids']) > 20:
                self.examples.append(encodings['input_ids'])
        
        print(f"✓ Created {len(self.examples)} training examples from corpus")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return {'input_ids': torch.tensor(self.examples[idx], dtype=torch.long)}


class AgriQADataset(Dataset):
    """Dataset for Q&A pairs."""
    
    def __init__(self, qa_file: Path, tokenizer, max_length: int = MAX_LENGTH):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.examples = []
        
        if not qa_file.exists():
            print(f"⚠️  Q&A file not found: {qa_file}")
            return
        
        print(f"📖 Loading Q&A pairs from {qa_file}...")
        
        qa_pairs = []
        with open(qa_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    qa_pairs.append(json.loads(line))
        
        print(f"📝 Processing {len(qa_pairs)} Q&A pairs...")
        
        # Format Q&A pairs for training
        for qa in tqdm(qa_pairs, desc="Tokenizing Q&A pairs"):
            question = qa.get('question', '').strip()
            answer = qa.get('answer', '').strip()
            
            if not question or not answer:
                continue
            
            # Format: Q: <question>\nA: <answer>
            formatted_text = f"{tokenizer.bos_token}Q: {question}\nA: {answer}{tokenizer.eos_token}"
            
            # Tokenize
            encodings = tokenizer(
                formatted_text,
                truncation=True,
                max_length=max_length,
                padding=False,
                return_tensors=None
            )
            
            if len(encodings['input_ids']) > 10:
                self.examples.append(encodings['input_ids'])
        
        print(f"✓ Created {len(self.examples)} training examples from Q&A pairs")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return {'input_ids': torch.tensor(self.examples[idx], dtype=torch.long)}


class CombinedDataset(Dataset):
    """Combined dataset from corpus and Q&A pairs."""
    
    def __init__(self, corpus_dataset: Dataset, qa_dataset: Dataset):
        self.examples = []
        
        # Add all corpus examples
        for i in range(len(corpus_dataset)):
            self.examples.append(corpus_dataset[i])
        
        # Add all Q&A examples
        for i in range(len(qa_dataset)):
            self.examples.append(qa_dataset[i])
        
        print(f"\n✓ Combined dataset: {len(self.examples)} total examples")
        print(f"   - Corpus examples: {len(corpus_dataset)}")
        print(f"   - Q&A examples: {len(qa_dataset)}")
    
    def __len__(self):
        return len(self.examples)
    
    def __getitem__(self, idx):
        return self.examples[idx]


def prepare_datasets(tokenizer):
    """Prepare training datasets."""
    print("\n" + "=" * 70)
    print("PREPARING DATASETS")
    print("=" * 70)
    
    # Load corpus dataset
    corpus_dataset = AgriCorpusDataset(CORPUS_FILE, tokenizer, MAX_LENGTH)
    
    # Load Q&A dataset
    qa_dataset = AgriQADataset(QA_FILE, tokenizer, MAX_LENGTH)
    
    # Combine datasets
    combined_dataset = CombinedDataset(corpus_dataset, qa_dataset)
    
    return combined_dataset


def train_model():
    """Main training function."""
    print("=" * 70)
    print("MINI LLM TRAINING - AGRICULTURAL DATA")
    print("=" * 70)
    print(f"\nModel: {MODEL_NAME}")
    print(f"Max Length: {MAX_LENGTH}")
    print(f"Batch Size: {BATCH_SIZE}")
    print(f"Learning Rate: {LEARNING_RATE}")
    print(f"Epochs: {NUM_EPOCHS}")
    print(f"Device: {'CUDA' if torch.cuda.is_available() else 'CPU'}")
    
    # Load tokenizer
    print(f"\n📥 Loading tokenizer: {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # Set pad token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    print("✓ Tokenizer loaded")
    
    # Load model
    print(f"\n📥 Loading model: {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    print("✓ Model loaded")
    print(f"   Parameters: {model.num_parameters():,}")
    
    # Prepare datasets
    train_dataset = prepare_datasets(tokenizer)
    
    # Data collator for language modeling
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # We're doing causal language modeling, not masked LM
    )
    
    # Training arguments
    print("\n" + "=" * 70)
    print("CONFIGURING TRAINING")
    print("=" * 70)
    
    training_args = TrainingArguments(
        output_dir=str(CHECKPOINT_DIR),
        overwrite_output_dir=True,
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        learning_rate=LEARNING_RATE,
        warmup_steps=WARMUP_STEPS,
        logging_steps=LOGGING_STEPS,
        save_steps=SAVE_STEPS,
        save_total_limit=2,  # Keep only 2 checkpoints
        prediction_loss_only=True,
        report_to="none",  # Disable wandb/tensorboard
        logging_dir=str(CHECKPOINT_DIR / "logs"),
        fp16=torch.cuda.is_available(),  # Enable mixed precision for GPU
    )
    
    print(f"✓ Training configuration set")
    print(f"   Total training steps: {len(train_dataset) * NUM_EPOCHS // (BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS)}")
    
    # Initialize trainer
    print("\n" + "=" * 70)
    print("STARTING TRAINING")
    print("=" * 70)
    
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )
    
    # Train
    print("\n🚀 Training started...\n")
    trainer.train()
    
    # Save final model
    print("\n" + "=" * 70)
    print("SAVING MODEL")
    print("=" * 70)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"💾 Saving model to {OUTPUT_DIR}...")
    model.save_pretrained(str(OUTPUT_DIR))
    tokenizer.save_pretrained(str(OUTPUT_DIR))
    
    print("✓ Model saved successfully")
    
    # Display final statistics
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE")
    print("=" * 70)
    print(f"📁 Model location: {OUTPUT_DIR.resolve()}")
    print(f"📊 Files saved:")
    for file in OUTPUT_DIR.iterdir():
        print(f"   - {file.name}")
    print("=" * 70)
    
    print("\n✅ Training completed successfully!")
    print(f"\nTo use the model, run: python mini_llm/inference.py")


if __name__ == "__main__":
    # Check if required files exist
    if not CORPUS_FILE.exists():
        print(f"❌ Error: Corpus file not found: {CORPUS_FILE}")
        print(f"   Please run: python mini_llm/extract_and_clean_pdfs.py")
        exit(1)
    
    if not QA_FILE.exists():
        print(f"⚠️  Warning: Q&A file not found: {QA_FILE}")
        print(f"   Run: python mini_llm/generate_qa_pairs.py (recommended but optional)")
        print(f"   Continuing with corpus data only...\n")
    
    train_model()
