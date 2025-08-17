#!/usr/bin/env python3
"""
Create Sample Workflows - Generate test workflows with metadata for repository setup.
"""

import json
import os
from datetime import datetime
from pathlib import Path

def create_sample_workflow(name, description, categories, integrations, complexity, quality_score, node_count=8):
    """Create a sample workflow with metadata."""
    
    # Create sample nodes
    nodes = []
    for i in range(node_count):
        node = {
            "id": f"node-{i}",
            "name": f"Node {i+1}",
            "type": f"n8n-nodes-base.{integrations[0] if integrations else 'httpRequest'}",
            "position": [i * 200, i * 100],
            "parameters": {}
        }
        
        # Add sticky note for documentation
        if i == 0:
            node = {
                "id": f"node-{i}",
                "name": "Documentation",
                "type": "n8n-nodes-base.stickyNote",
                "position": [0, 0],
                "parameters": {
                    "content": f"# {name}\n\n{description}\n\nThis workflow demonstrates {', '.join(categories)} functionality."
                }
            }
        
        nodes.append(node)
    
    # Create sample connections
    connections = {}
    for i in range(len(nodes) - 1):
        connections[f"node-{i}"] = {
            "main": [[{"node": f"node-{i+1}", "type": "main", "index": 0}]]
        }
    
    # Create workflow data
    workflow_data = {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "pinData": {},
        "settings": {},
        "staticData": {},
        "tags": [],
        "triggerCount": 1,
        "updatedAt": datetime.now().isoformat(),
        "versionId": "1"
    }
    
    # Create metadata
    metadata = {
        "workflow_name": name,
        "scraped_at": datetime.now().isoformat(),
        "source_url": f"https://n8n.io/workflows/sample-{name.lower().replace(' ', '-')}",
        "node_count": len(nodes),
        "connection_count": len(connections),
        "has_trigger": True,
        "has_credentials": len(integrations) > 0,
        "integrations": integrations,
        "categories": categories,
        "complexity": complexity,
        "quality_score": quality_score,
        "description": description
    }
    
    # Create enhanced workflow
    enhanced_workflow = {
        "_metadata": metadata,
        **workflow_data
    }
    
    return enhanced_workflow

def main():
    """Create sample workflows for testing."""
    print("🚀 Creating Sample n8n Workflows")
    print("=" * 50)
    
    # Define sample workflows
    sample_workflows = [
        {
            "name": "Email Automation with AI",
            "description": "Automate email processing with AI-powered content analysis and response generation",
            "categories": ["ai-automation", "email-automation"],
            "integrations": ["gmail", "openai", "google-sheets"],
            "complexity": "intermediate",
            "quality_score": 85,
            "node_count": 12
        },
        {
            "name": "Slack Notification System",
            "description": "Comprehensive Slack notification system with filtering and scheduling",
            "categories": ["communication", "notifications"],
            "integrations": ["slack", "http", "cron"],
            "complexity": "beginner",
            "quality_score": 75,
            "node_count": 8
        },
        {
            "name": "Data Processing Pipeline",
            "description": "Advanced data processing pipeline with error handling and validation",
            "categories": ["data-processing", "api-integration"],
            "integrations": ["mysql", "postgres", "http"],
            "complexity": "advanced",
            "quality_score": 92,
            "node_count": 15
        },
        {
            "name": "Payment Processing Automation",
            "description": "Automated payment processing with Stripe integration and webhook handling",
            "categories": ["payment-processing", "api-integration"],
            "integrations": ["stripe", "webhook", "email"],
            "complexity": "intermediate",
            "quality_score": 88,
            "node_count": 10
        },
        {
            "name": "File Management System",
            "description": "Automated file management with Google Drive and Dropbox integration",
            "categories": ["file-management", "automation"],
            "integrations": ["gdrive", "dropbox", "s3"],
            "complexity": "beginner",
            "quality_score": 70,
            "node_count": 6
        },
        {
            "name": "AI Content Generation",
            "description": "AI-powered content generation workflow using OpenAI and Claude",
            "categories": ["ai-automation", "content-creation"],
            "integrations": ["openai", "anthropic", "notion"],
            "complexity": "advanced",
            "quality_score": 95,
            "node_count": 18
        },
        {
            "name": "Customer Support Automation",
            "description": "Automated customer support system with ticket management and responses",
            "categories": ["communication", "automation"],
            "integrations": ["zendesk", "slack", "email"],
            "complexity": "intermediate",
            "quality_score": 82,
            "node_count": 14
        },
        {
            "name": "Web Scraping Pipeline",
            "description": "Advanced web scraping pipeline with data extraction and processing",
            "categories": ["web-scraping", "data-processing"],
            "integrations": ["http", "csv", "database"],
            "complexity": "advanced",
            "quality_score": 90,
            "node_count": 16
        }
    ]
    
    # Create workflows directory if it doesn't exist
    workflows_dir = Path('workflows')
    workflows_dir.mkdir(exist_ok=True)
    
    created_count = 0
    
    for i, workflow_spec in enumerate(sample_workflows, 1):
        print(f"\n📝 [{i}/{len(sample_workflows)}] Creating: {workflow_spec['name']}")
        
        # Create the workflow
        workflow_data = create_sample_workflow(**workflow_spec)
        
        # Generate filename
        safe_name = workflow_spec['name'].replace(' ', '_').replace('-', '_')
        filename = f"{safe_name}.json"
        filepath = workflows_dir / filename
        
        # Save workflow
        with open(filepath, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        print(f"  💾 Saved: {filename}")
        print(f"  📊 Quality: {workflow_spec['quality_score']}/100")
        print(f"  🏷️  Categories: {', '.join(workflow_spec['categories'])}")
        print(f"  🔗 Integrations: {', '.join(workflow_spec['integrations'])}")
        
        created_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 Created {created_count} sample workflows!")
    print("\n🔄 Generating indexes...")
    
    # Generate indexes
    try:
        from generate_indexes import main as generate_indexes
        generate_indexes()
        print("✅ Indexes generated successfully!")
    except Exception as e:
        print(f"❌ Error generating indexes: {e}")
    
    print(f"\n📁 Total workflows: {len(list(workflows_dir.glob('*.json')))}")
    print("🚀 Ready for GitHub repository setup!")

if __name__ == "__main__":
    main()
