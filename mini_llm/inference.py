"""
Inference script for the fine-tuned Mini LLM.

This script:
1. Loads the fine-tuned model from models/mini_llm/
2. Accepts text prompts
3. Generates responses using the model
"""

import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
import warnings
warnings.filterwarnings('ignore')


# Configuration
MODEL_DIR = Path("models/mini_llm")
MAX_LENGTH = 150  # Reduced to prevent long repetitions
TEMPERATURE = 0.9
TOP_K = 50
TOP_P = 0.9
NUM_RETURN_SEQUENCES = 1
REPETITION_PENALTY = 1.5  # Stronger penalty
NO_REPEAT_NGRAM_SIZE = 4  # Prevent longer phrase repetition


class AgriLLM:
    """Agricultural Mini LLM for text generation."""
    
    def __init__(self, model_dir: Path = MODEL_DIR):
        """Initialize the model and tokenizer."""
        self.model_dir = model_dir
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        print("=" * 70)
        print("LOADING AGRICULTURAL MINI LLM")
        print("=" * 70)
        print(f"📁 Model directory: {model_dir.resolve()}")
        print(f"💻 Device: {self.device}")
        
        # Load tokenizer
        print("\n📥 Loading tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
        
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        print("✓ Tokenizer loaded")
        
        # Load model
        print("\n📥 Loading model...")
        self.model = AutoModelForCausalLM.from_pretrained(str(model_dir))
        self.model.to(self.device)
        self.model.eval()
        
        print("✓ Model loaded")
        print(f"   Parameters: {self.model.num_parameters():,}")
        print("=" * 70)
    
    def generate(
        self,
        prompt: str,
        max_length: int = MAX_LENGTH,
        temperature: float = TEMPERATURE,
        top_k: int = TOP_K,
        top_p: float = TOP_P,
        num_return_sequences: int = NUM_RETURN_SEQUENCES,
        repetition_penalty: float = REPETITION_PENALTY,
        no_repeat_ngram_size: int = NO_REPEAT_NGRAM_SIZE,
    ) -> str:
        """
        Generate text based on the prompt.
        
        Args:
            prompt: Input text prompt
            max_length: Maximum length of generated text
            temperature: Sampling temperature (higher = more random)
            top_k: Top-k sampling parameter
            top_p: Top-p (nucleus) sampling parameter
            num_return_sequences: Number of sequences to generate
            repetition_penalty: Penalty for repeating tokens (>1.0 reduces repetition)
            no_repeat_ngram_size: Size of n-grams that cannot be repeated
        
        Returns:
            Generated text
        """
        # Encode the prompt
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length // 2  # Leave room for generation
        )
        
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p,
                num_return_sequences=num_return_sequences,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=repetition_penalty,
                no_repeat_ngram_size=no_repeat_ngram_size,
                early_stopping=True,
            )
        
        # Decode the generated text
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        return generated_text
    
    def answer_question(self, question: str) -> str:
        """
        Answer a question using the Q&A format.
        
        Args:
            question: The question to answer
        
        Returns:
            Generated answer
        """
        # Format the prompt as Q&A
        prompt = f"Q: {question}\nA:"
        
        # Generate the response with stricter controls
        full_response = self.generate(
            prompt, 
            max_length=200,
            repetition_penalty=2.0,  # Very strong penalty for Q&A
            no_repeat_ngram_size=4,
        )
        
        # Extract just the answer part
        if "\nA:" in full_response:
            answer = full_response.split("\nA:", 1)[1].strip()
            # Stop at the next question if present
            if "\nQ:" in answer:
                answer = answer.split("\nQ:", 1)[0].strip()
            # Stop at first period followed by newline or if too long
            sentences = answer.split('. ')
            if len(sentences) > 3:
                answer = '. '.join(sentences[:3]) + '.'
        else:
            answer = full_response.replace(prompt, "").strip()
            # Limit to first few sentences
            sentences = answer.split('. ')
            if len(sentences) > 3:
                answer = '. '.join(sentences[:3]) + '.'
        
        return answer
    
    def continue_text(self, text: str) -> str:
        """
        Continue/complete the given text.
        
        Args:
            text: Text to continue
        
        Returns:
            Completed text
        """
        return self.generate(text, max_length=350)


def interactive_mode():
    """Run interactive Q&A mode."""
    # Load model
    try:
        llm = AgriLLM()
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        print(f"\nMake sure you've trained the model first:")
        print(f"   python train_mini_llm.py")
        return
    
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE")
    print("=" * 70)
    print("\nWelcome to the Agricultural Mini LLM!")
    print("\nYou can:")
    print("  1. Ask questions (e.g., 'How to grow maize?')")
    print("  2. Start a sentence to complete (e.g., 'Maize cultivation requires')")
    print("\nType 'quit' or 'exit' to stop.")
    print("Type 'examples' to see sample questions.")
    print("=" * 70)
    
    while True:
        print("\n")
        user_input = input("🌾 You: ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if user_input.lower() == 'examples':
            print("\n📝 Example questions:")
            print("  - How to grow maize?")
            print("  - What fertilizer should be used for tomatoes?")
            print("  - How to control pests in potato?")
            print("  - What are the requirements for wheat cultivation?")
            print("  - When should irrigation be applied?")
            continue
        
        # Determine if it's a question or text to complete
        is_question = user_input.endswith('?') or user_input.lower().startswith(('what', 'how', 'when', 'where', 'why', 'which', 'who'))
        
        print("\n🤖 AgriLLM: ", end="", flush=True)
        
        try:
            if is_question:
                response = llm.answer_question(user_input)
            else:
                response = llm.continue_text(user_input)
            
            print(response)
        
        except Exception as e:
            print(f"\n❌ Error generating response: {e}")


def batch_test():
    """Test the model with predefined questions."""
    # Load model
    try:
        llm = AgriLLM()
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        return
    
    print("\n" + "=" * 70)
    print("BATCH TEST MODE")
    print("=" * 70)
    
    test_questions = [
        "How to grow maize?",
        "What fertilizer should be used for tomatoes?",
        "How to control pests?",
        "What are the requirements for wheat cultivation?",
        "When should irrigation be applied?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*70}")
        print(f"Question {i}: {question}")
        print(f"{'='*70}")
        
        try:
            answer = llm.answer_question(question)
            print(f"Answer: {answer}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("BATCH TEST COMPLETE")
    print("=" * 70)


def single_generation(prompt: str):
    """Generate text for a single prompt."""
    try:
        llm = AgriLLM()
    except Exception as e:
        print(f"\n❌ Error loading model: {e}")
        return
    
    print("\n" + "=" * 70)
    print(f"PROMPT: {prompt}")
    print("=" * 70)
    
    try:
        if prompt.endswith('?') or prompt.lower().startswith(('what', 'how', 'when', 'where', 'why')):
            response = llm.answer_question(prompt)
        else:
            response = llm.continue_text(prompt)
        
        print(f"\nGENERATED TEXT:\n{response}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)


def main():
    """Main function."""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "    🌾  AGRICULTURAL MINI LLM - INFERENCE  🌾    ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Check if model exists
    if not MODEL_DIR.exists():
        print(f"\n❌ Error: Model not found at {MODEL_DIR.resolve()}")
        print(f"\nPlease train the model first:")
        print(f"   1. python mini_llm/extract_and_clean_pdfs.py")
        print(f"   2. python mini_llm/generate_qa_pairs.py")
        print(f"   3. python train_mini_llm.py")
        return
    
    print("\nSelect mode:")
    print("  1. Interactive Mode (ask questions)")
    print("  2. Batch Test Mode (run predefined questions)")
    print("  3. Single Prompt")
    print()
    
    try:
        choice = input("Your choice (1-3): ").strip()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        return
    
    if choice == "1":
        interactive_mode()
    elif choice == "2":
        batch_test()
    elif choice == "3":
        prompt = input("\nEnter your prompt: ").strip()
        if prompt:
            single_generation(prompt)
    else:
        print("Invalid choice. Please run again and select 1, 2, or 3.")


if __name__ == "__main__":
    main()
