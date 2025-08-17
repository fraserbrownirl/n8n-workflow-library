#!/usr/bin/env python3
"""
Single Workflow Scraper - Scrapes one workflow at a time with random delays.
Safe and respectful approach to avoid rate limiting.
"""

import time
import json
import random
import os
import requests
import zipfile
import html
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Import functions from the main scraper
from scrape_workflows import (
    download_chrome_driver, setup_driver, extract_workflow_json_from_page,
    extract_metadata_from_workflow, sanitize_filename, get_existing_workflows
)

def get_next_workflow_url():
    """Get the next workflow URL to scrape."""
    # For now, we'll use a predefined list
    # In the future, you could scrape n8nArena.com for the latest workflows
    
    workflow_urls = [
        "https://n8n.io/workflows/5678-automate-email-filtering-and-ai-summarization-100percent-free-and-effective-works-724/",
        "https://n8n.io/workflows/1234-slack-notification-automation/",
        "https://n8n.io/workflows/5678-data-processing-pipeline/",
        "https://n8n.io/workflows/9012-ai-content-generation/",
        "https://n8n.io/workflows/3456-payment-processing-automation/",
        "https://n8n.io/workflows/7890-customer-support-automation/",
        "https://n8n.io/workflows/2345-file-management-system/",
        "https://n8n.io/workflows/6789-web-scraping-pipeline/",
        "https://n8n.io/workflows/0123-email-marketing-automation/",
        "https://n8n.io/workflows/4567-social-media-automation/"
    ]
    
    # You can add more URLs here or implement dynamic discovery
    return workflow_urls

def scrape_single_workflow(workflow_url, min_delay=8, max_delay=15):
    """Scrape a single workflow with random delay."""
    print(f"🔍 Scraping single workflow: {workflow_url}")
    print("=" * 60)
    
    # Get existing workflows for deduplication
    existing_workflows = get_existing_workflows()
    print(f"📊 Found {len(existing_workflows)} existing workflows")
    
    driver = None
    try:
        driver = setup_driver()
        
        # Navigate to the workflow page
        print("  📄 Loading workflow page...")
        driver.get(workflow_url)
        
        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Wait for dynamic content
        time.sleep(3)
        
        # Look for "Use for free" button
        button_selectors = [
            "//*[contains(text(), 'Use for free')]",
            "//button[contains(text(), 'Use for free')]",
            "//a[contains(text(), 'Use for free')]"
        ]
        
        button_found = False
        for selector in button_selectors:
            try:
                buttons = driver.find_elements(By.XPATH, selector)
                if buttons:
                    print(f"  ✅ Found 'Use for free' button")
                    
                    # Scroll to button
                    driver.execute_script("arguments[0].scrollIntoView();", buttons[0])
                    time.sleep(2)
                    
                    # Click the button
                    buttons[0].click()
                    print("  ✅ Clicked 'Use for Free' button!")
                    button_found = True
                    break
            except Exception as e:
                continue
        
        if not button_found:
            print("  ❌ Could not find 'Use for Free' button")
            return False
        
        # Wait for the modal to appear and workflow JSON to load
        time.sleep(5)
        
        # Extract the workflow JSON
        workflow_data = extract_workflow_json_from_page(driver)
        
        if workflow_data:
            # Extract metadata
            metadata = extract_metadata_from_workflow(workflow_data, workflow_url)
            
            # Create enhanced workflow with metadata
            enhanced_workflow = {
                "_metadata": metadata,
                **workflow_data  # Original workflow data unchanged
            }
            
            # Generate filename
            workflow_name = metadata['workflow_name']
            safe_name = sanitize_filename(workflow_name)
            filename = f"{safe_name}.json"
            
            # Check for duplicates
            if safe_name in existing_workflows:
                print(f"  ⚠️  Workflow already exists: {filename}")
                return False
            
            # Save workflow
            filepath = Path('workflows') / filename
            with open(filepath, 'w') as f:
                json.dump(enhanced_workflow, f, indent=2)
            
            print(f"  💾 Saved workflow to {filename}")
            
            # Show workflow details
            print(f"  📊 Details: {metadata['node_count']} nodes, {metadata['connection_count']} connections")
            print(f"  🏷️  Categories: {', '.join(metadata['categories'])}")
            print(f"  🔗 Integrations: {', '.join(metadata['integrations'])}")
            print(f"  ⭐ Quality Score: {metadata['quality_score']}/100")
            
            # Generate indexes
            print("  🔄 Updating indexes...")
            try:
                from generate_indexes import main as generate_indexes
                generate_indexes()
                print("  ✅ Indexes updated!")
            except Exception as e:
                print(f"  ❌ Error updating indexes: {e}")
            
            print(f"\n🎉 SUCCESS: Added workflow '{workflow_name}'!")
            return True
            
        else:
            print("  ❌ Could not extract workflow JSON")
            return False
            
    except Exception as e:
        print(f"  ❌ Error scraping workflow: {e}")
        return False
    finally:
        if driver:
            driver.quit()
    
    return False

def main():
    """Main function for single workflow scraping."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Scrape a single n8n workflow')
    parser.add_argument('--url', type=str, help='Specific workflow URL to scrape')
    parser.add_argument('--min-delay', type=int, default=8, help='Minimum delay between scrapes (seconds)')
    parser.add_argument('--max-delay', type=int, default=15, help='Maximum delay between scrapes (seconds)')
    
    args = parser.parse_args()
    
    if args.url:
        # Scrape specific URL
        success = scrape_single_workflow(args.url, args.min_delay, args.max_delay)
        if success:
            print("\n✅ Workflow scraped successfully!")
        else:
            print("\n❌ Failed to scrape workflow.")
    else:
        # Interactive mode
        print("🚀 Single Workflow Scraper")
        print("=" * 50)
        print("This scraper adds one workflow at a time with random delays.")
        print("It's safe and respectful to n8n.io servers.")
        print("")
        
        workflow_urls = get_next_workflow_url()
        
        print("Available workflow URLs:")
        for i, url in enumerate(workflow_urls, 1):
            print(f"  {i}. {url}")
        
        print("")
        choice = input("Enter workflow number to scrape (or 'q' to quit): ")
        
        if choice.lower() == 'q':
            print("👋 Goodbye!")
            return
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(workflow_urls):
                url = workflow_urls[index]
                
                # Random delay before starting
                delay = random.randint(args.min_delay, args.max_delay)
                print(f"⏱️  Waiting {delay} seconds before starting...")
                time.sleep(delay)
                
                success = scrape_single_workflow(url, args.min_delay, args.max_delay)
                
                if success:
                    print("\n✅ Workflow scraped successfully!")
                    print("💡 Tip: Run this script again to scrape another workflow.")
                else:
                    print("\n❌ Failed to scrape workflow.")
            else:
                print("❌ Invalid choice.")
        except ValueError:
            print("❌ Please enter a valid number.")

if __name__ == "__main__":
    main()
