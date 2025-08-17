#!/usr/bin/env python3
"""
Test script to verify the n8n workflow library setup
"""

import json
import os
from pathlib import Path

def test_structure():
    """Test the repository structure."""
    print("🔍 Testing Repository Structure...")
    
    required_dirs = ['workflows', 'indexes', 'scripts', '.github/workflows']
    required_files = [
        'scripts/scrape_workflows.py',
        'scripts/generate_indexes.py', 
        'scripts/api.py',
        'openapi.yaml',
        'README.md',
        'requirements.txt',
        '.github/workflows/scrape.yml'
    ]
    
    all_good = True
    
    # Check directories
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ (missing)")
            all_good = False
    
    # Check files
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
            all_good = False
    
    return all_good

def test_workflows():
    """Test workflow files."""
    print("\n📁 Testing Workflows...")
    
    workflows_dir = Path('workflows')
    if not workflows_dir.exists():
        print("  ❌ workflows/ directory not found")
        return False
    
    workflow_files = list(workflows_dir.glob('*.json'))
    print(f"  📊 Found {len(workflow_files)} workflow files")
    
    for workflow_file in workflow_files:
        try:
            with open(workflow_file, 'r') as f:
                data = json.load(f)
            
            # Check if it has metadata (enhanced workflow)
            if '_metadata' in data:
                metadata = data['_metadata']
                print(f"  ✅ {workflow_file.name} - Enhanced (Quality: {metadata.get('quality_score', 'N/A')})")
            else:
                print(f"  ⚠️  {workflow_file.name} - Basic (no metadata)")
                
        except Exception as e:
            print(f"  ❌ {workflow_file.name} - Error: {e}")
    
    return len(workflow_files) > 0

def test_indexes():
    """Test index files."""
    print("\n📊 Testing Indexes...")
    
    indexes_dir = Path('indexes')
    if not indexes_dir.exists():
        print("  ❌ indexes/ directory not found")
        return False
    
    index_files = ['manifest.json', 'categories.json', 'quality.json', 'integrations.json']
    all_good = True
    
    for index_file in index_files:
        file_path = indexes_dir / index_file
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"  ✅ {index_file} - Valid JSON")
            except Exception as e:
                print(f"  ❌ {index_file} - Invalid JSON: {e}")
                all_good = False
        else:
            print(f"  ❌ {index_file} - Missing")
            all_good = False
    
    return all_good

def test_scripts():
    """Test script files."""
    print("\n🔧 Testing Scripts...")
    
    scripts_dir = Path('scripts')
    if not scripts_dir.exists():
        print("  ❌ scripts/ directory not found")
        return False
    
    script_files = ['scrape_workflows.py', 'generate_indexes.py', 'api.py']
    all_good = True
    
    for script_file in script_files:
        file_path = scripts_dir / script_file
        if file_path.exists():
            print(f"  ✅ {script_file}")
        else:
            print(f"  ❌ {script_file} - Missing")
            all_good = False
    
    return all_good

def test_github_action():
    """Test GitHub Action configuration."""
    print("\n🤖 Testing GitHub Action...")
    
    action_file = Path('.github/workflows/scrape.yml')
    if not action_file.exists():
        print("  ❌ GitHub Action not found")
        return False
    
    try:
        with open(action_file, 'r') as f:
            content = f.read()
        
        # Check for key features
        features = [
            'workflow_dispatch',
            'manual trigger',
            'deduplication',
            'index generation'
        ]
        
        for feature in features:
            if feature in content.lower():
                print(f"  ✅ {feature}")
            else:
                print(f"  ⚠️  {feature} - Not found")
        
        return True
    except Exception as e:
        print(f"  ❌ Error reading action: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing n8n Workflow Library Setup")
    print("=" * 50)
    
    tests = [
        ("Structure", test_structure),
        ("Workflows", test_workflows),
        ("Indexes", test_indexes),
        ("Scripts", test_scripts),
        ("GitHub Action", test_github_action)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Your n8n workflow library is ready!")
        print("\n📋 Next steps:")
        print("  1. Create GitHub repository")
        print("  2. Push this code: git remote add origin <your-repo-url>")
        print("  3. git push -u origin main")
        print("  4. Test the GitHub Action manually")
        print("  5. Start the API: python3 scripts/api.py")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()
