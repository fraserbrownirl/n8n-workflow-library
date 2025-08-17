#!/usr/bin/env python3
"""
Index Generator - Creates searchable indexes from workflow metadata.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

def load_workflows():
    """Load all workflows from the workflows directory."""
    workflows_dir = Path('workflows')
    workflows = []
    
    if not workflows_dir.exists():
        print("❌ Workflows directory not found")
        return workflows
    
    for file in workflows_dir.glob('*.json'):
        try:
            with open(file, 'r') as f:
                workflow_data = json.load(f)
                workflows.append(workflow_data)
        except Exception as e:
            print(f"❌ Error loading {file}: {e}")
    
    print(f"✅ Loaded {len(workflows)} workflows")
    return workflows

def generate_manifest(workflows):
    """Generate manifest.json - master catalog of all workflows."""
    manifest = {
        "generated_at": datetime.now().isoformat(),
        "total_workflows": len(workflows),
        "workflows": []
    }
    
    for workflow in workflows:
        metadata = workflow.get('_metadata', {})
        manifest_entry = {
            "filename": f"{metadata.get('workflow_name', 'Unknown')}.json",
            "name": metadata.get('workflow_name', 'Unknown'),
            "description": metadata.get('description', ''),
            "categories": metadata.get('categories', []),
            "integrations": metadata.get('integrations', []),
            "complexity": metadata.get('complexity', 'unknown'),
            "quality_score": metadata.get('quality_score', 0),
            "node_count": metadata.get('node_count', 0),
            "connection_count": metadata.get('connection_count', 0),
            "scraped_at": metadata.get('scraped_at', ''),
            "source_url": metadata.get('source_url', '')
        }
        manifest["workflows"].append(manifest_entry)
    
    # Sort by quality score (highest first)
    manifest["workflows"].sort(key=lambda x: x["quality_score"], reverse=True)
    
    return manifest

def generate_categories_index(workflows):
    """Generate categories.json - workflows grouped by category."""
    categories = defaultdict(list)
    
    for workflow in workflows:
        metadata = workflow.get('_metadata', {})
        workflow_categories = metadata.get('categories', ['general'])
        
        for category in workflow_categories:
            categories[category].append({
                "filename": f"{metadata.get('workflow_name', 'Unknown')}.json",
                "name": metadata.get('workflow_name', 'Unknown'),
                "description": metadata.get('description', ''),
                "quality_score": metadata.get('quality_score', 0),
                "complexity": metadata.get('complexity', 'unknown'),
                "node_count": metadata.get('node_count', 0)
            })
    
    # Sort workflows within each category by quality score
    for category in categories:
        categories[category].sort(key=lambda x: x["quality_score"], reverse=True)
    
    # Convert to regular dict and add metadata
    result = {
        "generated_at": datetime.now().isoformat(),
        "total_categories": len(categories),
        "categories": dict(categories)
    }
    
    return result

def generate_quality_index(workflows):
    """Generate quality.json - workflows ranked by quality score."""
    quality_tiers = {
        "excellent": [],
        "good": [],
        "fair": [],
        "basic": []
    }
    
    for workflow in workflows:
        metadata = workflow.get('_metadata', {})
        quality_score = metadata.get('quality_score', 0)
        
        entry = {
            "filename": f"{metadata.get('workflow_name', 'Unknown')}.json",
            "name": metadata.get('workflow_name', 'Unknown'),
            "description": metadata.get('description', ''),
            "categories": metadata.get('categories', []),
            "complexity": metadata.get('complexity', 'unknown'),
            "node_count": metadata.get('node_count', 0)
        }
        
        if quality_score >= 80:
            quality_tiers["excellent"].append(entry)
        elif quality_score >= 60:
            quality_tiers["good"].append(entry)
        elif quality_score >= 40:
            quality_tiers["fair"].append(entry)
        else:
            quality_tiers["basic"].append(entry)
    
    # Sort within each tier by quality score
    for tier in quality_tiers:
        quality_tiers[tier].sort(key=lambda x: x.get("quality_score", 0), reverse=True)
    
    result = {
        "generated_at": datetime.now().isoformat(),
        "quality_tiers": quality_tiers,
        "summary": {
            "excellent": len(quality_tiers["excellent"]),
            "good": len(quality_tiers["good"]),
            "fair": len(quality_tiers["fair"]),
            "basic": len(quality_tiers["basic"])
        }
    }
    
    return result

def generate_integrations_index(workflows):
    """Generate integrations.json - workflows grouped by integration."""
    integrations = defaultdict(list)
    integration_stats = Counter()
    
    for workflow in workflows:
        metadata = workflow.get('_metadata', {})
        workflow_integrations = metadata.get('integrations', [])
        
        for integration in workflow_integrations:
            integrations[integration].append({
                "filename": f"{metadata.get('workflow_name', 'Unknown')}.json",
                "name": metadata.get('workflow_name', 'Unknown'),
                "description": metadata.get('description', ''),
                "categories": metadata.get('categories', []),
                "quality_score": metadata.get('quality_score', 0),
                "complexity": metadata.get('complexity', 'unknown')
            })
            integration_stats[integration] += 1
    
    # Sort workflows within each integration by quality score
    for integration in integrations:
        integrations[integration].sort(key=lambda x: x["quality_score"], reverse=True)
    
    # Convert to regular dict and add metadata
    result = {
        "generated_at": datetime.now().isoformat(),
        "total_integrations": len(integrations),
        "integration_stats": dict(integration_stats),
        "integrations": dict(integrations)
    }
    
    return result

def save_index(index_data, filename):
    """Save index to JSON file."""
    indexes_dir = Path('indexes')
    indexes_dir.mkdir(exist_ok=True)
    
    filepath = indexes_dir / filename
    with open(filepath, 'w') as f:
        json.dump(index_data, f, indent=2)
    
    print(f"💾 Saved {filename}")

def main():
    """Main function to generate all indexes."""
    print("🚀 Generating n8n Workflow Indexes")
    print("=" * 50)
    
    # Load all workflows
    workflows = load_workflows()
    
    if not workflows:
        print("❌ No workflows found to index")
        return
    
    # Generate indexes
    print("\n📊 Generating indexes...")
    
    # 1. Manifest (master catalog)
    print("  📋 Generating manifest.json...")
    manifest = generate_manifest(workflows)
    save_index(manifest, "manifest.json")
    
    # 2. Categories index
    print("  🏷️  Generating categories.json...")
    categories = generate_categories_index(workflows)
    save_index(categories, "categories.json")
    
    # 3. Quality index
    print("  ⭐ Generating quality.json...")
    quality = generate_quality_index(workflows)
    save_index(quality, "quality.json")
    
    # 4. Integrations index
    print("  🔗 Generating integrations.json...")
    integrations = generate_integrations_index(workflows)
    save_index(integrations, "integrations.json")
    
    # Print summary
    print(f"\n📈 Index Summary:")
    print(f"  - Total workflows: {len(workflows)}")
    print(f"  - Categories: {len(categories['categories'])}")
    print(f"  - Integrations: {len(integrations['integrations'])}")
    print(f"  - Quality tiers: {quality['summary']}")
    
    print("\n🎉 All indexes generated successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
