"""
Generate Q&A pairs from the agricultural corpus for supervised fine-tuning.

This script:
1. Reads the cleaned corpus from mini_llm/data/agri_corpus.txt
2. Extracts key agricultural concepts (crops, pests, diseases, fertilizers)
3. Generates Q&A pairs using pattern matching and templates
4. Saves to mini_llm/data/qa_pairs.jsonl
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
import random


# Configuration
CORPUS_FILE = Path("mini_llm/data/agri_corpus.txt")
OUTPUT_FILE = Path("mini_llm/data/qa_pairs.jsonl")
TARGET_QA_PAIRS = 150  # Target number of Q&A pairs


# Keywords to identify relevant agricultural topics
CROP_KEYWORDS = ['maize', 'wheat', 'rice', 'potato', 'tomato', 'pepper', 'barley', 'millet', 'sorghum', 'cotton']
PEST_KEYWORDS = ['pest', 'insect', 'aphid', 'caterpillar', 'worm', 'beetle', 'borer', 'weevil']
DISEASE_KEYWORDS = ['disease', 'blight', 'rot', 'mildew', 'wilt', 'spot', 'virus', 'fungus', 'bacterial']
FERTILIZER_KEYWORDS = ['fertilizer', 'fertiliser', 'nitrogen', 'phosphorus', 'potassium', 'urea', 'manure', 'compost', 'nutrient']
PRACTICE_KEYWORDS = ['planting', 'sowing', 'irrigation', 'cultivation', 'harvesting', 'spacing', 'yield']


# Question templates
QUESTION_TEMPLATES = {
    'what': [
        "What is {}?",
        "What are the characteristics of {}?",
        "What are the benefits of {}?",
        "What causes {}?",
        "What is the recommended {} for {}?",
    ],
    'how': [
        "How to manage {}?",
        "How to control {}?",
        "How to apply {}?",
        "How to prevent {}?",
        "How should {} be used?",
    ],
    'when': [
        "When should {} be applied?",
        "When to plant {}?",
        "When does {} occur?",
    ],
    'why': [
        "Why is {} important?",
        "Why does {} happen?",
    ],
    'which': [
        "Which fertilizer is best for {}?",
        "Which method is recommended for {}?",
    ]
}


def load_corpus() -> List[str]:
    """Load and return paragraphs from the corpus."""
    if not CORPUS_FILE.exists():
        raise FileNotFoundError(f"Corpus file not found: {CORPUS_FILE}")
    
    with open(CORPUS_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    return paragraphs


def extract_sentences(paragraph: str) -> List[str]:
    """Split paragraph into sentences."""
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', paragraph)
    return [s.strip() for s in sentences if len(s.strip()) > 20]


def contains_keywords(text: str, keywords: List[str]) -> bool:
    """Check if text contains any of the keywords."""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def extract_topic(sentence: str, keywords: List[str]) -> str:
    """Extract the main topic from a sentence based on keywords."""
    sentence_lower = sentence.lower()
    for keyword in keywords:
        if keyword in sentence_lower:
            # Try to extract the phrase around the keyword
            pattern = r'\b(\w+\s+)?' + re.escape(keyword) + r'(\s+\w+)?'
            match = re.search(pattern, sentence_lower)
            if match:
                return match.group(0).strip()
    return ""


def generate_qa_from_paragraph(paragraph: str) -> List[Dict[str, str]]:
    """Generate Q&A pairs from a single paragraph."""
    qa_pairs = []
    sentences = extract_sentences(paragraph)
    
    if not sentences or len(sentences) < 2:
        return qa_pairs
    
    # Check for different types of content
    has_fertilizer = contains_keywords(paragraph, FERTILIZER_KEYWORDS)
    has_pest = contains_keywords(paragraph, PEST_KEYWORDS)
    has_disease = contains_keywords(paragraph, DISEASE_KEYWORDS)
    has_crop = contains_keywords(paragraph, CROP_KEYWORDS)
    
    # Generate questions based on content type
    if has_fertilizer and has_crop:
        crop = extract_topic(paragraph, CROP_KEYWORDS)
        if crop:
            question = f"What fertilizer should be used for {crop}?"
            answer = paragraph[:500]  # Limit answer length
            qa_pairs.append({"question": question, "answer": answer})
    
    if has_pest or has_disease:
        issue = extract_topic(paragraph, PEST_KEYWORDS + DISEASE_KEYWORDS)
        if issue:
            question = f"How to control {issue}?"
            answer = paragraph[:500]
            qa_pairs.append({"question": question, "answer": answer})
    
    if has_crop and contains_keywords(paragraph, PRACTICE_KEYWORDS):
        crop = extract_topic(paragraph, CROP_KEYWORDS)
        practice = extract_topic(paragraph, PRACTICE_KEYWORDS)
        if crop and practice:
            question = f"What is the recommended {practice} for {crop}?"
            answer = paragraph[:500]
            qa_pairs.append({"question": question, "answer": answer})
    
    # Generic questions from informative paragraphs
    if len(paragraph) > 100 and len(paragraph) < 600:
        # Extract key phrase from first sentence
        first_sentence = sentences[0]
        if len(first_sentence.split()) > 5:
            # Create a "What is..." question
            words = first_sentence.split()[:10]
            topic_phrase = ' '.join(words)
            
            # Try to identify the main subject
            subject_match = re.search(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', first_sentence)
            if subject_match:
                subject = subject_match.group(1)
                if len(subject.split()) <= 4:
                    question = f"What is {subject}?"
                    answer = paragraph[:500]
                    qa_pairs.append({"question": question, "answer": answer})
    
    return qa_pairs


def generate_qa_pairs(paragraphs: List[str], target_count: int = TARGET_QA_PAIRS) -> List[Dict[str, str]]:
    """Generate Q&A pairs from all paragraphs."""
    print(f"\n📝 Generating Q&A pairs from {len(paragraphs)} paragraphs...")
    
    all_qa_pairs = []
    seen_questions = set()
    
    # Shuffle paragraphs for diversity
    shuffled_paragraphs = paragraphs.copy()
    random.shuffle(shuffled_paragraphs)
    
    for paragraph in shuffled_paragraphs:
        if len(all_qa_pairs) >= target_count:
            break
        
        # Skip very short or very long paragraphs
        if len(paragraph) < 100 or len(paragraph) > 1000:
            continue
        
        qa_pairs = generate_qa_from_paragraph(paragraph)
        
        for qa in qa_pairs:
            # Avoid duplicate questions
            q_normalized = qa['question'].lower().strip()
            if q_normalized not in seen_questions:
                seen_questions.add(q_normalized)
                all_qa_pairs.append(qa)
                
                if len(all_qa_pairs) >= target_count:
                    break
    
    # Add some template-based Q&A pairs for common topics
    template_qa = generate_template_qa(paragraphs, target_count - len(all_qa_pairs))
    all_qa_pairs.extend(template_qa)
    
    return all_qa_pairs[:target_count]


def generate_template_qa(paragraphs: List[str], count: int) -> List[Dict[str, str]]:
    """Generate additional Q&A pairs using templates."""
    template_qa = []
    
    # Find paragraphs about specific crops
    crop_paragraphs = {}
    for crop in CROP_KEYWORDS:
        for para in paragraphs:
            if crop in para.lower() and len(para) > 150:
                if crop not in crop_paragraphs:
                    crop_paragraphs[crop] = []
                crop_paragraphs[crop].append(para)
    
    # Generate crop-related questions
    for crop, paras in crop_paragraphs.items():
        if len(template_qa) >= count:
            break
        
        para = random.choice(paras) if paras else ""
        if not para:
            continue
        
        questions = [
            f"How to grow {crop}?",
            f"What are the requirements for {crop} cultivation?",
            f"What pests affect {crop}?",
            f"What is the best fertilizer for {crop}?",
        ]
        
        for question in questions:
            if len(template_qa) >= count:
                break
            template_qa.append({
                "question": question,
                "answer": para[:500]
            })
    
    return template_qa


def save_qa_pairs(qa_pairs: List[Dict[str, str]], output_path: Path):
    """Save Q&A pairs to JSONL file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for qa in qa_pairs:
            json_line = json.dumps(qa, ensure_ascii=False)
            f.write(json_line + '\n')


def main():
    """Main function to generate Q&A pairs."""
    print("=" * 70)
    print("Q&A PAIRS GENERATION")
    print("=" * 70)
    
    # Load corpus
    print(f"\n📖 Loading corpus from {CORPUS_FILE}...")
    paragraphs = load_corpus()
    print(f"✓ Loaded {len(paragraphs)} paragraphs")
    
    # Generate Q&A pairs
    qa_pairs = generate_qa_pairs(paragraphs, TARGET_QA_PAIRS)
    
    # Save to file
    print(f"\n💾 Saving Q&A pairs to {OUTPUT_FILE}...")
    save_qa_pairs(qa_pairs, OUTPUT_FILE)
    
    # Statistics
    print("\n" + "=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)
    print(f"📄 Output file: {OUTPUT_FILE.resolve()}")
    print(f"📊 Statistics:")
    print(f"   - Total Q&A pairs: {len(qa_pairs)}")
    print(f"   - Average question length: {sum(len(qa['question']) for qa in qa_pairs) // len(qa_pairs)} chars")
    print(f"   - Average answer length: {sum(len(qa['answer']) for qa in qa_pairs) // len(qa_pairs)} chars")
    
    # Show sample Q&A pairs
    print(f"\n📝 Sample Q&A pairs:")
    for i, qa in enumerate(qa_pairs[:3], 1):
        print(f"\n   {i}. Q: {qa['question']}")
        print(f"      A: {qa['answer'][:100]}...")
    
    print("=" * 70)


if __name__ == "__main__":
    main()
