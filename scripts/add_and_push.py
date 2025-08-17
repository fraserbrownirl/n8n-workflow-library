#!/usr/bin/env python3
"""
Add and Push - Scrapes one workflow and pushes it to GitHub automatically.
"""

import subprocess
import time
import random
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed")
            return True
        else:
            print(f"❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} error: {e}")
        return False

def add_and_push_workflow(workflow_url=None):
    """Scrape one workflow and push to GitHub."""
    print("🚀 Add and Push Workflow")
    print("=" * 50)
    
    # Step 1: Scrape the workflow
    if workflow_url:
        print(f"🔍 Scraping workflow: {workflow_url}")
        success = run_command(
            f"python3 scripts/single_scraper.py --url '{workflow_url}'",
            "Scraping workflow"
        )
    else:
        print("🔍 Starting interactive scraper...")
        success = run_command(
            "python3 scripts/single_scraper.py",
            "Scraping workflow"
        )
    
    if not success:
        print("❌ Workflow scraping failed")
        return False
    
    # Step 2: Check if new files were added
    print("\n📊 Checking for new workflows...")
    workflows_before = set(Path('workflows').glob('*.json'))
    
    # Wait a moment for file system
    time.sleep(2)
    
    workflows_after = set(Path('workflows').glob('*.json'))
    new_workflows = workflows_after - workflows_before
    
    if not new_workflows:
        print("⚠️  No new workflows were added")
        return False
    
    print(f"✅ Found {len(new_workflows)} new workflow(s):")
    for workflow in new_workflows:
        print(f"  📄 {workflow.name}")
    
    # Step 3: Add files to git
    success = run_command("git add workflows/ indexes/", "Adding files to git")
    if not success:
        return False
    
    # Step 4: Commit
    workflow_names = [w.stem for w in new_workflows]
    commit_message = f"📦 Add workflow(s): {', '.join(workflow_names)}"
    success = run_command(f'git commit -m "{commit_message}"', "Committing changes")
    if not success:
        return False
    
    # Step 5: Push to GitHub
    success = run_command("git push origin main", "Pushing to GitHub")
    if not success:
        return False
    
    print("\n🎉 SUCCESS!")
    print(f"✅ Added {len(new_workflows)} workflow(s) to GitHub")
    print(f"📍 Repository: https://github.com/fraserbrownirl/n8n-workflow-library")
    
    return True

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Add workflow and push to GitHub')
    parser.add_argument('--url', type=str, help='Specific workflow URL to scrape')
    parser.add_argument('--auto', action='store_true', help='Run automatically without prompts')
    
    args = parser.parse_args()
    
    if args.auto:
        # Automatic mode
        success = add_and_push_workflow(args.url)
        if success:
            print("\n✅ Workflow added and pushed successfully!")
        else:
            print("\n❌ Failed to add workflow.")
    else:
        # Interactive mode
        print("🚀 Add and Push Workflow")
        print("=" * 50)
        print("This will:")
        print("1. Scrape one workflow")
        print("2. Add it to git")
        print("3. Commit the changes")
        print("4. Push to GitHub")
        print("")
        
        if args.url:
            print(f"📋 Using URL: {args.url}")
            proceed = input("Proceed? (y/n): ")
        else:
            print("📋 Will use interactive scraper")
            proceed = input("Proceed? (y/n): ")
        
        if proceed.lower() in ['y', 'yes']:
            success = add_and_push_workflow(args.url)
            if success:
                print("\n✅ Workflow added and pushed successfully!")
            else:
                print("\n❌ Failed to add workflow.")
        else:
            print("👋 Cancelled.")

if __name__ == "__main__":
    main()
