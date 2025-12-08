"""
Master script to execute all Mini LLM pipeline steps.

This script runs:
1. PDF extraction and cleaning
2. Q&A pairs generation
3. Model training
4. (Optional) Test inference

Usage:
    python run_mini_llm_pipeline.py [--skip-training] [--test-inference]
"""

import sys
import subprocess
from pathlib import Path
import argparse


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(title.upper().center(70))
    print("=" * 70 + "\n")


def run_step(script_path: str, description: str) -> bool:
    """
    Run a Python script and return success status.
    
    Args:
        script_path: Path to the Python script
        description: Description of the step
    
    Returns:
        True if successful, False otherwise
    """
    print_section(description)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=False
        )
        print(f"\n✅ {description} - COMPLETED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ {description} - ERROR")
        print(f"Error: {e}")
        return False


def check_prerequisites():
    """Check if required directories and files exist."""
    print_section("Checking Prerequisites")
    
    pdf_dir = Path("data/pdfs")
    
    if not pdf_dir.exists():
        print(f"❌ PDF directory not found: {pdf_dir}")
        print("Please create the directory and add PDF files.")
        return False
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"❌ No PDF files found in {pdf_dir}")
        print("Please add PDF files to the directory.")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files in {pdf_dir}")
    return True


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description="Run Mini LLM pipeline")
    parser.add_argument("--skip-training", action="store_true", help="Skip model training step")
    parser.add_argument("--test-inference", action="store_true", help="Run inference test after training")
    args = parser.parse_args()
    
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "    🌾  MINI LLM PIPELINE - COMPLETE EXECUTION  🌾    ".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed. Exiting.")
        return 1
    
    # Step 1: Extract and clean PDFs
    success = run_step(
        "mini_llm/extract_and_clean_pdfs.py",
        "Step 1: Extract and Clean PDFs"
    )
    
    if not success:
        print("\n❌ Pipeline failed at Step 1")
        return 1
    
    # Step 2: Generate Q&A pairs
    success = run_step(
        "mini_llm/generate_qa_pairs.py",
        "Step 2: Generate Q&A Pairs"
    )
    
    if not success:
        print("\n⚠️  Warning: Q&A generation failed, but continuing...")
        print("   Training will use corpus data only.")
    
    # Step 3: Train model (unless skipped)
    if not args.skip_training:
        success = run_step(
            "train_mini_llm.py",
            "Step 3: Train Mini LLM"
        )
        
        if not success:
            print("\n❌ Pipeline failed at Step 3")
            return 1
    else:
        print_section("Step 3: Train Mini LLM - SKIPPED")
    
    # Step 4: Test inference (if requested)
    if args.test_inference and not args.skip_training:
        print_section("Step 4: Test Inference")
        print("\nLaunching inference script...")
        print("Note: The inference script will open in interactive mode.")
        print("      Press Ctrl+C to exit when done.\n")
        
        try:
            subprocess.run([sys.executable, "mini_llm/inference.py"])
        except KeyboardInterrupt:
            print("\n\nInference test interrupted by user.")
    
    # Final summary
    print_section("Pipeline Complete")
    print("✅ All steps completed successfully!\n")
    print("📁 Generated files:")
    print("   - mini_llm/data/agri_corpus.txt")
    print("   - mini_llm/data/qa_pairs.jsonl")
    
    if not args.skip_training:
        print("   - models/mini_llm/ (trained model)")
    
    print("\n🚀 Next steps:")
    if args.skip_training:
        print("   - Run: python train_mini_llm.py (to train the model)")
    else:
        print("   - Run: python mini_llm/inference.py (to test the model)")
    
    print("\n" + "=" * 70)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
