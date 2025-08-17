#!/usr/bin/env python3
"""
FastAPI REST API for n8n Workflow Library
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import json
import os
from pathlib import Path
from datetime import datetime

app = FastAPI(
    title="n8n Workflow Search API",
    description="Search and browse n8n workflows with metadata",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_index(filename: str) -> Dict[str, Any]:
    """Load an index file."""
    index_path = Path('indexes') / filename
    if not index_path.exists():
        raise HTTPException(status_code=404, detail=f"Index {filename} not found")
    
    with open(index_path, 'r') as f:
        return json.load(f)

def load_workflow(filename: str) -> Dict[str, Any]:
    """Load a workflow file."""
    workflow_path = Path('workflows') / filename
    if not workflow_path.exists():
        raise HTTPException(status_code=404, detail=f"Workflow {filename} not found")
    
    with open(workflow_path, 'r') as f:
        return json.load(f)

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "n8n Workflow Search API",
        "version": "1.0.0",
        "endpoints": {
            "search": "/api/search",
            "categories": "/api/categories",
            "integrations": "/api/integrations",
            "quality": "/api/quality",
            "workflow": "/api/workflow/{filename}",
            "manifest": "/api/manifest"
        },
        "docs": "/docs"
    }

@app.get("/api/search")
async def search_workflows(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    integration: Optional[str] = Query(None, description="Filter by integration"),
    complexity: Optional[str] = Query(None, description="Filter by complexity (beginner/intermediate/advanced)"),
    min_quality: Optional[int] = Query(None, description="Minimum quality score (0-100)"),
    max_nodes: Optional[int] = Query(None, description="Maximum number of nodes"),
    limit: Optional[int] = Query(50, description="Maximum number of results")
):
    """Search workflows with filters."""
    try:
        manifest = load_index("manifest.json")
        workflows = manifest.get("workflows", [])
        
        # Apply filters
        filtered_workflows = workflows
        
        # Text search
        if q:
            q_lower = q.lower()
            filtered_workflows = [
                w for w in filtered_workflows
                if (q_lower in w.get("name", "").lower() or
                    q_lower in w.get("description", "").lower() or
                    any(q_lower in cat.lower() for cat in w.get("categories", [])) or
                    any(q_lower in integ.lower() for integ in w.get("integrations", [])))
            ]
        
        # Category filter
        if category:
            filtered_workflows = [
                w for w in filtered_workflows
                if category.lower() in [cat.lower() for cat in w.get("categories", [])]
            ]
        
        # Integration filter
        if integration:
            filtered_workflows = [
                w for w in filtered_workflows
                if integration.lower() in [integ.lower() for integ in w.get("integrations", [])]
            ]
        
        # Complexity filter
        if complexity:
            filtered_workflows = [
                w for w in filtered_workflows
                if w.get("complexity", "").lower() == complexity.lower()
            ]
        
        # Quality filter
        if min_quality is not None:
            filtered_workflows = [
                w for w in filtered_workflows
                if w.get("quality_score", 0) >= min_quality
            ]
        
        # Node count filter
        if max_nodes is not None:
            filtered_workflows = [
                w for w in filtered_workflows
                if w.get("node_count", 0) <= max_nodes
            ]
        
        # Apply limit
        if limit:
            filtered_workflows = filtered_workflows[:limit]
        
        return {
            "query": {
                "search": q,
                "category": category,
                "integration": integration,
                "complexity": complexity,
                "min_quality": min_quality,
                "max_nodes": max_nodes,
                "limit": limit
            },
            "total_results": len(filtered_workflows),
            "results": filtered_workflows
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.get("/api/categories")
async def get_categories():
    """Get all categories with workflow counts."""
    try:
        categories = load_index("categories.json")
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading categories: {str(e)}")

@app.get("/api/categories/{category}")
async def get_category_workflows(category: str):
    """Get workflows for a specific category."""
    try:
        categories = load_index("categories.json")
        category_workflows = categories.get("categories", {}).get(category, [])
        
        if not category_workflows:
            raise HTTPException(status_code=404, detail=f"Category '{category}' not found")
        
        return {
            "category": category,
            "workflow_count": len(category_workflows),
            "workflows": category_workflows
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading category: {str(e)}")

@app.get("/api/integrations")
async def get_integrations():
    """Get all integrations with workflow counts."""
    try:
        integrations = load_index("integrations.json")
        return integrations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading integrations: {str(e)}")

@app.get("/api/integrations/{integration}")
async def get_integration_workflows(integration: str):
    """Get workflows for a specific integration."""
    try:
        integrations = load_index("integrations.json")
        integration_workflows = integrations.get("integrations", {}).get(integration, [])
        
        if not integration_workflows:
            raise HTTPException(status_code=404, detail=f"Integration '{integration}' not found")
        
        return {
            "integration": integration,
            "workflow_count": len(integration_workflows),
            "workflows": integration_workflows
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading integration: {str(e)}")

@app.get("/api/quality")
async def get_quality_tiers():
    """Get workflows grouped by quality tiers."""
    try:
        quality = load_index("quality.json")
        return quality
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading quality tiers: {str(e)}")

@app.get("/api/quality/{tier}")
async def get_quality_tier_workflows(tier: str):
    """Get workflows for a specific quality tier."""
    try:
        quality = load_index("quality.json")
        tier_workflows = quality.get("quality_tiers", {}).get(tier, [])
        
        if not tier_workflows:
            raise HTTPException(status_code=404, detail=f"Quality tier '{tier}' not found")
        
        return {
            "tier": tier,
            "workflow_count": len(tier_workflows),
            "workflows": tier_workflows
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading quality tier: {str(e)}")

@app.get("/api/workflow/{filename}")
async def get_workflow(filename: str):
    """Get a specific workflow by filename."""
    try:
        workflow = load_workflow(filename)
        return workflow
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading workflow: {str(e)}")

@app.get("/api/manifest")
async def get_manifest():
    """Get the complete manifest of all workflows."""
    try:
        manifest = load_index("manifest.json")
        return manifest
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading manifest: {str(e)}")

@app.get("/api/stats")
async def get_stats():
    """Get overall statistics about the workflow library."""
    try:
        manifest = load_index("manifest.json")
        categories = load_index("categories.json")
        integrations = load_index("integrations.json")
        quality = load_index("quality.json")
        
        # Calculate additional stats
        total_workflows = len(manifest.get("workflows", []))
        avg_quality = sum(w.get("quality_score", 0) for w in manifest.get("workflows", [])) / total_workflows if total_workflows > 0 else 0
        avg_nodes = sum(w.get("node_count", 0) for w in manifest.get("workflows", [])) / total_workflows if total_workflows > 0 else 0
        
        complexity_distribution = {}
        for workflow in manifest.get("workflows", []):
            complexity = workflow.get("complexity", "unknown")
            complexity_distribution[complexity] = complexity_distribution.get(complexity, 0) + 1
        
        return {
            "total_workflows": total_workflows,
            "total_categories": len(categories.get("categories", {})),
            "total_integrations": len(integrations.get("integrations", {})),
            "quality_distribution": quality.get("summary", {}),
            "complexity_distribution": complexity_distribution,
            "average_quality_score": round(avg_quality, 2),
            "average_node_count": round(avg_nodes, 2),
            "last_updated": manifest.get("generated_at", "")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading stats: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check if required directories exist
        workflows_dir = Path('workflows')
        indexes_dir = Path('indexes')
        
        workflow_count = len(list(workflows_dir.glob('*.json'))) if workflows_dir.exists() else 0
        index_count = len(list(indexes_dir.glob('*.json'))) if indexes_dir.exists() else 0
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "workflows_available": workflow_count,
            "indexes_available": index_count
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
