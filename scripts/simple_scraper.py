#!/usr/bin/env python3
"""
Simple Human-like n8n Scraper
Just opens the page, clicks "Use for Free", and gets the JSON.
"""

import time
import json
import re
import html
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def setup_simple_driver():
    """Simple Chrome setup - like a human would use."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Use existing Chrome driver if available
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except:
        print("❌ Chrome not found. Please install Chrome browser.")
        return None

def get_workflow_name_from_url(url):
    """Get workflow name from URL - simple approach."""
    # Extract from URL like: .../5678-automate-email-filtering-and-ai-summarization-100percent-free-and-effective-works-724/
    parts = url.split('/')
    if len(parts) > 2:
        last_part = parts[-2] if parts[-1] == "" else parts[-1]
        # Convert to readable name
        name = last_part.replace('-', ' ').title()
        # Remove numbers at start
        name = re.sub(r'^\d+\s*', '', name)
        return name
    return "Workflow"

def scrape_workflow(url):
    """Simple workflow scraping - like a human would do."""
    print(f"🔍 Scraping: {url}")
    
    driver = setup_simple_driver()
    if not driver:
        return None
    
    try:
        # 1. Open the page (like a human)
        print("  📄 Opening page...")
        driver.get(url)
        time.sleep(3)  # Wait like a human
        
        # 2. Handle cookie banner (like a human would)
        print("  🍪 Checking for cookie banner...")
        try:
            cookie_buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Accept') or contains(text(), 'Accept All') or contains(text(), 'OK')]")
            if cookie_buttons:
                print("  ✅ Found cookie banner, accepting...")
                cookie_buttons[0].click()
                time.sleep(2)
        except:
            pass  # No cookie banner
        
        # 3. Look for "Use for Free" button
        print("  🔍 Looking for 'Use for Free' button...")
        buttons = driver.find_elements(By.XPATH, "//*[contains(text(), 'Use for free')]")
        
        if not buttons:
            print("  ❌ Could not find 'Use for Free' button")
            return None
        
        # 4. Scroll to button and click (like a human)
        print("  ✅ Found button, scrolling and clicking...")
        driver.execute_script("arguments[0].scrollIntoView();", buttons[0])
        time.sleep(1)
        buttons[0].click()
        time.sleep(3)  # Wait for modal
        
        # 5. Get the page source and find JSON
        print("  📋 Getting workflow JSON...")
        page_source = driver.page_source
        
        # Look for the workflow JSON in the n8n-demo component
        pattern = r'<n8n-demo[^>]*workflow="([^"]*)"[^>]*>'
        matches = re.findall(pattern, page_source)
        
        if not matches:
            print("  ❌ Could not find workflow JSON")
            return None
        
        # 6. Extract and parse JSON
        json_str = html.unescape(matches[0])
        workflow_data = json.loads(json_str)
        
        print(f"  ✅ Found workflow: {len(workflow_data.get('nodes', []))} nodes")
        
        # 7. Get workflow name
        workflow_name = get_workflow_name_from_url(url)
        filename = f"{workflow_name.replace(' ', '_')}.json"
        
        # 8. Save the workflow
        workflows_dir = Path('workflows')
        workflows_dir.mkdir(exist_ok=True)
        
        filepath = workflows_dir / filename
        with open(filepath, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        print(f"  💾 Saved as: {filename}")
        return filename
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return None
    finally:
        driver.quit()

def main():
    """Main function."""
    print("🚀 Simple n8n Workflow Scraper")
    print("=" * 40)
    
    # Test with the workflow we know works
    url = "https://n8n.io/workflows/5678-automate-email-filtering-and-ai-summarization-100percent-free-and-effective-works-724/"
    
    result = scrape_workflow(url)
    
    if result:
        print(f"\n🎉 Success! Saved: {result}")
        print("💡 Run this script again to scrape another workflow.")
    else:
        print("\n❌ Failed to scrape workflow.")

if __name__ == "__main__":
    main()
