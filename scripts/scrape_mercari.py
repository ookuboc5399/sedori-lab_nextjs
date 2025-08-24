
import sys
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import requests

# A single product page URL (requests is fine here)
def scrape_product_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        title_string = soup.title.string if soup.title else "No title found"
        price_string = "Price not found"
        price_element = soup.find("div", attrs={"data-testid": "price"})
        if price_element:
            raw_price = price_element.text.strip()
            price_string = "".join(filter(str.isdigit, raw_price))

        result = {
            "title": title_string.strip(),
            "price": int(price_string) if price_string.isdigit() else "N/A",
            "url": url,
            "source": "Mercari"
        }
        print(json.dumps(result, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        sys.stderr.write(json.dumps({"error": f"Network request failed: {e}"}) + '\n')
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(json.dumps({"error": f"An unexpected error occurred: {e}"}) + '\n')
        sys.exit(1)

# The new listings on the homepage using Selenium and structured data
def scrape_new_listings():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get("https://jp.mercari.com/")
        time.sleep(5) # Wait for dynamic content to load
        
        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        new_items = []
        
        structured_data_scripts = soup.find_all('script', type='application/ld+json')

        if not structured_data_scripts:
            sys.stderr.write(json.dumps({"error": "Could not find any ld+json structured data on the page."}) + '\n')
            sys.exit(1)

        for script in structured_data_scripts:
            try:
                data = json.loads(script.string)
                if data.get('@type') == 'ItemList':
                    for item in data.get('itemListElement', []):
                        product = item.get('item', {})
                        if product:
                            name = product.get('name', 'N/A')
                            url = product.get('url', 'N/A')
                            price = product.get('offers', {}).get('price', 0)
                            
                            new_items.append({
                                "title": name,
                                "price": int(price),
                                "url": url,
                                "source": "Mercari"
                            })
                    break # Found the main item list, no need to check other scripts
            except (json.JSONDecodeError, AttributeError):
                continue
        
        if not new_items:
             sys.stderr.write(json.dumps({"error": "Found ld+json data, but could not extract new items from it."}) + '\n')
             sys.exit(1)

        print(json.dumps(new_items, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(json.dumps({"error": f"An unexpected error occurred in Selenium process: {e}"}) + '\n')
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--new':
            scrape_new_listings()
        elif sys.argv[1] == '--product' and len(sys.argv) > 2:
            url_to_scrape = sys.argv[2]
            scrape_product_page(url_to_scrape)
        else:
            sys.stderr.write(json.dumps({"error": "Invalid arguments"}) + '\n')
            sys.exit(1)
    else:
        sys.stderr.write(json.dumps({"error": "Usage: python scrape_mercari.py --new | --product <URL>"}) + '\n')
        sys.exit(1)
