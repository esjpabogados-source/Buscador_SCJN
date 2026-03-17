from playwright.sync_api import sync_playwright
import json

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    
    api_calls = []
    
    # Listen to all requests
    def handle_request(route, request):
        if 'api' in request.url.lower() or 'busqueda' in request.url.lower():
            api_calls.append({
                'url': request.url,
                'method': request.method,
                'headers': request.headers,
                'post_data': request.post_data
            })
        route.continue_()
            
    # Enable request interception
    page.route("**/*", handle_request)
    
    print("Navigating to SCJN search page...")
    page.goto("https://sjf2.scjn.gob.mx/busqueda-principal-tesis")
    
    # Wait a bit
    page.wait_for_timeout(3000)
    
    try:
        print("Performing search...")
        page.fill("input[type='text']", "amparo directo")
        page.press("input[type='text']", "Enter")
        # Click the search button if Enter doesn't work. The button might be different. Let's just wait to see if requests are made.
        page.wait_for_timeout(5000)
    except Exception as e:
        print(f"Interaction error: {e}")
        
    print(f"Captured {len(api_calls)} interesting requests.")
    with open('api_calls.json', 'w', encoding='utf-8') as f:
        json.dump(api_calls, f, indent=2, ensure_ascii=False)
            
    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
