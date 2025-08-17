#!/usr/bin/env python3
"""
FastAPI server for n8n workflow library
Provides REST API endpoints for searching and accessing workflows
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Import semantic search
try:
    from semantic_search import SemanticSearch
    SEMANTIC_AVAILABLE = True
except ImportError:
    SEMANTIC_AVAILABLE = False
    print("⚠️ Semantic search not available. Install dependencies: pip install sentence-transformers faiss-cpu")

app = FastAPI(
    title="n8n Workflow Library API",
    description="API for searching and accessing n8n workflows with semantic search capabilities",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize semantic search
semantic_search = None
if SEMANTIC_AVAILABLE:
    try:
        semantic_search = SemanticSearch()
        semantic_search.load_index()
        print("✅ Semantic search loaded successfully")
    except Exception as e:
        print(f"⚠️ Failed to load semantic search: {e}")

class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    filename: str
    description: Optional[str] = None
    quality_score: Optional[int] = None
    categories: List[str] = []
    integrations: List[str] = []
    node_count: Optional[int] = None
    connection_count: Optional[int] = None
    complexity: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[WorkflowResponse]
    total: int
    search_type: str

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "n8n Workflow Library API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search - Search workflows (semantic + keyword)",
            "similar": "/api/similar/{workflow_id} - Find similar workflows",
            "workflow": "/api/workflow/{filename} - Get specific workflow",
            "categories": "/api/categories - List all categories",
            "integrations": "/api/integrations - List all integrations",
            "quality": "/api/quality - Get quality rankings",
            "manifest": "/api/manifest - Get complete catalog",
            "stats": "/api/stats - Get library statistics",
            "health": "/api/health - Health check"
        },
        "semantic_search": SEMANTIC_AVAILABLE and semantic_search is not None
    }

@app.get("/api/search")
async def search_workflows(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Number of results to return"),
    search_type: str = Query("semantic", description="Search type: semantic, keyword, or hybrid")
):
    """Search workflows using semantic or keyword search."""
    try:
        if search_type == "semantic" and semantic_search:
            # Use semantic search
            results = semantic_search.search(q, top_k=limit)
            workflows = []
            
            for result in results:
                workflow_data = load_workflow_by_filename(result['filename'])
                if workflow_data:
                    workflows.append(create_workflow_response(workflow_data, result))
            
            return SearchResponse(
                query=q,
                results=workflows,
                total=len(workflows),
                search_type="semantic"
            )
        
        elif search_type == "keyword":
            # Use keyword search
            workflows = keyword_search(q, limit)
            return SearchResponse(
                query=q,
                results=workflows,
                total=len(workflows),
                search_type="keyword"
            )
        
        elif search_type == "hybrid" and semantic_search:
            # Combine semantic and keyword search
            semantic_results = semantic_search.search(q, top_k=limit//2)
            keyword_results = keyword_search(q, limit//2)
            
            # Combine and deduplicate
            combined = {}
            for result in semantic_results + keyword_results:
                workflow_id = result.get('workflow_id', result.get('filename'))
                if workflow_id not in combined:
                    combined[workflow_id] = result
            
            workflows = list(combined.values())[:limit]
            return SearchResponse(
                query=q,
                results=workflows,
                total=len(workflows),
                search_type="hybrid"
            )
        
        else:
            # Fallback to keyword search
            workflows = keyword_search(q, limit)
            return SearchResponse(
                query=q,
                results=workflows,
                total=len(workflows),
                search_type="keyword"
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/similar/{workflow_id}")
async def find_similar_workflows(
    workflow_id: str,
    limit: int = Query(5, description="Number of similar workflows to return")
):
    """Find workflows similar to a specific workflow."""
    if not semantic_search:
        raise HTTPException(status_code=503, detail="Semantic search not available")
    
    try:
        results = semantic_search.find_similar(workflow_id, top_k=limit)
        workflows = []
        
        for result in results:
            workflow_data = load_workflow_by_filename(result['filename'])
            if workflow_data:
                workflows.append(create_workflow_response(workflow_data, result))
        
        return {
            "workflow_id": workflow_id,
            "similar_workflows": workflows,
            "total": len(workflows)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar search error: {str(e)}")

@app.get("/api/workflow/{filename}")
async def get_workflow(filename: str):
    """Get a specific workflow by filename."""
    try:
        workflow_data = load_workflow_by_filename(filename)
        if not workflow_data:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return workflow_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading workflow: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """Get all available categories."""
    try:
        categories_file = Path('indexes/categories.json')
        if categories_file.exists():
            with open(categories_file, 'r') as f:
                return json.load(f)
        else:
            return {"categories": [], "message": "Categories index not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading categories: {str(e)}")

@app.get("/api/integrations")
async def get_integrations():
    """Get all available integrations."""
    try:
        integrations_file = Path('indexes/integrations.json')
        if integrations_file.exists():
            with open(integrations_file, 'r') as f:
                return json.load(f)
        else:
            return {"integrations": [], "message": "Integrations index not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading integrations: {str(e)}")

@app.get("/api/quality")
async def get_quality_rankings():
    """Get workflows ranked by quality score."""
    try:
        quality_file = Path('indexes/quality.json')
        if quality_file.exists():
            with open(quality_file, 'r') as f:
                return json.load(f)
        else:
            return {"rankings": [], "message": "Quality index not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading quality rankings: {str(e)}")

@app.get("/api/manifest")
async def get_manifest():
    """Get the complete workflow catalog."""
    try:
        manifest_file = Path('indexes/manifest.json')
        if manifest_file.exists():
            with open(manifest_file, 'r') as f:
                return json.load(f)
        else:
            return {"workflows": [], "message": "Manifest not found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading manifest: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get library statistics."""
    try:
        workflows_dir = Path('workflows')
        workflow_files = list(workflows_dir.glob('*.json'))
        
        # Calculate basic stats
        total_workflows = len(workflow_files)
        total_size = sum(f.stat().st_size for f in workflow_files)
        
        # Load categories and integrations for counts
        categories_count = 0
        integrations_count = 0
        
        categories_file = Path('indexes/categories.json')
        if categories_file.exists():
            with open(categories_file, 'r') as f:
                categories_data = json.load(f)
                categories_count = len(categories_data.get('categories', []))
        
        integrations_file = Path('indexes/integrations.json')
        if integrations_file.exists():
            with open(integrations_file, 'r') as f:
                integrations_data = json.load(f)
                integrations_count = len(integrations_data.get('integrations', []))
        
        return {
            "total_workflows": total_workflows,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "categories_count": categories_count,
            "integrations_count": integrations_count,
            "semantic_search_available": SEMANTIC_AVAILABLE and semantic_search is not None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating stats: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "semantic_search": SEMANTIC_AVAILABLE and semantic_search is not None,
        "workflows_directory": Path('workflows').exists(),
        "indexes_directory": Path('indexes').exists()
    }

def load_workflow_by_filename(filename: str) -> Optional[Dict[str, Any]]:
    """Load a workflow by filename."""
    try:
        filepath = Path('workflows') / filename
        if filepath.exists():
            with open(filepath, 'r') as f:
                return json.load(f)
        return None
    except Exception:
        return None

def keyword_search(query: str, limit: int) -> List[Dict[str, Any]]:
    """Simple keyword search through workflows."""
    workflows = []
    query_lower = query.lower()
    
    workflows_dir = Path('workflows')
    for filepath in workflows_dir.glob('*.json'):
        try:
            with open(filepath, 'r') as f:
                workflow_data = json.load(f)
                
                # Check if query matches workflow name, description, or metadata
                search_text = ""
                if 'name' in workflow_data:
                    search_text += workflow_data['name'] + " "
                if '_metadata' in workflow_data:
                    if 'description' in workflow_data['_metadata']:
                        search_text += workflow_data['_metadata']['description'] + " "
                    if 'categories' in workflow_data['_metadata']:
                        search_text += " ".join(workflow_data['_metadata']['categories']) + " "
                    if 'integrations' in workflow_data['_metadata']:
                        search_text += " ".join(workflow_data['_metadata']['integrations']) + " "
                
                if query_lower in search_text.lower():
                    workflows.append(create_workflow_response(workflow_data))
                    
                    if len(workflows) >= limit:
                        break
        except Exception:
            continue
    
    return workflows

def create_workflow_response(workflow_data: Dict[str, Any], search_result: Optional[Dict[str, Any]] = None) -> WorkflowResponse:
    """Create a standardized workflow response."""
    metadata = workflow_data.get('_metadata', {})
    
    response = WorkflowResponse(
        workflow_id=metadata.get('workflow_id', ''),
        name=workflow_data.get('name', 'Unknown'),
        filename=workflow_data.get('_filename', ''),
        description=metadata.get('description'),
        quality_score=metadata.get('quality_score'),
        categories=metadata.get('categories', []),
        integrations=metadata.get('integrations', []),
        node_count=len(workflow_data.get('nodes', [])),
        connection_count=len(workflow_data.get('connections', {})),
        complexity=metadata.get('complexity')
    )
    
    # Add search score if available
    if search_result and 'score' in search_result:
        response.__dict__['search_score'] = search_result['score']
    
    return response

if __name__ == "__main__":
    print("🚀 Starting n8n Workflow Library API...")
    print(f"🔍 Semantic search available: {SEMANTIC_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
