import os
import json
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from pyppeteer import launch

# Config
OUTPUT_FOLDER = "ERROR_army_data"
HEADLESS_MODE = True  # Set False for debugging

def setup_folders():
    """Create folders for storing scraped data."""
    folders = ["html", "text", "images", "videos", "scripts", "apis", "metadata", "hidden_data"]
    for folder in folders:
        os.makedirs(os.path.join(OUTPUT_FOLDER, folder), exist_ok=True)

def save_data(content, filename, subfolder="text"):
    """Save scraped data to a file."""
    path = os.path.join(OUTPUT_FOLDER, subfolder, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def download_file(url, folder):
    """Download and save files (images, videos, PDFs, etc.)."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        if response.status_code == 200:
            filename = os.path.basename(urlparse(url).path) or f"file_{int(time.time())}"
            filepath = os.path.join(OUTPUT_FOLDER, folder, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
    except Exception as e:
        print(f"❌ Failed to download {url}: {e}")
    return False

def scrape_with_selenium(url):
    """Use Selenium to scrape dynamic content."""
    options = Options()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JavaScript to load
        
        # Get all HTML (including dynamically loaded content)
        html = driver.page_source
        save_data(html, "full_page.html", "html")
        
        # Extract hidden inputs
        hidden_inputs = driver.find_elements_by_xpath("//input[@type='hidden']")
        hidden_data = {input.get_attribute('name'): input.get_attribute('value') for input in hidden_inputs}
        save_data(json.dumps(hidden_data), "hidden_inputs.json", "hidden_data")
        
        # Extract localStorage & sessionStorage
        local_storage = driver.execute_script("return JSON.stringify(localStorage);")
        session_storage = driver.execute_script("return JSON.stringify(sessionStorage);")
        save_data(local_storage, "local_storage.json", "hidden_data")
        save_data(session_storage, "session_storage.json", "hidden_data")
        
        # Extract API calls from Network tab (requires Chrome DevTools)
        logs = driver.get_log("performance")
        api_calls = [log["message"] for log in logs if "fetch" in log["message"] or "api" in log["message"].lower()]
        save_data("\n".join(api_calls), "api_calls.txt", "apis")
        
        return html
    finally:
        driver.quit()

def scrape_with_pyppeteer(url):
    """Use Pyppeteer (headless Chrome) for advanced scraping."""
    async def fetch():
        browser = await launch(headless=HEADLESS_MODE)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})
        
        # Get full HTML
        html = await page.content()
        save_data(html, "dynamic_page.html", "html")
        
        # Extract JavaScript variables
        js_vars = await page.evaluate('''() => {
            const data = {};
            for (let key in window) {
                if (typeof window[key] !== 'function' && !key.startsWith('_')) {
                    try {
                        data[key] = window[key];
                    } catch (e) {}
                }
            }
            return data;
        }''')
        save_data(json.dumps(js_vars), "javascript_vars.json", "hidden_data")
        
        await browser.close()
        return html
    
    import asyncio
    return asyncio.get_event_loop().run_until_complete(fetch())

def scrape_metadata(soup):
    """Extract SEO & metadata."""
    meta_data = {
        "title": soup.title.string if soup.title else None,
        "meta_tags": {tag.get('name', tag.get('property')): tag.get('content') 
                      for tag in soup.find_all('meta')},
        "json_ld": [json.loads(script.string) for script in soup.find_all('script', type='application/ld+json')],
        "open_graph": {tag.get('property'): tag.get('content') 
                       for tag in soup.find_all('meta', property=re.compile(r'^og:'))}
    }
    save_data(json.dumps(meta_data), "metadata.json", "metadata")

def scrape_all_assets(soup, base_url):
    """Download images, videos, scripts, and other assets."""
    # Images
    for img in soup.find_all('img'):
        img_url = img.get('src') or img.get('data-src')
        if img_url:
            img_url = urljoin(base_url, img_url)
            download_file(img_url, "images")
    
    # Videos
    for video in soup.find_all('video'):
        video_url = video.get('src') or video.find('source').get('src') if video.find('source') else None
        if video_url:
            video_url = urljoin(base_url, video_url)
            download_file(video_url, "videos")
    
    # Scripts
    for script in soup.find_all('script', src=True):
        script_url = urljoin(base_url, script['src'])
        download_file(script_url, "scripts")

def main():
    setup_folders()
    url = input("Enter website URL: ")
    
    # Scrape with Requests (static content)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    save_data(response.text, "static_page.html", "html")
    
    # Extract metadata
    scrape_metadata(soup)
    
    # Download assets
    scrape_all_assets(soup, url)
    
    # Scrape dynamic content with Selenium
    selenium_html = scrape_with_selenium(url)
    
    # Scrape JavaScript variables with Pyppeteer
    pyppeteer_html = scrape_with_pyppeteer(url)
    
    print(f"✅ All data saved in '{OUTPUT_FOLDER}' folder!")

if __name__ == "__main__":
    main()
