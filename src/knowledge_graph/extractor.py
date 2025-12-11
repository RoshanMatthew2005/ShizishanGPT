"""
AgriKG Triple Extractor
Extracts structured triples from Word documents using NLP and pattern matching.
"""

import re
import csv
from pathlib import Path
from typing import List, Dict, Tuple, Set
from docx import Document
import spacy
from collections import defaultdict


class AgriKGExtractor:
    """Extract agricultural knowledge triples from Word documents."""
    
    def __init__(self, data_dir: str = "Data/AgriKF_Data"):
        """
        Initialize the extractor.
        
        Args:
            data_dir: Directory containing Word documents
        """
        self.data_dir = Path(data_dir)
        self.triples = []
        self.entities = defaultdict(set)
        
        # Load spaCy model for NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("⚠️  Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Agricultural patterns for relationship extraction
        self.disease_patterns = [
            r'(?P<crop>\w+)\s+(?:is affected by|suffers from|infected by)\s+(?P<disease>[\w\s]+)',
            r'(?P<disease>[\w\s]+)\s+(?:affects|infects|damages)\s+(?P<crop>\w+)',
            r'(?P<disease>[\w\s]+)\s+(?:disease|infection)\s+(?:in|of)\s+(?P<crop>\w+)',
        ]
        
        self.pest_patterns = [
            r'(?P<crop>\w+)\s+(?:is attacked by|infested with)\s+(?P<pest>[\w\s]+)',
            r'(?P<pest>[\w\s]+)\s+(?:attacks|infests|damages)\s+(?P<crop>\w+)',
            r'(?P<pest>[\w\s]+)\s+(?:pest|insect)\s+(?:on|of)\s+(?P<crop>\w+)',
        ]
        
        self.fertilizer_patterns = [
            r'(?P<crop>\w+)\s+(?:requires|needs)\s+(?P<fertilizer>[\w\s]+(?:fertilizer|NPK|urea))',
            r'apply\s+(?P<fertilizer>[\w\s]+)\s+(?:to|for)\s+(?P<crop>\w+)',
            r'(?P<fertilizer>[\w\s]+)\s+(?:is recommended for|suitable for)\s+(?P<crop>\w+)',
        ]
        
        self.soil_patterns = [
            r'(?P<crop>\w+)\s+(?:grows well in|prefers|requires)\s+(?P<soil>[\w\s]+soil)',
            r'(?P<soil>[\w\s]+soil)\s+(?:is ideal for|suitable for)\s+(?P<crop>\w+)',
        ]
        
        self.treatment_patterns = [
            r'(?P<disease>[\w\s]+)\s+(?:treated with|controlled by)\s+(?P<treatment>[\w\s]+)',
            r'(?:use|apply)\s+(?P<treatment>[\w\s]+)\s+(?:to treat|for)\s+(?P<disease>[\w\s]+)',
        ]
    
    def read_docx(self, file_path: Path) -> str:
        """
        Read text from a Word document.
        
        Args:
            file_path: Path to .docx file
            
        Returns:
            Extracted text
        """
        try:
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"❌ Error reading {file_path.name}: {e}")
            return ""
    
    def normalize_entity(self, entity: str, entity_type: str) -> str:
        """
        Normalize entity names (lowercase, clean, standardize).
        
        Args:
            entity: Entity name
            entity_type: Type of entity
            
        Returns:
            Normalized entity name
        """
        # Clean and lowercase
        entity = entity.strip().lower()
        
        # Remove extra spaces
        entity = re.sub(r'\s+', ' ', entity)
        
        # Remove common words
        stopwords = ['the', 'a', 'an', 'of', 'in', 'on', 'at', 'to', 'for']
        words = entity.split()
        entity = ' '.join([w for w in words if w not in stopwords])
        
        # Standardize crop names
        crop_map = {
            'paddy': 'rice',
            'wheat crop': 'wheat',
            'maize crop': 'maize',
            'corn': 'maize',
        }
        if entity_type == 'Crop' and entity in crop_map:
            entity = crop_map[entity]
        
        return entity.strip()
    
    def extract_from_patterns(self, text: str, patterns: List[str], 
                             subject_type: str, object_type: str, 
                             relation: str) -> List[Tuple[str, str, str]]:
        """
        Extract triples using regex patterns.
        
        Args:
            text: Input text
            patterns: List of regex patterns
            subject_type: Type of subject entity
            object_type: Type of object entity
            relation: Relationship type
            
        Returns:
            List of (subject, relation, object) triples
        """
        triples = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groupdict()
                
                # Extract and normalize entities
                if 'crop' in groups and 'disease' in groups:
                    crop = self.normalize_entity(groups['crop'], 'Crop')
                    disease = self.normalize_entity(groups['disease'], 'Disease')
                    if relation == 'AFFECTED_BY_DISEASE':
                        triples.append((crop, relation, disease))
                    else:
                        triples.append((disease, relation, crop))
                    
                    self.entities['Crop'].add(crop)
                    self.entities['Disease'].add(disease)
                
                elif 'crop' in groups and 'pest' in groups:
                    crop = self.normalize_entity(groups['crop'], 'Crop')
                    pest = self.normalize_entity(groups['pest'], 'Pest')
                    triples.append((crop, 'AFFECTED_BY_PEST', pest))
                    
                    self.entities['Crop'].add(crop)
                    self.entities['Pest'].add(pest)
                
                elif 'crop' in groups and 'fertilizer' in groups:
                    crop = self.normalize_entity(groups['crop'], 'Crop')
                    fertilizer = self.normalize_entity(groups['fertilizer'], 'Fertilizer')
                    triples.append((crop, 'REQUIRES_FERTILIZER', fertilizer))
                    
                    self.entities['Crop'].add(crop)
                    self.entities['Fertilizer'].add(fertilizer)
                
                elif 'crop' in groups and 'soil' in groups:
                    crop = self.normalize_entity(groups['crop'], 'Crop')
                    soil = self.normalize_entity(groups['soil'], 'Soil')
                    triples.append((crop, 'GROWS_IN_SOIL', soil))
                    
                    self.entities['Crop'].add(crop)
                    self.entities['Soil'].add(soil)
                
                elif 'disease' in groups and 'treatment' in groups:
                    disease = self.normalize_entity(groups['disease'], 'Disease')
                    treatment = self.normalize_entity(groups['treatment'], 'Treatment')
                    triples.append((disease, 'TREATED_BY', treatment))
                    
                    self.entities['Disease'].add(disease)
                    self.entities['Treatment'].add(treatment)
        
        return triples
    
    def extract_from_document(self, file_path: Path) -> List[Tuple[str, str, str]]:
        """
        Extract triples from a single document.
        
        Args:
            file_path: Path to document
            
        Returns:
            List of triples
        """
        print(f"📄 Processing: {file_path.name}")
        
        # Read document
        text = self.read_docx(file_path)
        if not text:
            return []
        
        doc_triples = []
        
        # Extract using patterns
        doc_triples.extend(self.extract_from_patterns(
            text, self.disease_patterns, 'Crop', 'Disease', 'AFFECTED_BY_DISEASE'))
        doc_triples.extend(self.extract_from_patterns(
            text, self.pest_patterns, 'Crop', 'Pest', 'AFFECTED_BY_PEST'))
        doc_triples.extend(self.extract_from_patterns(
            text, self.fertilizer_patterns, 'Crop', 'Fertilizer', 'REQUIRES_FERTILIZER'))
        doc_triples.extend(self.extract_from_patterns(
            text, self.soil_patterns, 'Crop', 'Soil', 'GROWS_IN_SOIL'))
        doc_triples.extend(self.extract_from_patterns(
            text, self.treatment_patterns, 'Disease', 'Treatment', 'TREATED_BY'))
        
        # Use NLP for additional extraction
        doc = self.nlp(text)
        
        # Extract crop names from filename
        filename = file_path.stem.lower()
        if 'rice' in filename or 'paddy' in filename:
            self.entities['Crop'].add('rice')
        elif 'wheat' in filename:
            self.entities['Crop'].add('wheat')
        elif 'maize' in filename or 'corn' in filename:
            self.entities['Crop'].add('maize')
        
        # Extract diseases from headers/titles
        for sent in doc.sents:
            text_lower = sent.text.lower()
            if 'disease' in text_lower or 'blight' in text_lower or 'rot' in text_lower:
                # Extract disease name
                disease_name = sent.text.strip()
                if len(disease_name) < 50:  # Likely a title
                    disease_name = self.normalize_entity(disease_name, 'Disease')
                    self.entities['Disease'].add(disease_name)
                    
                    # Link to crop if found in filename
                    for crop in self.entities['Crop']:
                        if crop in filename:
                            doc_triples.append((crop, 'AFFECTED_BY_DISEASE', disease_name))
        
        print(f"  ✓ Extracted {len(doc_triples)} triples")
        return doc_triples
    
    def extract_all(self) -> List[Tuple[str, str, str]]:
        """
        Extract triples from all documents in data directory.
        
        Returns:
            List of all triples
        """
        print(f"\n{'='*70}")
        print("🌾 AgriKG Triple Extraction")
        print(f"{'='*70}\n")
        
        if not self.data_dir.exists():
            print(f"❌ Directory not found: {self.data_dir}")
            return []
        
        # Find all .docx files
        docx_files = list(self.data_dir.glob("*.docx"))
        
        if not docx_files:
            print(f"❌ No .docx files found in {self.data_dir}")
            return []
        
        print(f"Found {len(docx_files)} Word documents\n")
        
        # Extract from each document
        for file_path in docx_files:
            doc_triples = self.extract_from_document(file_path)
            self.triples.extend(doc_triples)
        
        # Remove duplicates
        self.triples = list(set(self.triples))
        
        print(f"\n{'='*70}")
        print(f"✅ Extraction Complete")
        print(f"{'='*70}")
        print(f"Total Triples: {len(self.triples)}")
        print(f"Unique Crops: {len(self.entities['Crop'])}")
        print(f"Unique Diseases: {len(self.entities['Disease'])}")
        print(f"Unique Pests: {len(self.entities['Pest'])}")
        print(f"Unique Fertilizers: {len(self.entities['Fertilizer'])}")
        print(f"Unique Soils: {len(self.entities['Soil'])}")
        print(f"Unique Treatments: {len(self.entities['Treatment'])}")
        print(f"{'='*70}\n")
        
        return self.triples
    
    def save_to_csv(self, output_file: str = "data/agri_triples.csv"):
        """
        Save extracted triples to CSV file.
        
        Args:
            output_file: Output CSV file path
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['subject', 'relation', 'object'])
            writer.writerows(self.triples)
        
        print(f"💾 Saved {len(self.triples)} triples to {output_path}")
    
    def get_statistics(self) -> Dict:
        """Get extraction statistics."""
        relation_counts = defaultdict(int)
        for subject, relation, obj in self.triples:
            relation_counts[relation] += 1
        
        return {
            'total_triples': len(self.triples),
            'unique_entities': {k: len(v) for k, v in self.entities.items()},
            'relation_counts': dict(relation_counts)
        }


if __name__ == "__main__":
    # Run extraction
    extractor = AgriKGExtractor()
    triples = extractor.extract_all()
    
    # Save to CSV
    extractor.save_to_csv()
    
    # Print statistics
    stats = extractor.get_statistics()
    print("\n📊 Statistics:")
    print(f"  Total Triples: {stats['total_triples']}")
    print(f"\n  Entities by Type:")
    for entity_type, count in stats['unique_entities'].items():
        print(f"    - {entity_type}: {count}")
    print(f"\n  Relations:")
    for relation, count in stats['relation_counts'].items():
        print(f"    - {relation}: {count}")
