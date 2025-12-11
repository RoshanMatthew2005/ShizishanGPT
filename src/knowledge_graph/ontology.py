"""
AgriKG Ontology Definition
Defines the schema for the Agriculture Knowledge Graph.
"""

# Node Types
NODE_TYPES = {
    'Crop': {
        'properties': ['name', 'scientific_name', 'family', 'season', 'growth_duration'],
        'description': 'Agricultural crops (rice, wheat, maize, etc.)'
    },
    'Disease': {
        'properties': ['name', 'pathogen_type', 'severity', 'symptoms'],
        'description': 'Plant diseases and infections'
    },
    'Pest': {
        'properties': ['name', 'scientific_name', 'type', 'damage_type'],
        'description': 'Insects and pests affecting crops'
    },
    'Fertilizer': {
        'properties': ['name', 'type', 'npk_ratio', 'application_method'],
        'description': 'Fertilizers and nutrients'
    },
    'Pesticide': {
        'properties': ['name', 'type', 'active_ingredient', 'target'],
        'description': 'Pesticides, fungicides, herbicides'
    },
    'Soil': {
        'properties': ['type', 'ph_range', 'texture', 'drainage'],
        'description': 'Soil types and characteristics'
    },
    'Climate': {
        'properties': ['zone', 'temperature_range', 'rainfall_range', 'humidity'],
        'description': 'Climate zones and conditions'
    },
    'Region': {
        'properties': ['name', 'state', 'country', 'agro_zone'],
        'description': 'Geographic regions'
    },
    'Nutrient': {
        'properties': ['name', 'symbol', 'role', 'deficiency_symptoms'],
        'description': 'Plant nutrients (N, P, K, etc.)'
    },
    'Treatment': {
        'properties': ['name', 'method', 'dosage', 'timing'],
        'description': 'Disease/pest treatment methods'
    }
}

# Relationship Types
RELATIONSHIP_TYPES = {
    # Crop relationships
    'AFFECTED_BY_DISEASE': {
        'from': 'Crop',
        'to': 'Disease',
        'properties': ['severity', 'stage', 'symptoms'],
        'description': 'Crop is affected by a disease'
    },
    'AFFECTED_BY_PEST': {
        'from': 'Crop',
        'to': 'Pest',
        'properties': ['damage_level', 'stage', 'signs'],
        'description': 'Crop is affected by a pest'
    },
    'REQUIRES_FERTILIZER': {
        'from': 'Crop',
        'to': 'Fertilizer',
        'properties': ['stage', 'quantity', 'frequency'],
        'description': 'Crop requires specific fertilizer'
    },
    'REQUIRES_NUTRIENT': {
        'from': 'Crop',
        'to': 'Nutrient',
        'properties': ['quantity', 'stage', 'importance'],
        'description': 'Crop requires specific nutrient'
    },
    'GROWS_IN_SOIL': {
        'from': 'Crop',
        'to': 'Soil',
        'properties': ['suitability', 'yield_impact'],
        'description': 'Crop grows in specific soil type'
    },
    'GROWS_IN_CLIMATE': {
        'from': 'Crop',
        'to': 'Climate',
        'properties': ['suitability', 'yield_potential'],
        'description': 'Crop grows in specific climate'
    },
    'GROWN_IN_REGION': {
        'from': 'Crop',
        'to': 'Region',
        'properties': ['area', 'production', 'major_variety'],
        'description': 'Crop is grown in region'
    },
    
    # Disease relationships
    'TREATED_BY': {
        'from': 'Disease',
        'to': 'Treatment',
        'properties': ['efficacy', 'timing', 'method'],
        'description': 'Disease is treated by treatment method'
    },
    'CONTROLLED_BY_PESTICIDE': {
        'from': 'Disease',
        'to': 'Pesticide',
        'properties': ['dosage', 'application_method', 'timing'],
        'description': 'Disease is controlled by pesticide'
    },
    'OCCURS_IN_CLIMATE': {
        'from': 'Disease',
        'to': 'Climate',
        'properties': ['prevalence', 'season'],
        'description': 'Disease occurs in specific climate'
    },
    
    # Pest relationships
    'CONTROLLED_BY_PESTICIDE': {
        'from': 'Pest',
        'to': 'Pesticide',
        'properties': ['dosage', 'application_method', 'efficacy'],
        'description': 'Pest is controlled by pesticide'
    },
    'CONTROLLED_BY_TREATMENT': {
        'from': 'Pest',
        'to': 'Treatment',
        'properties': ['method', 'efficacy'],
        'description': 'Pest is controlled by treatment'
    },
    
    # Fertilizer relationships
    'CONTAINS_NUTRIENT': {
        'from': 'Fertilizer',
        'to': 'Nutrient',
        'properties': ['percentage', 'form'],
        'description': 'Fertilizer contains nutrient'
    },
    
    # Region relationships
    'HAS_CLIMATE': {
        'from': 'Region',
        'to': 'Climate',
        'properties': ['predominance'],
        'description': 'Region has climate zone'
    },
    'HAS_SOIL': {
        'from': 'Region',
        'to': 'Soil',
        'properties': ['predominance', 'area_percentage'],
        'description': 'Region has soil type'
    }
}

# Sample queries for validation
SAMPLE_QUERIES = {
    'diseases_for_crop': """
        MATCH (c:Crop {name: $crop_name})-[r:AFFECTED_BY_DISEASE]->(d:Disease)
        RETURN d.name as disease, r.severity as severity, r.symptoms as symptoms
        ORDER BY r.severity DESC
    """,
    
    'pests_for_crop': """
        MATCH (c:Crop {name: $crop_name})-[r:AFFECTED_BY_PEST]->(p:Pest)
        RETURN p.name as pest, p.type as pest_type, r.damage_level as damage
        ORDER BY r.damage_level DESC
    """,
    
    'fertilizers_for_crop': """
        MATCH (c:Crop {name: $crop_name})-[r:REQUIRES_FERTILIZER]->(f:Fertilizer)
        RETURN f.name as fertilizer, f.type as type, f.npk_ratio as npk, 
               r.stage as application_stage, r.quantity as quantity
        ORDER BY r.stage
    """,
    
    'ideal_soil_for_crop': """
        MATCH (c:Crop {name: $crop_name})-[r:GROWS_IN_SOIL]->(s:Soil)
        WHERE r.suitability = 'high' OR r.suitability = 'ideal'
        RETURN s.type as soil_type, s.ph_range as ph, s.texture as texture,
               r.yield_impact as impact
        ORDER BY r.suitability DESC
    """,
    
    'crops_for_region': """
        MATCH (r:Region {name: $region_name})-[rel:GROWN_IN_REGION]-(c:Crop)
        RETURN c.name as crop, c.season as season, rel.production as production,
               rel.major_variety as variety
        ORDER BY rel.production DESC
    """,
    
    'treatment_for_disease': """
        MATCH (d:Disease {name: $disease_name})-[r:TREATED_BY]->(t:Treatment)
        RETURN t.name as treatment, t.method as method, t.dosage as dosage,
               r.efficacy as efficacy, r.timing as timing
        ORDER BY r.efficacy DESC
    """,
    
    'pesticides_for_pest': """
        MATCH (p:Pest {name: $pest_name})-[r:CONTROLLED_BY_PESTICIDE]->(pc:Pesticide)
        RETURN pc.name as pesticide, pc.active_ingredient as ingredient,
               r.dosage as dosage, r.efficacy as efficacy
        ORDER BY r.efficacy DESC
    """,
    
    'crop_complete_info': """
        MATCH (c:Crop {name: $crop_name})
        OPTIONAL MATCH (c)-[rd:AFFECTED_BY_DISEASE]->(d:Disease)
        OPTIONAL MATCH (c)-[rp:AFFECTED_BY_PEST]->(p:Pest)
        OPTIONAL MATCH (c)-[rf:REQUIRES_FERTILIZER]->(f:Fertilizer)
        OPTIONAL MATCH (c)-[rs:GROWS_IN_SOIL]->(s:Soil)
        OPTIONAL MATCH (c)-[rcl:GROWS_IN_CLIMATE]->(cl:Climate)
        RETURN c, 
               collect(DISTINCT {disease: d.name, severity: rd.severity}) as diseases,
               collect(DISTINCT {pest: p.name, damage: rp.damage_level}) as pests,
               collect(DISTINCT {fertilizer: f.name, stage: rf.stage}) as fertilizers,
               collect(DISTINCT {soil: s.type, suitability: rs.suitability}) as soils,
               collect(DISTINCT {climate: cl.zone}) as climates
    """
}

def get_ontology_summary():
    """Get a summary of the ontology."""
    return {
        'node_types': list(NODE_TYPES.keys()),
        'relationship_types': list(RELATIONSHIP_TYPES.keys()),
        'total_nodes': len(NODE_TYPES),
        'total_relationships': len(RELATIONSHIP_TYPES)
    }
