"""
Mini LLM Loader
Loads and manages the fine-tuned Mini LLM (DistilGPT-2)
"""

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MiniLLM:
    """
    Wrapper for the fine-tuned Mini LLM
    """
    
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model = None
        self.tokenizer = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.loaded = False
        
        # Generation parameters
        self.max_length = 150
        self.temperature = 0.9
        self.repetition_penalty = 1.5
        self.no_repeat_ngram_size = 4
        self.num_beams = 3
    
    def load(self):
        """Load the Mini LLM model"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model directory not found: {self.model_path}")
            
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_path))
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(str(self.model_path))
            self.model.to(self.device)
            self.model.eval()
            
            self.loaded = True
            
            # Get model parameters
            num_params = sum(p.numel() for p in self.model.parameters())
            logger.info(f"✓ Mini LLM loaded from {self.model_path}")
            logger.info(f"✓ Model parameters: {num_params:,}")
            logger.info(f"✓ Device: {self.device}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Mini LLM: {e}")
            self.loaded = False
            return False
    
    def generate(self, prompt: str, max_length: int = None, temperature: float = None) -> str:
        """
        Generate text from prompt
        
        Args:
            prompt: Input prompt
            max_length: Maximum generation length
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load() first.")
        
        try:
            # Use default parameters if not specified
            max_len = max_length or self.max_length
            temp = temperature or self.temperature
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    max_length=max_len,
                    temperature=temp,
                    repetition_penalty=self.repetition_penalty,
                    no_repeat_ngram_size=self.no_repeat_ngram_size,
                    num_beams=self.num_beams,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new generated text (remove prompt)
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            # Truncate to first few sentences to avoid repetition
            generated_text = self._truncate_to_sentences(generated_text, max_sentences=3)
            
            logger.info(f"Generated {len(generated_text)} characters")
            return generated_text
            
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise
    
    def answer_question(self, question: str, context: str = "") -> str:
        """
        Answer a question, optionally with context
        
        Args:
            question: The question to answer
            context: Optional context for answering
        
        Returns:
            Generated answer
        """
        if context:
            prompt = f"Context: {context[:500]}\n\nQuestion: {question}\n\nAnswer:"
        else:
            prompt = f"Question: {question}\n\nAnswer:"
        
        return self.generate(prompt)
    
    def _truncate_to_sentences(self, text: str, max_sentences: int = 3) -> str:
        """
        Truncate text to first N sentences
        """
        import re
        
        # Split by sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Take first N sentences
        truncated = ' '.join(sentences[:max_sentences])
        
        # Ensure it ends with punctuation
        if truncated and truncated[-1] not in '.!?':
            truncated += '.'
        
        return truncated


def load_mini_llm(model_path: str) -> MiniLLM:
    """
    Factory function to load Mini LLM
    """
    model = MiniLLM(model_path)
    model.load()
    return model
