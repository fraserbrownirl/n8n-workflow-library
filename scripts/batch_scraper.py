#!/usr/bin/env python3
"""
Batch n8n Workflow Scraper - Scrapes multiple workflows with enhanced metadata.
"""

import time
import json
import re
import os
import requests
import zipfile
import html
import hashlib
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

def get_workflow_urls_from_n8n_arena():
    """Get workflow URLs from n8nArena.com (simulated for now)."""
    # For now, we'll use a list of known workflow URLs
    # In a real implementation, you'd scrape n8nArena.com for the latest workflows
    
    workflow_urls = [
        "https://n8n.io/workflows/5678-automate-email-filtering-and-ai-summarization-100percent-free-and-effective-works-724/",
        "https://n8n.io/workflows/1234-slack-notification-automation/",
        "https://n8n.io/workflows/5678-data-processing-pipeline/",
        "https://n8n.io/workflows/9012-ai-content-generation/",
        "https://n8n.io/workflows/3456-payment-processing-automation/"
    ]
    
    print(f"📋 Found {len(workflow_urls)} workflow URLs to process")
    return workflow_urls

def scrape_workflow_batch(workflow_urls, max_workflows=None, delay=5):
    """Scrape a batch of workflows."""
    print("🚀 Starting Batch n8n Workflow Scraper")
    print("=" * 60)
    
    # Get existing workflows for deduplication
    existing_workflows = get_existing_workflows()
    print(f"📊 Found {len(existing_workflows)} existing workflows")
    
    # Limit the number of workflows to scrape
    if max_workflows:
        workflow_urls = workflow_urls[:max_workflows]
        print(f"📋 Limiting to {max_workflows} workflows")
    
    driver = None
    scraped_count = 0
    failed_count = 0
    
    try:
        driver = setup_driver()
        
        for i, workflow_url in enumerate(workflow_urls, 1):
            print(f"\n🔍 [{i}/{len(workflow_urls)}] Scraping: {workflow_url}")
            
            try:
                # Navigate to the workflow page
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
                    failed_count += 1
                    continue
                
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
                        continue
                    
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
                    
                    scraped_count += 1
                    existing_workflows.add(safe_name)  # Update for next iteration
                    
                else:
                    print("  ❌ Could not extract workflow JSON")
                    failed_count += 1
                
                # Delay between scrapes
                if i < len(workflow_urls):
                    print(f"  ⏱️  Waiting {delay} seconds before next scrape...")
                    time.sleep(delay)
                    
            except Exception as e:
                print(f"  ❌ Error scraping workflow: {e}")
                failed_count += 1
                continue
    
    except Exception as e:
        print(f"❌ Error setting up driver: {e}")
    finally:
        if driver:
            driver.quit()
    
    print("\n" + "=" * 60)
    print("📊 Batch Scraping Summary:")
    print(f"  ✅ Successfully scraped: {scraped_count}")
    print(f"  ❌ Failed: {failed_count}")
    print(f"  📋 Total processed: {len(workflow_urls)}")
    
    if scraped_count > 0:
        print(f"\n🎉 SUCCESS: Added {scraped_count} new workflows!")
        print("The workflow JSONs are unaltered with metadata added!")
    else:
        print("\n⚠️  No new workflows were scraped.")
    
    return scraped_count

def main():
    """Main function for batch scraping."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch scrape n8n workflows')
    parser.add_argument('--max', type=int, default=5, help='Maximum workflows to scrape')
    parser.add_argument('--delay', type=int, default=5, help='Delay between scrapes (seconds)')
    parser.add_argument('--urls', nargs='+', help='Specific workflow URLs to scrape')
    
    args = parser.parse_args()
    
    if args.urls:
        workflow_urls = args.urls
    else:
        workflow_urls = get_workflow_urls_from_n8n_arena()
    
    scraped_count = scrape_workflow_batch(
        workflow_urls, 
        max_workflows=args.max, 
        delay=args.delay
    )
    
    if scraped_count > 0:
        print(f"\n🔄 Generating indexes for {scraped_count} new workflows...")
        try:
            from generate_indexes import main as generate_indexes
            generate_indexes()
            print("✅ Indexes generated successfully!")
        except Exception as e:
            print(f"❌ Error generating indexes: {e}")

if __name__ == "__main__":
    main()
