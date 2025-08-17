#!/usr/bin/env python3
"""
CSV-based n8n Workflow Scraper
Reads from final_consolidated.csv and scrapes workflows with proper names and popularity data
"""

import csv
import time
import json
import re
import html
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def setup_driver():
    """Setup Chrome driver."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except:
        print("❌ Chrome not found. Please install Chrome browser.")
        return None

def sanitize_filename(name):
    """Sanitize workflow name for filename."""
    # Remove special characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', name)
    sanitized = re.sub(r'[-\s]+', '_', sanitized)
    return sanitized.strip('_')

def scrape_workflow_from_url(driver, url, workflow_name, used_count):
    """Scrape a single workflow from n8n.io."""
    print(f"🔍 Scraping: {workflow_name}")
    print(f"   📊 Used by: {used_count} people")
    
    try:
        # Open the workflow page
        driver.get(url)
        time.sleep(3)
        
        # Handle cookie banner
        try:
            cookie_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Accept') or contains(text(), 'Accept All')]")
            if cookie_buttons:
                cookie_buttons[0].click()
                time.sleep(2)
        except:
            pass
        
        # Look for "Use for Free" button
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Use for free')]")
        
        if not buttons:
            print("  ❌ Could not find 'Use for Free' button")
            return None
        
        # Click the button
        driver.execute_script("arguments[0].scrollIntoView();", buttons[0])
        time.sleep(1)
        buttons[0].click()
        time.sleep(3)
        
        # Get the workflow JSON
        page_source = driver.page_source
        pattern = r'<n8n-demo[^>]*workflow="([^"]*)"[^>]*>'
        matches = re.findall(pattern, page_source)
        
        if not matches:
            print("  ❌ Could not find workflow JSON")
            return None
        
        # Parse JSON
        json_str = html.unescape(matches[0])
        workflow_data = json.loads(json_str)
        
        print(f"  ✅ Found workflow: {len(workflow_data.get('nodes', []))} nodes")
        
        # Add metadata
        if '_metadata' not in workflow_data:
            workflow_data['_metadata'] = {}
        
        workflow_data['_metadata'].update({
            'name': workflow_name,
            'used_count': int(used_count),
            'popularity_score': calculate_popularity_score(int(used_count)),
            'source_url': url,
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        })
        
        # Save with proper name
        filename = f"{sanitize_filename(workflow_name)}.json"
        
        workflows_dir = Path('workflows')
        workflows_dir.mkdir(exist_ok=True)
        
        filepath = workflows_dir / filename
        
        # Check if already exists
        if filepath.exists():
            print(f"  ⚠️ Already exists: {filename}")
            return None
        
        with open(filepath, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        print(f"  💾 Saved as: {filename}")
        return filename
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None

def calculate_popularity_score(used_count):
    """Calculate popularity score based on usage count."""
    if used_count >= 50000:
        return 100
    elif used_count >= 10000:
        return 85
    elif used_count >= 5000:
        return 70
    elif used_count >= 1000:
        return 55
    elif used_count >= 100:
        return 40
    else:
        return 25

def load_csv_data(csv_path):
    """Load workflow data from CSV."""
    workflows = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                workflows.append({
                    'name': row['Name'].strip(),
                    'url': row['URL'].strip(),
                    'used_count': int(row['Used'])
                })
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []
    
    return workflows

def main():
    """Main function."""
    print("🚀 CSV-based n8n Workflow Scraper")
    print("=" * 50)
    
    # Load CSV data
    csv_path = Path.home() / 'Downloads' / 'final_consolidated.csv'
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        return
    
    workflows = load_csv_data(csv_path)
    print(f"📊 Loaded {len(workflows)} workflows from CSV")
    
    if not workflows:
        print("❌ No workflows found in CSV")
        return
    
    # Sort by popularity (used count)
    workflows.sort(key=lambda x: x['used_count'], reverse=True)
    
    # Show top workflows
    print(f"\n🏆 Top 10 most popular workflows:")
    for i, workflow in enumerate(workflows[:10], 1):
        print(f"  {i}. {workflow['name']} ({workflow['used_count']} users)")
    
    # Ask user how many to scrape
    try:
        max_workflows = int(input(f"\n📋 How many workflows to scrape? (1-{len(workflows)}): "))
        max_workflows = min(max_workflows, len(workflows))
    except ValueError:
        max_workflows = 5
        print(f"📋 Using default: {max_workflows} workflows")
    
    # Setup driver
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # Scrape workflows
        print(f"\n🔄 Starting to scrape {max_workflows} workflows...")
        scraped_count = 0
        
        for i, workflow in enumerate(workflows[:max_workflows], 1):
            print(f"\n--- Workflow {i}/{max_workflows} ---")
            result = scrape_workflow_from_url(
                driver, 
                workflow['url'], 
                workflow['name'], 
                workflow['used_count']
            )
            
            if result:
                scraped_count += 1
            
            # Random delay between scrapes (human-like)
            if i < max_workflows:
                delay = random.uniform(3, 8)
                print(f"⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        print(f"\n🎉 Completed! Scraped {scraped_count}/{max_workflows} workflows")
        
        if scraped_count > 0:
            print("\n💡 Next steps:")
            print("   1. Run: python3 scripts/generate_embeddings.py")
            print("   2. Run: python3 scripts/generate_indexes.py")
            print("   3. Commit and push to GitHub")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
