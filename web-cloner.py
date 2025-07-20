import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import concurrent.futures
import mimetypes
import time

# Developer credit
DEVELOPER_CREDIT = "@ERROR0101r"

class WebsiteExtractor:
    def __init__(self, base_url, output_dir="website_assets"):
        self.base_url = base_url
        self.domain = urlparse(base_url).netloc
        self.output_dir = output_dir
        self.visited_urls = set()
        self.assets_downloaded = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Combined files
        self.all_js = ""
        self.all_css = ""
        
    def is_valid_url(self, url):
        """Check if a URL is valid and belongs to the same domain."""
        parsed = urlparse(url)
        return bool(parsed.netloc) and parsed.netloc == self.domain
        
    def get_absolute_url(self, url):
        """Convert relative URL to absolute URL."""
        return urljoin(self.base_url, url)
        
    def sanitize_filename(self, url):
        """Create a safe filename from URL."""
        parsed = urlparse(url)
        path = parsed.path.split('/')[-1] or "index"
        netloc = parsed.netloc.replace('.', '_')
        filename = f"{netloc}_{path}"
        
        # Remove invalid characters
        filename = "".join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
        return filename
        
    def download_file(self, url, asset_type=None):
        """Download a file from the given URL."""
        if url in self.assets_downloaded:
            return
            
        try:
            response = self.session.get(url, stream=True, timeout=10)
            response.raise_for_status()
            
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Determine filename
            filename = self.sanitize_filename(url)
            content_type = response.headers.get('content-type', '')
            
            # Handle different file types
            if 'javascript' in content_type or url.endswith('.js'):
                file_path = os.path.join(self.output_dir, "combined_js.js")
                js_content = response.text
                self.all_js += f"\n/* === {url} === */\n{js_content}\n"
                return
            elif 'css' in content_type or url.endswith('.css'):
                file_path = os.path.join(self.output_dir, "combined_css.css")
                css_content = response.text
                self.all_css += f"\n/* === {url} === */\n{css_content}\n"
                return
            else:
                # For other files (images, etc.)
                extension = mimetypes.guess_extension(content_type) or '.bin'
                if not filename.endswith(extension):
                    filename += extension
                file_path = os.path.join(self.output_dir, filename)
                
            # Save the file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            self.assets_downloaded.add(url)
            print(f"Downloaded: {url}")
            return True
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")
            return False
            
    def extract_assets(self, soup, page_url):
        """Extract all assets (images, scripts, styles) from the page."""
        assets = []
        
        # Extract images
        for img in soup.find_all('img', src=True):
            src = img['src']
            if not src.startswith('data:'):  # Skip base64 encoded images
                assets.append(self.get_absolute_url(src))
                
        # Extract scripts
        for script in soup.find_all('script', src=True):
            assets.append(self.get_absolute_url(script['src']))
            
        # Extract stylesheets
        for link in soup.find_all('link', rel='stylesheet', href=True):
            assets.append(self.get_absolute_url(link['href']))
            
        # Extract other assets (favicon, etc.)
        for link in soup.find_all('link', href=True):
            if any(rel in link.get('rel', []) for rel in ['icon', 'shortcut icon', 'apple-touch-icon']):
                assets.append(self.get_absolute_url(link['href']))
                
        # Extract background images from CSS
        for tag in soup.find_all(style=True):
            style = tag['style']
            if 'url(' in style:
                start = style.index('url(') + 4
                end = style.index(')', start)
                url = style[start:end].strip('"\'')
                if url and not url.startswith('data:'):
                    assets.append(self.get_absolute_url(url))
                    
        # Download all assets
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.download_file, asset) for asset in assets]
            concurrent.futures.wait(futures)
            
    def extract_links(self, soup):
        """Extract all internal links from the page."""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('/') or self.domain in href:
                absolute_url = self.get_absolute_url(href)
                if self.is_valid_url(absolute_url) and absolute_url not in self.visited_urls:
                    links.append(absolute_url)
        return links
        
    def process_page(self, url):
        """Process a single webpage."""
        if url in self.visited_urls:
            return []
            
        self.visited_urls.add(url)
        print(f"Processing: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Save the HTML content
            filename = self.sanitize_filename(url) + ".html"
            file_path = os.path.join(self.output_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
                
            # Parse HTML and extract assets
            soup = BeautifulSoup(response.text, 'html.parser')
            self.extract_assets(soup, url)
            
            # Extract and return internal links for further processing
            return self.extract_links(soup)
        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return []
            
    def save_combined_files(self):
        """Save combined JS and CSS files."""
        if self.all_js:
            with open(os.path.join(self.output_dir, "combined_js.js"), 'w', encoding='utf-8') as f:
                f.write(self.all_js)
        if self.all_css:
            with open(os.path.join(self.output_dir, "combined_css.css"), 'w', encoding='utf-8') as f:
                f.write(self.all_css)
            
    def crawl_website(self):
        """Crawl the website starting from the base URL."""
        print(f"Starting website extraction for {self.base_url}")
        print(f"Developer: {DEVELOPER_CREDIT}")
        
        to_visit = [self.base_url]
        
        while to_visit:
            current_url = to_visit.pop(0)
            new_links = self.process_page(current_url)
            to_visit.extend(new_links)
            
        # Save combined files after crawling is complete
        self.save_combined_files()
        
        print("\nWebsite extraction completed!")
        print(f"Total pages processed: {len(self.visited_urls)}")
        print(f"Total assets downloaded: {len(self.assets_downloaded)}")
        print(f"All files saved in: {os.path.abspath(self.output_dir)}")
        

def main():
    print("Website Asset Extractor Tool")
    print(f"Developed by: {DEVELOPER_CREDIT}\n")
    
    website_url = input("Enter the website URL to extract (include http:// or https://): ").strip()
    
    if not website_url.startswith(('http://', 'https://')):
        print("Invalid URL. Please include http:// or https://")
        return
        
    output_dir = input("Enter output directory (default: website_assets): ").strip()
    if not output_dir:
        output_dir = "website_assets"
        
    extractor = WebsiteExtractor(website_url, output_dir)
    
    start_time = time.time()
    extractor.crawl_website()
    end_time = time.time()
    
    print(f"\nProcess completed in {end_time - start_time:.2f} seconds.")
    

if __name__ == "__main__":
    main()
