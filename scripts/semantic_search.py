#!/usr/bin/env python3
"""
Semantic search for workflows
Uses TF-IDF embeddings for similarity search
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jsonlines
import pickle

class SemanticSearch:
    def __init__(self):
        self.vectorizer = None
        self.embeddings_matrix = None
        self.workflow_ids = {}
        self.embeddings_data = []
        self.loaded = False
    
    def load_index(self):
        """Load the TF-IDF vectorizer and metadata."""
        indexes_dir = Path('indexes')
        
        # Load TF-IDF vectorizer
        if (indexes_dir / 'tfidf_vectorizer.pkl').exists():
            with open(indexes_dir / 'tfidf_vectorizer.pkl', 'rb') as f:
                self.vectorizer = pickle.load(f)
        else:
            raise FileNotFoundError("TF-IDF vectorizer not found. Run generate_embeddings.py first.")
        
        # Load workflow ID mappings
        if (indexes_dir / 'workflow_ids.json').exists():
            with open(indexes_dir / 'workflow_ids.json', 'r') as f:
                self.workflow_ids = json.load(f)
        else:
            raise FileNotFoundError("Workflow IDs mapping not found. Run generate_embeddings.py first.")
        
        # Load embeddings metadata
        if (indexes_dir / 'embeddings.jsonl').exists():
            self.embeddings_data = []
            with jsonlines.open(indexes_dir / 'embeddings.jsonl', 'r') as reader:
                for item in reader:
                    self.embeddings_data.append(item)
        else:
            raise FileNotFoundError("Embeddings metadata not found. Run generate_embeddings.py first.")
        
        # Create embeddings matrix
        self.embeddings_matrix = np.array([item['embedding'] for item in self.embeddings_data])
        self.loaded = True
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar workflows."""
        if not self.loaded:
            self.load_index()
        
        # Transform the query using the same vectorizer
        query_vector = self.vectorizer.transform([query]).toarray()
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.embeddings_matrix)[0]
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Format results
        results = []
        for i, idx in enumerate(top_indices):
            embedding_item = self.embeddings_data[idx]
            workflow_id = embedding_item['workflow_id']
            
            result = {
                'rank': i + 1,
                'score': float(similarities[idx]),
                'workflow_id': workflow_id,
                'filename': embedding_item['filename'],
                'name': self.workflow_ids.get(workflow_id, {}).get('name', 'Unknown'),
                'search_text': embedding_item['search_text'][:200] + '...' if len(embedding_item['search_text']) > 200 else embedding_item['search_text']
            }
            results.append(result)
        
        return results
    
    def find_similar(self, workflow_id: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find workflows similar to a specific workflow."""
        if not self.loaded:
            self.load_index()
        
        # Find the workflow's embedding
        workflow_idx = None
        for i, item in enumerate(self.embeddings_data):
            if item['workflow_id'] == workflow_id:
                workflow_idx = i
                break
        
        if workflow_idx is None:
            return []
        
        # Get the workflow's embedding
        workflow_embedding = np.array(self.embeddings_data[workflow_idx]['embedding']).reshape(1, -1)
        
        # Calculate cosine similarity with all other workflows
        similarities = cosine_similarity(workflow_embedding, self.embeddings_matrix)[0]
        
        # Get top-k indices (excluding the workflow itself)
        top_indices = np.argsort(similarities)[::-1][1:top_k+1]
        
        # Format results
        results = []
        for i, idx in enumerate(top_indices):
            embedding_item = self.embeddings_data[idx]
            result_workflow_id = embedding_item['workflow_id']
            
            result = {
                'rank': i + 1,
                'score': float(similarities[idx]),
                'workflow_id': result_workflow_id,
                'filename': embedding_item['filename'],
                'name': self.workflow_ids.get(result_workflow_id, {}).get('name', 'Unknown'),
                'search_text': embedding_item['search_text'][:200] + '...' if len(embedding_item['search_text']) > 200 else embedding_item['search_text']
            }
            results.append(result)
        
        return results

def main():
    """Test the semantic search functionality."""
    print("🔍 Testing semantic search...")
    
    try:
        search = SemanticSearch()
        search.load_index()
        
        # Test search
        query = "email automation"
        print(f"\n🔎 Searching for: '{query}'")
        results = search.search(query, top_k=3)
        
        for result in results:
            print(f"  {result['rank']}. {result['name']} (Score: {result['score']:.3f})")
            print(f"     File: {result['filename']}")
            print(f"     Text: {result['search_text']}")
            print()
        
        # Test similar workflows
        if results:
            workflow_id = results[0]['workflow_id']
            print(f"🔍 Finding workflows similar to: {results[0]['name']}")
            similar = search.find_similar(workflow_id, top_k=3)
            
            for result in similar:
                print(f"  {result['rank']}. {result['name']} (Score: {result['score']:.3f})")
                print(f"     File: {result['filename']}")
                print()
        
        print("✅ Semantic search is working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure to run generate_embeddings.py first")

if __name__ == "__main__":
    main()
