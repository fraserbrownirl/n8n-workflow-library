#!/usr/bin/env python3
"""
Generate embeddings for semantic search
Creates vector embeddings for all workflows using TF-IDF approach
"""

import json
import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import jsonlines
from tqdm import tqdm
from slugify import slugify

def load_workflows() -> List[Dict[str, Any]]:
    """Load all workflows from the workflows directory."""
    workflows_dir = Path('workflows')
    workflows = []
    
    for file_path in workflows_dir.glob('*.json'):
        try:
            with open(file_path, 'r') as f:
                workflow_data = json.load(f)
                workflow_data['_filename'] = file_path.name
                workflows.append(workflow_data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return workflows

def create_search_text(workflow: Dict[str, Any]) -> str:
    """Create searchable text from workflow data."""
    text_parts = []
    
    # Add workflow name
    if 'name' in workflow:
        text_parts.append(workflow['name'])
    
    # Add metadata description
    if '_metadata' in workflow and 'description' in workflow['_metadata']:
        text_parts.append(workflow['_metadata']['description'])
    
    # Add node names and types
    if 'nodes' in workflow:
        for node in workflow['nodes']:
            if 'name' in node:
                text_parts.append(node['name'])
            if 'type' in node:
                text_parts.append(node['type'])
    
    # Add integrations
    if '_metadata' in workflow and 'integrations' in workflow['_metadata']:
        text_parts.extend(workflow['_metadata']['integrations'])
    
    # Add categories
    if '_metadata' in workflow and 'categories' in workflow['_metadata']:
        text_parts.extend(workflow['_metadata']['categories'])
    
    return ' '.join(text_parts)

def generate_persistent_id(workflow: Dict[str, Any]) -> str:
    """Generate a persistent ID for the workflow."""
    # Use filename as base for consistency
    filename = workflow.get('_filename', '')
    if filename:
        # Create a hash from filename
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, filename))
    else:
        return str(uuid.uuid4())

def generate_embeddings():
    """Generate embeddings for all workflows using TF-IDF."""
    print("🚀 Generating embeddings for semantic search...")
    
    # Load workflows
    workflows = load_workflows()
    print(f"📊 Loaded {len(workflows)} workflows")
    
    if not workflows:
        print("❌ No workflows found")
        return
    
    # Prepare data for embedding
    search_texts = []
    workflow_ids = []
    workflow_data = []
    
    print("📝 Preparing workflow data...")
    for workflow in tqdm(workflows, desc="Processing workflows"):
        # Generate persistent ID
        workflow_id = generate_persistent_id(workflow)
        
        # Add persistent ID to metadata
        if '_metadata' not in workflow:
            workflow['_metadata'] = {}
        workflow['_metadata']['workflow_id'] = workflow_id
        
        # Create searchable text
        search_text = create_search_text(workflow)
        
        search_texts.append(search_text)
        workflow_ids.append(workflow_id)
        workflow_data.append(workflow)
    
    # Generate TF-IDF embeddings
    print("🔍 Generating TF-IDF embeddings...")
    vectorizer = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.9
    )
    
    # Fit and transform the text data
    tfidf_matrix = vectorizer.fit_transform(search_texts)
    
    # Convert to dense array for storage
    embeddings = tfidf_matrix.toarray()
    
    print(f"✅ Generated embeddings with {embeddings.shape[1]} features")
    
    # Save embeddings and metadata
    print("💾 Saving embeddings and metadata...")
    indexes_dir = Path('indexes')
    indexes_dir.mkdir(exist_ok=True)
    
    # Save TF-IDF vectorizer
    import pickle
    with open(indexes_dir / 'tfidf_vectorizer.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    # Save embeddings metadata
    embeddings_data = []
    for i, (workflow_id, search_text, embedding) in enumerate(zip(workflow_ids, search_texts, embeddings)):
        embeddings_data.append({
            'workflow_id': workflow_id,
            'filename': workflow_data[i]['_filename'],
            'search_text': search_text,
            'embedding': embedding.tolist()
        })
    
    with jsonlines.open(indexes_dir / 'embeddings.jsonl', 'w') as writer:
        for item in embeddings_data:
            writer.write(item)
    
    # Save workflow ID mappings
    workflow_id_mappings = {
        workflow_id: {
            'filename': workflow['_filename'],
            'name': workflow.get('name', 'Unknown'),
            'search_text': search_text
        }
        for workflow_id, workflow, search_text in zip(workflow_ids, workflow_data, search_texts)
    }
    
    with open(indexes_dir / 'workflow_ids.json', 'w') as f:
        json.dump(workflow_id_mappings, f, indent=2)
    
    # Update workflows with persistent IDs
    print("📝 Updating workflows with persistent IDs...")
    for workflow in workflows:
        filename = workflow['_filename']
        filepath = Path('workflows') / filename
        with open(filepath, 'w') as f:
            json.dump(workflow, f, indent=2)
    
    print(f"✅ Generated embeddings for {len(workflows)} workflows")
    print(f"📁 Saved to: indexes/tfidf_vectorizer.pkl, indexes/embeddings.jsonl, indexes/workflow_ids.json")

if __name__ == "__main__":
    generate_embeddings()
