"""
AgriKG Builder
Builds the knowledge graph in Neo4j using py2neo.
"""

import csv
from pathlib import Path
from typing import List, Dict, Tuple
from py2neo import Graph, Node, Relationship
from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom
import os
from dotenv import load_dotenv

load_dotenv()


class AgriKGBuilder:
    """Build Agriculture Knowledge Graph in Neo4j."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j URI (default: from env or localhost)
            user: Neo4j username (default: from env or neo4j)
            password: Neo4j password (default: from env)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = user or os.getenv("NEO4J_USER", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            self.graph = Graph(self.uri, auth=(self.user, self.password))
            print(f"✅ Connected to Neo4j at {self.uri}")
        except Exception as e:
            print(f"❌ Failed to connect to Neo4j: {e}")
            print(f"   Make sure Neo4j is running and credentials are correct")
            raise
    
    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        print("🗑️  Clearing existing database...")
        self.graph.delete_all()
        print("✅ Database cleared")
    
    def create_indexes(self):
        """Create indexes for faster querying."""
        print("📑 Creating indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS FOR (c:Crop) ON (c.name)",
            "CREATE INDEX IF NOT EXISTS FOR (d:Disease) ON (d.name)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Pest) ON (p.name)",
            "CREATE INDEX IF NOT EXISTS FOR (f:Fertilizer) ON (f.name)",
            "CREATE INDEX IF NOT EXISTS FOR (pc:Pesticide) ON (pc.name)",
            "CREATE INDEX IF NOT EXISTS FOR (s:Soil) ON (s.type)",
            "CREATE INDEX IF NOT EXISTS FOR (cl:Climate) ON (cl.zone)",
            "CREATE INDEX IF NOT EXISTS FOR (r:Region) ON (r.name)",
            "CREATE INDEX IF NOT EXISTS FOR (n:Nutrient) ON (n.name)",
            "CREATE INDEX IF NOT EXISTS FOR (t:Treatment) ON (t.name)",
        ]
        
        for index_query in indexes:
            self.graph.run(index_query)
        
        print("✅ Indexes created")
    
    def create_constraints(self):
        """Create uniqueness constraints."""
        print("🔒 Creating constraints...")
        
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Crop) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Pest) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (f:Fertilizer) REQUIRE f.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Soil) REQUIRE s.type IS UNIQUE",
        ]
        
        for constraint_query in constraints:
            try:
                self.graph.run(constraint_query)
            except Exception as e:
                print(f"  ⚠️  Constraint warning: {e}")
        
        print("✅ Constraints created")
    
    def create_or_get_node(self, label: str, name: str, **properties) -> Node:
        """
        Create or get existing node.
        
        Args:
            label: Node label
            name: Node name
            **properties: Additional properties
            
        Returns:
            Node object
        """
        # Check if node exists
        if label == 'Soil':
            match_query = f"MATCH (n:{label} {{type: $name}}) RETURN n"
        else:
            match_query = f"MATCH (n:{label} {{name: $name}}) RETURN n"
        
        result = self.graph.run(match_query, name=name).data()
        
        if result:
            return result[0]['n']
        
        # Create new node
        if label == 'Soil':
            node = Node(label, type=name, **properties)
        else:
            node = Node(label, name=name, **properties)
        
        self.graph.create(node)
        return node
    
    def load_triples_from_csv(self, csv_file: str = "data/agri_triples.csv"):
        """
        Load triples from CSV and create graph.
        
        Args:
            csv_file: Path to CSV file with triples
        """
        csv_path = Path(csv_file)
        
        if not csv_path.exists():
            print(f"❌ CSV file not found: {csv_path}")
            return
        
        print(f"\n{'='*70}")
        print("🌾 Building AgriKG from Triples")
        print(f"{'='*70}\n")
        
        # Read triples
        triples = []
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                triples.append((row['subject'], row['relation'], row['object']))
        
        print(f"📊 Loaded {len(triples)} triples from CSV")
        
        # Create nodes and relationships
        created_rels = 0
        
        for subject, relation, obj in triples:
            try:
                # Determine node labels based on relation
                if relation == 'AFFECTED_BY_DISEASE':
                    subject_node = self.create_or_get_node('Crop', subject)
                    object_node = self.create_or_get_node('Disease', obj)
                
                elif relation == 'AFFECTED_BY_PEST':
                    subject_node = self.create_or_get_node('Crop', subject)
                    object_node = self.create_or_get_node('Pest', obj)
                
                elif relation == 'REQUIRES_FERTILIZER':
                    subject_node = self.create_or_get_node('Crop', subject)
                    object_node = self.create_or_get_node('Fertilizer', obj)
                
                elif relation == 'GROWS_IN_SOIL':
                    subject_node = self.create_or_get_node('Crop', subject)
                    object_node = self.create_or_get_node('Soil', obj)
                
                elif relation == 'TREATED_BY':
                    subject_node = self.create_or_get_node('Disease', subject)
                    object_node = self.create_or_get_node('Treatment', obj)
                
                elif relation == 'CONTROLLED_BY_PESTICIDE':
                    if 'disease' in subject.lower():
                        subject_node = self.create_or_get_node('Disease', subject)
                    else:
                        subject_node = self.create_or_get_node('Pest', subject)
                    object_node = self.create_or_get_node('Pesticide', obj)
                
                else:
                    continue
                
                # Create relationship
                rel = Relationship(subject_node, relation, object_node)
                self.graph.merge(rel)
                created_rels += 1
                
                if created_rels % 10 == 0:
                    print(f"  Created {created_rels} relationships...", end='\r')
            
            except Exception as e:
                print(f"\n⚠️  Error creating triple ({subject}, {relation}, {obj}): {e}")
        
        print(f"\n\n{'='*70}")
        print(f"✅ Graph Building Complete")
        print(f"{'='*70}")
        print(f"Created {created_rels} relationships")
        print(f"{'='*70}\n")
    
    def add_manual_data(self):
        """Add additional curated data to enhance the knowledge graph."""
        print("📝 Adding curated knowledge...")
        
        # Add common soil types
        soil_types = [
            {'type': 'clay soil', 'texture': 'heavy', 'drainage': 'poor'},
            {'type': 'sandy soil', 'texture': 'light', 'drainage': 'good'},
            {'type': 'loamy soil', 'texture': 'balanced', 'drainage': 'good'},
            {'type': 'black soil', 'texture': 'heavy', 'drainage': 'moderate'},
            {'type': 'red soil', 'texture': 'friable', 'drainage': 'good'},
            {'type': 'alluvial soil', 'texture': 'variable', 'drainage': 'good'},
        ]
        
        for soil_data in soil_types:
            self.create_or_get_node('Soil', soil_data['type'], 
                                   texture=soil_data['texture'],
                                   drainage=soil_data['drainage'])
        
        # Add climate zones
        climates = [
            {'zone': 'tropical', 'temperature_range': '25-35°C', 'rainfall_range': '200-300cm'},
            {'zone': 'subtropical', 'temperature_range': '20-30°C', 'rainfall_range': '100-200cm'},
            {'zone': 'temperate', 'temperature_range': '10-20°C', 'rainfall_range': '50-100cm'},
        ]
        
        for climate_data in climates:
            self.create_or_get_node('Climate', climate_data['zone'],
                                   temperature_range=climate_data['temperature_range'],
                                   rainfall_range=climate_data['rainfall_range'])
        
        # Link crops to ideal conditions
        crop_conditions = [
            ('rice', 'GROWS_IN_SOIL', 'clay soil', {'suitability': 'high'}),
            ('rice', 'GROWS_IN_CLIMATE', 'tropical', {'suitability': 'high'}),
            ('wheat', 'GROWS_IN_SOIL', 'loamy soil', {'suitability': 'high'}),
            ('wheat', 'GROWS_IN_CLIMATE', 'temperate', {'suitability': 'high'}),
            ('maize', 'GROWS_IN_SOIL', 'loamy soil', {'suitability': 'high'}),
            ('maize', 'GROWS_IN_CLIMATE', 'subtropical', {'suitability': 'high'}),
        ]
        
        for crop_name, relation, condition, props in crop_conditions:
            crop = self.create_or_get_node('Crop', crop_name)
            if relation == 'GROWS_IN_SOIL':
                condition_node = self.create_or_get_node('Soil', condition)
            else:
                condition_node = self.create_or_get_node('Climate', condition)
            
            rel = Relationship(crop, relation, condition_node, **props)
            self.graph.merge(rel)
        
        print("✅ Curated knowledge added")
    
    def get_statistics(self) -> Dict:
        """Get graph statistics."""
        stats = {}
        
        # Count nodes by label
        labels = ['Crop', 'Disease', 'Pest', 'Fertilizer', 'Pesticide', 
                 'Soil', 'Climate', 'Region', 'Nutrient', 'Treatment']
        
        for label in labels:
            count = self.graph.run(f"MATCH (n:{label}) RETURN count(n) as count").data()[0]['count']
            stats[label] = count
        
        # Count relationships
        rel_count = self.graph.run("MATCH ()-[r]->() RETURN count(r) as count").data()[0]['count']
        stats['total_relationships'] = rel_count
        
        return stats
    
    def print_statistics(self):
        """Print graph statistics."""
        stats = self.get_statistics()
        
        print(f"\n{'='*70}")
        print("📊 AgriKG Statistics")
        print(f"{'='*70}")
        
        print("\nNodes by Type:")
        for label, count in stats.items():
            if label != 'total_relationships' and count > 0:
                print(f"  {label:15s}: {count:4d}")
        
        print(f"\nTotal Relationships: {stats['total_relationships']}")
        print(f"{'='*70}\n")


def build_knowledge_graph():
    """Main function to build the knowledge graph."""
    try:
        # Initialize builder
        builder = AgriKGBuilder()
        
        # Clear existing data
        builder.clear_database()
        
        # Create indexes and constraints
        builder.create_indexes()
        builder.create_constraints()
        
        # Load triples from CSV
        builder.load_triples_from_csv()
        
        # Add curated data
        builder.add_manual_data()
        
        # Print statistics
        builder.print_statistics()
        
        print("🎉 AgriKG built successfully!")
        
    except Exception as e:
        print(f"❌ Error building knowledge graph: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    build_knowledge_graph()
