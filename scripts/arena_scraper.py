#!/usr/bin/env python3
"""
n8nArena Scraper
1. Opens n8nArena.com
2. Sorts workflows by newest
3. Gets all workflow links
4. Scrapes each workflow from n8n.io
"""

import time
import json
import re
import html
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

def get_workflow_links_from_arena(driver, max_workflows=10):
    """Get workflow links from n8nArena.com sorted by newest."""
    print("🌐 Opening n8nArena.com/workflows...")
    driver.get("https://n8narena.com/workflows/")
    time.sleep(3)
    
    # Handle cookie banner if present
    try:
        cookie_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Accept') or contains(text(), 'Accept All')]")
        if cookie_buttons:
            print("🍪 Accepting cookies...")
            cookie_buttons[0].click()
            time.sleep(2)
    except:
        pass
    
    # Look for sort options - try to sort by newest
    print("📅 Looking for sort options...")
    try:
        # Look for sort dropdown or buttons
        sort_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Newest') or contains(text(), 'Latest') or contains(text(), 'Date') or contains(text(), 'Creation')]")
        if sort_elements:
            print("✅ Found sort option, clicking...")
            sort_elements[0].click()
            time.sleep(2)
    except:
        print("⚠️ Could not find sort option, continuing...")
    
    # Get all workflow links from the table
    print("🔗 Collecting workflow links from table...")
    workflow_links = []
    
    # Look for links in the table - specifically in the Workflow Name column
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"🔍 Found {len(links)} total links on page")
    
    for link in links:
        href = link.get_attribute("href")
        if href:
            print(f"  Link: {href}")
            if "n8n.io/workflows/" in href:
                workflow_links.append(href)
    
    print(f"📊 Found {len(workflow_links)} workflow links")
    
    # If no n8n.io links found, try looking for table rows
    if not workflow_links:
        print("🔍 Looking for table rows with workflow data...")
        try:
            # Look for table rows that might contain workflow links
            rows = driver.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 3:  # Workflow Name is typically the 3rd column
                    workflow_cell = cells[2]  # Index 2 for Workflow Name column
                    cell_links = workflow_cell.find_elements(By.TAG_NAME, "a")
                    for cell_link in cell_links:
                        href = cell_link.get_attribute("href")
                        if href and "n8n.io/workflows/" in href:
                            print(f"  Found workflow link in table: {href}")
                            workflow_links.append(href)
        except Exception as e:
            print(f"  Error looking in table: {e}")
    
    print(f"📊 After table search: {len(workflow_links)} workflow links")
    
    # Limit to max_workflows
    if len(workflow_links) > max_workflows:
        workflow_links = workflow_links[:max_workflows]
        print(f"📋 Limiting to {max_workflows} workflows")
    
    return workflow_links

def get_workflow_name_from_url(url):
    """Get workflow name from URL."""
    # Handle URLs like https://n8n.io/workflows/7328-generate-videos-from-text-prompts-using-gpt-5-and-google-veo-3
    if "/workflows/" in url:
        workflow_part = url.split("/workflows/")[-1].split("/")[0]
        
        # If it's a descriptive URL (contains dashes and text), extract the name
        if "-" in workflow_part and not workflow_part.isdigit():
            # Remove the ID at the start (e.g., "7328-")
            name_part = workflow_part.split("-", 1)[1] if "-" in workflow_part else workflow_part
            # Convert dashes to spaces and title case
            name = name_part.replace('-', ' ').title()
            return name
        else:
            # For numeric IDs, create a descriptive name
            return f"Workflow_{workflow_part}"
    return "Workflow"

def scrape_single_workflow(driver, url):
    """Scrape a single workflow from n8n.io."""
    print(f"🔍 Scraping: {url}")
    
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
        
        # Try to get the workflow name from the page header first
        workflow_name = None
        try:
            # Look for h1 tags or main headers
            headers = driver.find_elements(By.TAG_NAME, "h1")
            if headers:
                workflow_name = headers[0].text.strip()
                print(f"  📝 Found name in header: {workflow_name}")
        except:
            pass
        
        # If no header found, use URL
        if not workflow_name:
            workflow_name = get_workflow_name_from_url(url)
            print(f"  📝 Using name from URL: {workflow_name}")
        
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
        
        # Save with proper name
        filename = f"{workflow_name.replace(' ', '_').replace('/', '_').replace(':', '_')}.json"
        
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

def main():
    """Main function."""
    print("🚀 n8nArena Workflow Scraper")
    print("=" * 40)
    
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # Step 1-3: Get workflow links from n8nArena
        workflow_links = get_workflow_links_from_arena(driver, max_workflows=5)
        
        if not workflow_links:
            print("❌ No workflow links found")
            return
        
        print(f"\n📋 Found {len(workflow_links)} workflows to scrape:")
        for i, link in enumerate(workflow_links, 1):
            print(f"  {i}. {link}")
        
        # Step 4-6: Scrape each workflow
        print(f"\n🔄 Starting to scrape {len(workflow_links)} workflows...")
        scraped_count = 0
        
        for i, link in enumerate(workflow_links, 1):
            print(f"\n--- Workflow {i}/{len(workflow_links)} ---")
            result = scrape_single_workflow(driver, link)
            
            if result:
                scraped_count += 1
            
            # Random delay between scrapes (human-like)
            if i < len(workflow_links):
                delay = random.uniform(3, 8)
                print(f"⏳ Waiting {delay:.1f} seconds...")
                time.sleep(delay)
        
        print(f"\n🎉 Completed! Scraped {scraped_count}/{len(workflow_links)} workflows")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
