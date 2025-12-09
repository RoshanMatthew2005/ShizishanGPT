"""
LLM Engine
Wrapper for text generation - uses Gemma 2 (via Ollama) by default, Mini LLM as fallback.
"""
import torch
import os
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from transformers import GPT2LMHeadModel, GPT2Tokenizer


class LLMEngine:
    """LLM engine for agricultural text generation."""
    
    def __init__(self, model_path: str = "models/mini_llm"):
        """
        Initialize the LLM Engine.
        
        Args:
            model_path: Path to the fine-tuned model directory (fallback only)
        """
        self.name = "llm_generation"
        self.description = "Generates agricultural text using Gemma 2 or fine-tuned language model"
        
        # Gemma 2 configuration (priority)
        self.use_gemma = os.getenv("USE_GEMMA_FALLBACK", "true").lower() == "true"
        self.gemma_model = os.getenv("GEMMA_MODEL", "gemma2:2b")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        # Mini LLM configuration (fallback)
        self.model_path = Path(model_path)
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_loaded = False
        
        # Generation parameters
        self.default_params = {
            'max_length': 512,
            'temperature': 0.9,
            'top_k': 50,
            'top_p': 0.9,
            'repetition_penalty': 1.5,
            'no_repeat_ngram_size': 4,
            'do_sample': True,
            'early_stopping': True,
            'num_return_sequences': 1
        }
        
        # Gemma 2 parameters
        self.gemma_params = {
            'temperature': 0.7,
            'top_p': 0.9,
            'max_tokens': 1024
        }
        
    def load(self) -> bool:
        """Load the fine-tuned model and tokenizer."""
        try:
            if not self.model_path.exists():
                print(f"❌ Model not found: {self.model_path}")
                print(f"❌ Please train the model using: python train_mini_llm.py")
                return False
            
            # Load tokenizer
            print(f"Loading tokenizer from {self.model_path}...")
            self.tokenizer = GPT2Tokenizer.from_pretrained(str(self.model_path))
            
            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Load model
            print(f"Loading model from {self.model_path}...")
            self.model = GPT2LMHeadModel.from_pretrained(str(self.model_path))
            self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            print(f"✓ Mini LLM Engine loaded (fallback)")
            print(f"✓ Device: {self.device}")
            print(f"✓ Model parameters: {sum(p.numel() for p in self.model.parameters()) / 1e6:.1f}M")
            return True
            
        except Exception as e:
            print(f"❌ Error loading LLM engine: {e}")
            return False
    
    def _generate_with_gemma(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Generate text using Gemma 2 via Ollama.
        
        Args:
            prompt: Input prompt
            **kwargs: Generation parameters
            
        Returns:
            Dictionary with generated text
        """
        try:
            # Prepare parameters
            params = self.gemma_params.copy()
            params.update(kwargs)
            
            # Make request to Ollama
            payload = {
                "model": self.gemma_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": params.get('temperature', 0.7),
                    "top_p": params.get('top_p', 0.9),
                    "num_predict": params.get('max_tokens', 200)
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '').strip()
                
                return {
                    "success": True,
                    "tool": self.name,
                    "prompt": prompt,
                    "generated_text": generated_text,
                    "full_text": prompt + " " + generated_text,
                    "model": "gemma2",
                    "generation_params": params
                }
            else:
                return {
                    "success": False,
                    "error": f"Ollama request failed: {response.status_code}",
                    "tool": self.name
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Gemma 2 generation failed: {str(e)}",
                "tool": self.name
            }
    
    def generate(self, 
                 prompt: str,
                 max_length: Optional[int] = None,
                 temperature: Optional[float] = None,
                 **kwargs) -> Dict[str, Any]:
        """
        Generate text from a prompt.
        
        Args:
            prompt: The input prompt
            max_length: Maximum length of generated text (default: 150)
            temperature: Sampling temperature (default: 0.9)
            **kwargs: Additional generation parameters
        
        Returns:
            Dictionary with generated text
        """
        try:
            # Try Gemma 2 first if enabled
            if self.use_gemma:
                gemma_result = self._generate_with_gemma(prompt, **kwargs)
                if gemma_result["success"]:
                    return gemma_result
                else:
                    print(f"⚠️ Gemma 2 failed, falling back to Mini LLM: {gemma_result.get('error')}")
            
            # Fallback to Mini LLM
            if not self.is_loaded:
                if not self.load():
                    return {
                        "success": False,
                        "error": "Both Gemma 2 and Mini LLM unavailable",
                        "tool": self.name
                    }
            
            if not prompt or not prompt.strip():
                return {
                    "success": False,
                    "error": "Prompt cannot be empty",
                    "tool": self.name
                }
            
            # Prepare generation parameters
            gen_params = self.default_params.copy()
            if max_length:
                gen_params['max_length'] = max_length
            if temperature:
                gen_params['temperature'] = temperature
            gen_params.update(kwargs)
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors='pt').to(self.device)
            
            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    pad_token_id=self.tokenizer.eos_token_id,
                    **gen_params
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the generated part (remove prompt)
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            # Truncate to first few sentences to avoid long repetitive outputs
            sentences = generated_text.split('.')
            if len(sentences) > 3:
                generated_text = '. '.join(sentences[:3]) + '.'
            
            return {
                "success": True,
                "tool": self.name,
                "prompt": prompt,
                "generated_text": generated_text,
                "full_text": prompt + " " + generated_text,
                "generation_params": {
                    "temperature": gen_params['temperature'],
                    "max_length": gen_params['max_length'],
                    "repetition_penalty": gen_params['repetition_penalty']
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Text generation failed: {str(e)}",
                "tool": self.name
            }
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Answer a question using the LLM.
        
        Args:
            question: The question to answer
        
        Returns:
            Dictionary with answer
        """
        # Format as Q&A (the format used during training)
        prompt = f"Q: {question}\nA:"
        
        result = self.generate(
            prompt,
            max_length=512,
            temperature=0.8,
            repetition_penalty=2.0  # Higher penalty for Q&A
        )
        
        if result['success']:
            # Extract just the answer part
            answer = result['generated_text']
            result['answer'] = answer
            result['question'] = question
        
        return result
    
    def continue_text(self, partial_text: str) -> Dict[str, Any]:
        """
        Continue a partial text.
        
        Args:
            partial_text: The text to continue
        
        Returns:
            Dictionary with continuation
        """
        return self.generate(partial_text, max_length=200)
    
    def __call__(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Allow the engine to be called directly."""
        return self.generate(prompt, **kwargs)


# Example usage
if __name__ == "__main__":
    engine = LLMEngine()
    
    # Test 1: Question answering
    question = "What are the best practices for rice cultivation?"
    result1 = engine.answer_question(question)
    
    print("\n" + "="*70)
    print("LLM ENGINE TEST - Q&A")
    print("="*70)
    print(f"Question: {question}")
    print(f"Success: {result1['success']}")
    if result1['success']:
        print(f"Answer: {result1.get('answer', 'N/A')}")
    else:
        print(f"Error: {result1['error']}")
    print("="*70)
    
    # Test 2: Text generation
    prompt = "Nitrogen fertilizer is essential for"
    result2 = engine.generate(prompt)
    
    print("\n" + "="*70)
    print("LLM ENGINE TEST - Generation")
    print("="*70)
    print(f"Prompt: {prompt}")
    print(f"Success: {result2['success']}")
    if result2['success']:
        print(f"Generated: {result2['generated_text']}")
        print(f"Temperature: {result2['generation_params']['temperature']}")
    print("="*70)
