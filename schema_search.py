import os
from docx import Document
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json
import re

class HSMLSchemaSearch:
    def __init__(self, docx_path="docs/HSML Schema Doc.docx"):
        self.docx_path = docx_path
        self.schema_text = ""
        self.schema_chunks = []
        self.embeddings = None
        self.model = None
        self.load_schema()
        
    def load_schema(self):
        """Load and parse the HSML schema document"""
        try:
            doc = Document(self.docx_path)
            full_text = []
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text.strip())
            
            self.schema_text = "\n".join(full_text)
            self.chunk_schema()
            self.initialize_embeddings()
            
        except Exception as e:
            print(f"Error loading schema document: {e}")
            self.schema_text = "Error: Could not load HSML schema document"
    
    def chunk_schema(self, chunk_size=500, overlap=100):
        """Split schema into searchable chunks"""
        if not self.schema_text:
            return
            
        words = self.schema_text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        self.schema_chunks = chunks
    
    def initialize_embeddings(self):
        """Initialize sentence transformer model for semantic search"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            if self.schema_chunks:
                self.embeddings = self.model.encode(self.schema_chunks)
        except Exception as e:
            print(f"Error initializing embeddings: {e}")
    
    def search_schema(self, query, top_k=3):
        """Search the schema for relevant information"""
        if not self.model or self.embeddings is None or not self.schema_chunks:
            return []
        
        try:
            # Encode the query
            query_embedding = self.model.encode([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Get top matches
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    results.append({
                        'text': self.schema_chunks[idx],
                        'similarity': float(similarities[idx])
                    })
            
            return results
            
        except Exception as e:
            print(f"Error searching schema: {e}")
            return []
    
    def get_hsml_rules(self, json_data):
        """Get relevant HSML rules for a given JSON input"""
        search_terms = []
        
        if isinstance(json_data, dict):
            # Determine entity type based on content
            entity_type = self.determine_entity_type(json_data)
            search_terms.append(entity_type)
            
            # Add specific field-based searches
            for key, value in json_data.items():
                # Search for field definitions
                search_terms.append(f"{entity_type} {key}")
                
                # Search for specific field patterns
                if key in ['email', 'birth_date', 'job_title', 'works_for', 'affiliation', 'owns']:
                    search_terms.append(f"Person {key}")
                elif key in ['issued_by', 'access_authorization', 'authorized_for_domain', 'valid_for', 'valid_from', 'valid_until']:
                    search_terms.append(f"Credential {key}")
                elif key in ['position', 'rotation', 'space_location', 'creator', 'additional_properties']:
                    search_terms.append(f"Agent {key}")
                elif key in ['parent_company', 'subsidiaries']:
                    search_terms.append(f"Organization {key}")
            
            # Add general entity type searches
            search_terms.extend([
                f"{entity_type} definition",
                f"{entity_type} properties",
                f"{entity_type} required fields",
                f"{entity_type} schema"
            ])
        
        # Search for relevant rules with higher precision
        all_results = []
        for term in search_terms[:8]:  # Increased limit
            results = self.search_schema(term, top_k=3)  # More results per term
            all_results.extend(results)
        
        # Remove duplicates and sort by similarity
        unique_results = {}
        for result in all_results:
            text = result['text']
            if text not in unique_results or result['similarity'] > unique_results[text]['similarity']:
                unique_results[text] = result
        
        return sorted(unique_results.values(), key=lambda x: x['similarity'], reverse=True)
    
    def determine_entity_type(self, json_data):
        """Determine the most likely HSML entity type based on input data"""
        # Check for explicit type
        if 'type' in json_data:
            type_val = json_data['type'].lower()
            if type_val in ['person', 'human', 'user', 'employee']:
                return 'Person'
            elif type_val in ['agent', 'ai', 'bot', 'game_object']:
                return 'Agent'
            elif type_val in ['credential', 'access', 'permission']:
                return 'Credential'
            elif type_val in ['organization', 'company', 'corp']:
                return 'Organization'
            elif type_val in ['object', '3d', 'model']:
                return 'Object'
        
        # Analyze fields to determine type
        fields = set(json_data.keys())
        
        # Person indicators
        person_fields = {'email', 'birth_date', 'job_title', 'works_for', 'affiliation', 'owns', 'role'}
        if fields.intersection(person_fields):
            return 'Person'
        
        # Credential indicators
        credential_fields = {'issued_by', 'access_authorization', 'authorized_for_domain', 'valid_for', 'valid_from', 'valid_until', 'valid_in'}
        if fields.intersection(credential_fields):
            return 'Credential'
        
        # Agent indicators (3D data)
        agent_fields = {'position', 'rotation', 'space_location', 'creator', 'additional_properties', 'platform', 'model_url'}
        if fields.intersection(agent_fields):
            return 'Agent'
        
        # Organization indicators
        org_fields = {'parent_company', 'subsidiaries', 'department'}
        if fields.intersection(org_fields):
            return 'Organization'
        
        # Default based on most common field
        if 'name' in fields:
            return 'Entity'  # Generic entity
        
        return 'Entity'
    
    def format_rules_for_prompt(self, rules):
        """Format found rules for inclusion in AI prompt"""
        if not rules:
            return ""
        
        formatted_rules = "**HSML SCHEMA RULES** - Use these exact specifications:\n\n"
        for i, rule in enumerate(rules[:5], 1):  # Increased to top 5 rules
            similarity = rule['similarity']
            formatted_rules += f"**Rule {i}** (Relevance: {similarity:.2f}):\n{rule['text']}\n\n"
        
        formatted_rules += "**IMPORTANT**: Follow the schema exactly. Use the field names, types, and structures specified above. Do not deviate from the schema definitions."
        
        return formatted_rules

# Global instance
schema_search = None

def get_schema_search():
    """Get or create the global schema search instance"""
    global schema_search
    if schema_search is None:
        schema_search = HSMLSchemaSearch()
    return schema_search 