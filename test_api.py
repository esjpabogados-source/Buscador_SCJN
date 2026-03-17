import requests
import re
import os

def check_token():
    url = "https://sjf2.scjn.gob.mx/main.f0b4179a4a3892c0.js"
    print(f"Fetching {url}... ")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = response.text
            with open('main.js', 'w', encoding='utf-8') as f:
                f.write(html)
            print("Saved main.js")
            
            # Searching for bearer token pattern or something similar
            matches = re.findall(r'Bearer\s+(eyJ[\w-]+\.[\w-]+\.[\w-]+)', html)
            if matches:
                print("Found Bearer token in JS!")
                print(matches[0][:50] + "...")
            else:
                print("No hardcoded Bearer JWT found.")
                
            # look for API URLs
            api_urls = re.findall(r'(https?://[^\'"]+/api/[^\'"]+)', html)
            print("API URLs found:", set(api_urls))
            
            # look for token endpoints
            tokens = re.findall(r'(\btoken\b|\bauth\b)[\'":\s]+([^\'",]+)', html, re.IGNORECASE)
            print("Token references snippet:", tokens[:10])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_token()
