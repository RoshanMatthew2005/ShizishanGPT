"""
Extract and clean text from agricultural PDFs to create training corpus.

This script:
1. Reads all PDFs from data/pdfs/
2. Cleans the extracted text (removes headers, footers, special chars, etc.)
3. Saves cleaned text to mini_llm/data/agri_corpus.txt
"""

import re
import os
from pathlib import Path
from typing import List, Set
from PyPDF2 import PdfReader
from tqdm import tqdm


# Configuration
PDF_DIR = Path("data/pdfs")
OUTPUT_FILE = Path("mini_llm/data/agri_corpus.txt")
MIN_LINE_WORDS = 5  # Minimum words per line to keep
MIN_PARAGRAPH_LENGTH = 50  # Minimum characters for a paragraph


def is_header_footer(line: str) -> bool:
    """Detect if a line is likely a header or footer."""
    line_lower = line.lower().strip()
    
    # Common header/footer patterns
    header_footer_patterns = [
        r'^\d+$',  # Just page numbers
        r'^page \d+',  # "Page 1", "Page 2"
        r'^\d+ of \d+$',  # "1 of 10"
        r'chapter \d+',  # Chapter headers
        r'copyright',
        r'all rights reserved',
        r'^\d{4}$',  # Just year
        r'^[ivxlcdm]+$',  # Roman numerals only
    ]
    
    for pattern in header_footer_patterns:
        if re.search(pattern, line_lower):
            return True
    
    # Very short lines at start/end are often headers/footers
    if len(line.strip()) < 3:
        return True
        
    return False


def is_table_or_figure(line: str) -> bool:
    """Detect if a line is part of a table or figure caption."""
    line_lower = line.lower().strip()
    
    table_figure_patterns = [
        r'^table \d+',
        r'^fig\.?\s*\d+',
        r'^figure \d+',
        r'^chart \d+',
        r'^graph \d+',
        r'^\|.*\|',  # Table borders
        r'^[-=+]{3,}$',  # Horizontal lines in tables
    ]
    
    for pattern in table_figure_patterns:
        if re.search(pattern, line_lower):
            return True
    
    return False


def is_reference(line: str) -> bool:
    """Detect if a line is from a reference/bibliography section."""
    line_lower = line.lower().strip()
    
    reference_patterns = [
        r'^references?$',
        r'^bibliography$',
        r'^\[\d+\]',  # [1], [2], etc.
        r'^\d+\.\s+[A-Z]',  # 1. Author Name
        r'et al\.',
        r'\(\d{4}\)',  # Publication year
    ]
    
    for pattern in reference_patterns:
        if re.search(pattern, line_lower):
            return True
    
    return False


def clean_text(text: str) -> str:
    """Clean extracted text by removing unwanted elements."""
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
            
        # Skip headers, footers, tables, figures, references
        if is_header_footer(line) or is_table_or_figure(line) or is_reference(line):
            continue
        
        # Skip very short lines (likely fragments)
        words = line.strip().split()
        if len(words) < MIN_LINE_WORDS:
            continue
        
        # Clean the line
        cleaned = line.strip()
        
        # Remove special characters but keep basic punctuation
        cleaned = re.sub(r'[^\w\s.,;:!?()\-\'\"°%]', ' ', cleaned)
        
        # Collapse multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Remove standalone numbers that might be page numbers
        if re.match(r'^\d+$', cleaned.strip()):
            continue
        
        if cleaned:
            cleaned_lines.append(cleaned)
    
    return '\n'.join(cleaned_lines)


def merge_into_paragraphs(text: str) -> str:
    """Merge broken lines into full paragraphs."""
    lines = text.split('\n')
    paragraphs = []
    current_paragraph = []
    
    for line in lines:
        line = line.strip()
        
        if not line:
            # Empty line indicates paragraph break
            if current_paragraph:
                para = ' '.join(current_paragraph)
                if len(para) >= MIN_PARAGRAPH_LENGTH:
                    paragraphs.append(para)
                current_paragraph = []
        else:
            # Check if this line ends a sentence
            if line[-1] in '.!?':
                current_paragraph.append(line)
                # End paragraph here
                para = ' '.join(current_paragraph)
                if len(para) >= MIN_PARAGRAPH_LENGTH:
                    paragraphs.append(para)
                current_paragraph = []
            else:
                # Continue building paragraph
                current_paragraph.append(line)
    
    # Add final paragraph
    if current_paragraph:
        para = ' '.join(current_paragraph)
        if len(para) >= MIN_PARAGRAPH_LENGTH:
            paragraphs.append(para)
    
    return '\n\n'.join(paragraphs)


def remove_duplicates(paragraphs_text: str) -> str:
    """Remove duplicate paragraphs while maintaining order."""
    paragraphs = paragraphs_text.split('\n\n')
    seen: Set[str] = set()
    unique_paragraphs = []
    
    for para in paragraphs:
        para_normalized = para.lower().strip()
        if para_normalized not in seen and para_normalized:
            seen.add(para_normalized)
            unique_paragraphs.append(para)
    
    return '\n\n'.join(unique_paragraphs)


def extract_and_clean_pdfs():
    """Main function to extract and clean all PDFs."""
    print("=" * 70)
    print("PDF EXTRACTION AND CLEANING")
    print("=" * 70)
    
    # Find all PDF files
    pdf_files = sorted(PDF_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {PDF_DIR}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files in {PDF_DIR}")
    print()
    
    all_text = []
    total_pages = 0
    
    # Process each PDF
    for pdf_path in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
        try:
            reader = PdfReader(str(pdf_path))
            pdf_text = []
            
            for page in reader.pages:
                try:
                    text = page.extract_text() or ""
                    if text.strip():
                        pdf_text.append(text)
                        total_pages += 1
                except Exception as e:
                    print(f"⚠️  Warning: Failed to extract page from {pdf_path.name}: {e}")
                    continue
            
            # Combine all pages from this PDF
            combined = '\n'.join(pdf_text)
            
            # Clean the text
            cleaned = clean_text(combined)
            
            if cleaned:
                all_text.append(cleaned)
                
        except Exception as e:
            print(f"❌ Error processing {pdf_path.name}: {e}")
            continue
    
    print(f"\n✓ Extracted text from {total_pages} pages")
    
    # Combine all PDF texts
    print("\n📝 Merging and cleaning text...")
    combined_text = '\n\n'.join(all_text)
    
    # Merge into paragraphs
    paragraphs = merge_into_paragraphs(combined_text)
    
    # Remove duplicates
    unique_text = remove_duplicates(paragraphs)
    
    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(unique_text)
    
    # Statistics
    char_count = len(unique_text)
    word_count = len(unique_text.split())
    para_count = len(unique_text.split('\n\n'))
    
    print("\n" + "=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print(f"📄 Output file: {OUTPUT_FILE.resolve()}")
    print(f"📊 Statistics:")
    print(f"   - Total characters: {char_count:,}")
    print(f"   - Total words: {word_count:,}")
    print(f"   - Total paragraphs: {para_count:,}")
    print(f"   - Average words per paragraph: {word_count // para_count if para_count > 0 else 0}")
    print("=" * 70)


if __name__ == "__main__":
    extract_and_clean_pdfs()
