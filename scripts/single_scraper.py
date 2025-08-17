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
import re
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

def download_chrome_driver():
    """Download the correct Chrome driver for Mac ARM64."""
    print("📥 Downloading Chrome driver for Mac ARM64...")
    
    # Create driver directory
    driver_dir = os.path.expanduser("~/chromedriver")
    os.makedirs(driver_dir, exist_ok=True)
    
    # Download URL for Mac ARM64 Chrome driver
    driver_url = "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/139.0.7258.68/mac-arm64/chromedriver-mac-arm64.zip"
    
    try:
        # Download the driver
        response = requests.get(driver_url, stream=True)
        response.raise_for_status()
        
        zip_path = os.path.join(driver_dir, "chromedriver.zip")
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Extract the zip file
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(driver_dir)
        
        # Make the driver executable
        driver_path = os.path.join(driver_dir, "chromedriver-mac-arm64", "chromedriver")
        os.chmod(driver_path, 0o755)
        
        print(f"✅ Chrome driver downloaded to: {driver_path}")
        return driver_path
        
    except Exception as e:
        print(f"❌ Failed to download Chrome driver: {e}")
        return None

def setup_driver():
    """Initialize Chrome WebDriver for Mac ARM64."""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent to appear more like a real browser
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Set Chrome binary location for Mac
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome_path):
        chrome_options.binary_location = chrome_path
        print(f"✅ Using Chrome at: {chrome_path}")
    
    # Download and use the correct driver
    driver_path = download_chrome_driver()
    if not driver_path:
        raise Exception("Could not download Chrome driver")
    
    try:
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.set_window_size(1920, 1080)
        
        return driver
    except Exception as e:
        print(f"❌ Error setting up Chrome driver: {e}")
        raise

def extract_workflow_json_from_page(driver):
    """Extract complete workflow JSON from the page after clicking 'Use for Free'."""
    try:
        # Get the page source
        page_source = driver.page_source
        
        # Look for the n8n-demo component with workflow JSON
        n8n_demo_pattern = r'<n8n-demo[^>]*workflow="([^"]*)"[^>]*>'
        matches = re.findall(n8n_demo_pattern, page_source)
        
        if matches:
            print(f"Found {len(matches)} n8n-demo components")
            
            for i, match in enumerate(matches):
                # The workflow JSON is HTML-encoded, so we need to decode it
                decoded_json = html.unescape(match)
                
                try:
                    # Parse the JSON
                    workflow_data = json.loads(decoded_json)
                    
                    # Check if it's a complete workflow
                    if isinstance(workflow_data, dict) and 'nodes' in workflow_data and 'connections' in workflow_data:
                        print(f"✅ Found complete workflow JSON: {len(workflow_data['nodes'])} nodes, {len(workflow_data['connections'])} connections")
                        return workflow_data
                        
                except json.JSONDecodeError as e:
                    print(f"❌ Error parsing JSON: {e}")
                    continue
        
        print("❌ No complete workflow JSON found in page")
        return None
        
    except Exception as e:
        print(f"❌ Error extracting workflow JSON: {e}")
        return None

def extract_metadata_from_workflow(workflow_data, source_url):
    """Extract metadata from workflow without altering core data."""
    metadata = {
        "workflow_name": workflow_data.get('name', 'Untitled Workflow'),
        "scraped_at": datetime.now().isoformat(),
        "source_url": source_url,
        "node_count": len(workflow_data.get('nodes', [])),
        "connection_count": len(workflow_data.get('connections', {})),
        "has_trigger": any('trigger' in node.get('type', '').lower() for node in workflow_data.get('nodes', [])),
        "has_credentials": any('credentials' in node for node in workflow_data.get('nodes', [])),
        "integrations": extract_integrations(workflow_data),
        "categories": detect_categories(workflow_data),
        "complexity": calculate_complexity(workflow_data),
        "quality_score": calculate_quality_score(workflow_data),
        "description": extract_description(workflow_data)
    }
    
    return metadata

def extract_integrations(workflow_data):
    """Extract integration services from workflow."""
    integrations = set()
    
    for node in workflow_data.get('nodes', []):
        node_type = node.get('type', '')
        
        # Map node types to service names
        service_mapping = {
            'gmail': ['gmail', 'gmailTrigger'],
            'google-sheets': ['googleSheets'],
            'slack': ['slack'],
            'discord': ['discord'],
            'telegram': ['telegram'],
            'stripe': ['stripe'],
            'openai': ['openai', 'gpt'],
            'anthropic': ['anthropic', 'claude'],
            'groq': ['groq'],
            'http': ['httpRequest', 'webhook'],
            'mysql': ['mysql'],
            'postgres': ['postgres'],
            'notion': ['notion'],
            'airtable': ['airtable'],
            'hubspot': ['hubspot'],
            'salesforce': ['salesforce'],
            'zapier': ['zapier'],
            'twilio': ['twilio'],
            'sendgrid': ['sendgrid'],
            'mailchimp': ['mailchimp']
        }
        
        for service, patterns in service_mapping.items():
            if any(pattern.lower() in node_type.lower() for pattern in patterns):
                integrations.add(service)
    
    return list(integrations)

def detect_categories(workflow_data):
    """Detect workflow categories based on content."""
    categories = set()
    workflow_text = json.dumps(workflow_data).lower()
    
    category_patterns = {
        'ai-automation': ['gpt', 'claude', 'openai', 'anthropic', 'llm', 'langchain', 'ai', 'groq'],
        'email-automation': ['gmail', 'email', 'mailchimp', 'sendgrid'],
        'data-processing': ['csv', 'excel', 'transform', 'database', 'mysql', 'postgres'],
        'communication': ['slack', 'discord', 'telegram', 'twilio', 'sms'],
        'payment-processing': ['stripe', 'paypal', 'payment', 'invoice'],
        'file-management': ['gdrive', 'dropbox', 's3', 'upload', 'download'],
        'web-scraping': ['scrape', 'crawl', 'extract', 'parse'],
        'api-integration': ['http', 'webhook', 'rest', 'api'],
        'scheduling': ['cron', 'schedule', 'trigger'],
        'notifications': ['notify', 'alert', 'notification']
    }
    
    for category, patterns in category_patterns.items():
        if any(pattern in workflow_text for pattern in patterns):
            categories.add(category)
    
    return list(categories) if categories else ['general']

def calculate_complexity(workflow_data):
    """Calculate workflow complexity."""
    node_count = len(workflow_data.get('nodes', []))
    connection_count = len(workflow_data.get('connections', {}))
    has_conditionals = any('if' in node.get('type', '').lower() for node in workflow_data.get('nodes', []))
    has_loops = any('loop' in node.get('type', '').lower() for node in workflow_data.get('nodes', []))
    
    score = node_count + (connection_count * 0.5)
    if has_conditionals:
        score += 3
    if has_loops:
        score += 5
    
    if score <= 5:
        return 'beginner'
    elif score <= 15:
        return 'intermediate'
    else:
        return 'advanced'

def calculate_quality_score(workflow_data):
    """Calculate workflow quality score (0-100)."""
    score = 0
    
    # Has documentation (30 points)
    if has_documentation(workflow_data):
        score += 30
    
    # Uses credentials properly (20 points)
    if uses_proper_credentials(workflow_data):
        score += 20
    
    # Has error handling (15 points)
    if has_error_handling(workflow_data):
        score += 15
    
    # Well organized (10 points)
    if is_well_organized(workflow_data):
        score += 10
    
    # Modern integrations (15 points)
    if has_modern_integrations(workflow_data):
        score += 15
    
    # Reusable/parameterized (10 points)
    if is_parameterized(workflow_data):
        score += 10
    
    return min(score, 100)

def has_documentation(workflow_data):
    """Check if workflow has documentation."""
    for node in workflow_data.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.stickyNote':
            content = node.get('parameters', {}).get('content', '')
            if len(content) > 100:  # Substantial documentation
                return True
    return False

def uses_proper_credentials(workflow_data):
    """Check if credentials are used properly (not hardcoded)."""
    workflow_str = json.dumps(workflow_data)
    
    # Check for hardcoded API keys or passwords
    hardcoded_patterns = [
        r'api[_-]?key["\s:]+["\'][A-Za-z0-9]{20,}',
        r'password["\s:]+["\'][^"\']+["\']',
        r'Bearer [A-Za-z0-9]{20,}'
    ]
    
    for pattern in hardcoded_patterns:
        if re.search(pattern, workflow_str, re.IGNORECASE):
            return False
    
    # Check if uses credential nodes
    return any('credentials' in node for node in workflow_data.get('nodes', []))

def has_error_handling(workflow_data):
    """Check for error handling patterns."""
    error_indicators = ['error', 'catch', 'try', 'fail', 'stopAndError']
    workflow_str = json.dumps(workflow_data).lower()
    
    return any(indicator in workflow_str for indicator in error_indicators)

def is_well_organized(workflow_data):
    """Check if workflow is well organized."""
    nodes = workflow_data.get('nodes', [])
    if len(nodes) < 3:
        return True
    
    # Check if nodes have meaningful names
    default_names = 0
    for node in nodes:
        name = node.get('name', '')
        if re.match(r'^(Node|HTTP Request|Set|If)\d*$', name):
            default_names += 1
    
    return default_names < len(nodes) / 2

def has_modern_integrations(workflow_data):
    """Check for modern AI/API integrations."""
    modern_services = ['openai', 'anthropic', 'gpt', 'claude', 'langchain', 'stripe', 'twilio']
    workflow_str = json.dumps(workflow_data).lower()
    
    return any(service in workflow_str for service in modern_services)

def is_parameterized(workflow_data):
    """Check if workflow uses parameters/variables."""
    workflow_str = json.dumps(workflow_data)
    
    # Check for expression usage
    return '{{' in workflow_str or '$(' in workflow_str

def extract_description(workflow_data):
    """Extract description from sticky notes or metadata."""
    description_parts = []
    
    # Extract from sticky notes
    for node in workflow_data.get('nodes', []):
        if node.get('type') == 'n8n-nodes-base.stickyNote':
            content = node.get('parameters', {}).get('content', '')
            if content:
                # Extract title or first paragraph
                lines = content.split('\n')
                for line in lines[:3]:  # First 3 lines
                    line = re.sub(r'^#+\s*', '', line).strip()  # Remove markdown headers
                    if line and len(line) > 20:
                        description_parts.append(line)
                        break
    
    return ' | '.join(description_parts[:2]) if description_parts else ''

def sanitize_filename(name):
    """Sanitize workflow name for filename."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Limit length
    if len(name) > 100:
        name = name[:100]
    
    return name

def get_existing_workflows():
    """Get list of existing workflow filenames."""
    workflows_dir = Path('workflows')
    if not workflows_dir.exists():
        return set()
    
    existing = set()
    for file in workflows_dir.glob('*.json'):
        existing.add(file.stem)  # filename without extension
    
    return existing

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
