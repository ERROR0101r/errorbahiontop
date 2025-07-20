import hashlib
import requests
from urllib.parse import urlparse
import json
import os

class WebsiteAPIKeyGenerator:
    def __init__(self):
        self.api_keys_file = "website_api_keys.json"
        self.load_existing_keys()

    def load_existing_keys(self):
        """Load existing API keys from file"""
        if os.path.exists(self.api_keys_file):
            with open(self.api_keys_file, 'r') as f:
                self.api_keys = json.load(f)
        else:
            self.api_keys = {}

    def save_keys(self):
        """Save API keys to file"""
        with open(self.api_keys_file, 'w') as f:
            json.dump(self.api_keys, f, indent=4)

    def generate_api_key(self, website_url):
        """Generate a unique API key for a website"""
        parsed_url = urlparse(website_url)
        domain = parsed_url.netloc
        
        if domain in self.api_keys:
            return self.api_keys[domain]['api_key']
        
        # Create a hash-based API key
        secret_salt = "my_api_salt_123"  # In production, use a more secure salt
        key_string = f"{domain}{secret_salt}".encode('utf-8')
        api_key = hashlib.sha256(key_string).hexdigest()
        
        # Store the API key with the domain
        self.api_keys[domain] = {
            'api_key': api_key,
            'base_url': f"{parsed_url.scheme}://{domain}",
            'endpoints': {}
        }
        
        self.save_keys()
        return api_key

    def make_api_request(self, api_key, endpoint, method="GET", params=None, data=None):
        """Make a request to the website API using the generated key"""
        domain_info = None
        for domain, info in self.api_keys.items():
            if info['api_key'] == api_key:
                domain_info = info
                break
        
        if not domain_info:
            return {"error": "Invalid API key"}
        
        base_url = domain_info['base_url']
        full_url = f"{base_url}{endpoint}"
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                response = requests.get(full_url, headers=headers, params=params)
            elif method.upper() == "POST":
                response = requests.post(full_url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(full_url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(full_url, headers=headers)
            else:
                return {"error": "Unsupported HTTP method"}
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def get_api_key_for_website(self, website_url):
        """Get or generate API key for a website"""
        return self.generate_api_key(website_url)

def main():
    api_generator = WebsiteAPIKeyGenerator()
    
    print("Website to API Key Generator")
    print("----------------------------")
    
    while True:
        print("\nOptions:")
        print("1. Generate API key for a website")
        print("2. Make API request using existing key")
        print("3. Exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            website_url = input("Enter website URL (e.g., https://example.com): ")
            api_key = api_generator.generate_api_key(website_url)
            print(f"\nGenerated API Key for {website_url}:")
            print(api_key)
            print("\nYou can now use this key to make requests to the website.")
            
        elif choice == "2":
            api_key = input("Enter your API key: ")
            endpoint = input("Enter API endpoint (e.g., /api/data): ")
            method = input("Enter HTTP method (GET/POST/PUT/DELETE, default GET): ") or "GET"
            
            params = None
            data = None
            
            if method.upper() in ["POST", "PUT"]:
                data_input = input("Enter JSON data (optional, as dictionary): ")
                if data_input:
                    try:
                        data = json.loads(data_input)
                    except json.JSONDecodeError:
                        print("Invalid JSON format. Using empty data.")
            
            if method.upper() == "GET":
                params_input = input("Enter query parameters (optional, as dictionary): ")
                if params_input:
                    try:
                        params = json.loads(params_input)
                    except json.JSONDecodeError:
                        print("Invalid JSON format. Using no parameters.")
            
            response = api_generator.make_api_request(api_key, endpoint, method, params, data)
            print("\nAPI Response:")
            print(json.dumps(response, indent=2))
            
        elif choice == "3":
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
