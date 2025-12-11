"""
Build Agriculture Knowledge Graph
Main script to extract, build, and deploy AgriKG.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.knowledge_graph.extractor import AgriKGExtractor
from src.knowledge_graph.builder import AgriKGBuilder


def main():
    """Main function to build the knowledge graph."""
    print("\n" + "="*70)
    print("🌾 Agriculture Knowledge Graph Builder")
    print("="*70 + "\n")
    
    # Step 1: Extract triples from Word documents
    print("STEP 1: Extracting triples from documents...")
    print("-" * 70)
    
    extractor = AgriKGExtractor(data_dir="Data/AgriKF_Data")
    triples = extractor.extract_all()
    
    if not triples:
        print("\n❌ No triples extracted. Please check your data directory.")
        return
    
    # Save triples to CSV
    extractor.save_to_csv("data/agri_triples.csv")
    
    # Print extraction statistics
    stats = extractor.get_statistics()
    print(f"\n📊 Extraction Statistics:")
    print(f"  Total Triples: {stats['total_triples']}")
    print(f"  Unique Entities:")
    for entity_type, count in stats['unique_entities'].items():
        if count > 0:
            print(f"    - {entity_type}: {count}")
    
    # Step 2: Build knowledge graph in Neo4j
    print(f"\n{'='*70}")
    print("STEP 2: Building knowledge graph in Neo4j...")
    print("-" * 70)
    
    try:
        builder = AgriKGBuilder()
        
        # Clear existing data
        builder.clear_database()
        
        # Create indexes and constraints
        builder.create_indexes()
        builder.create_constraints()
        
        # Load triples
        builder.load_triples_from_csv("data/agri_triples.csv")
        
        # Add curated data
        builder.add_manual_data()
        
        # Print statistics
        builder.print_statistics()
        
        print(f"\n{'='*70}")
        print("✅ AgriKG Built Successfully!")
        print(f"{'='*70}\n")
        
        print("📝 Next Steps:")
        print("  1. Test queries using: python test_agri_kg.py")
        print("  2. Start the backend API to use KG in your application")
        print("  3. Query example: 'What diseases affect rice?'")
        print(f"\n{'='*70}\n")
        
    except Exception as e:
        print(f"\n❌ Error building knowledge graph: {e}")
        print("\n📝 Make sure:")
        print("  1. Neo4j is installed and running")
        print("  2. Neo4j credentials are set in .env file:")
        print("     NEO4J_URI=bolt://localhost:7687")
        print("     NEO4J_USER=neo4j")
        print("     NEO4J_PASSWORD=your_password")
        print(f"\n{'='*70}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
