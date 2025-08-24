import sys
import json
import time
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def search_amazon(query):
    """Searches Amazon Japan for a given query and returns a list of products."""
    search_url = f"https://www.amazon.co.jp/s?k={quote_plus(query)}"
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)

        driver.get(search_url)
        time.sleep(3)
        
        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Find all search result items based on the data-asin attribute
        results = soup.find_all('div', {'data-asin': True})

        for result in results:
            # Skip items that are not actual search results
            if not result.get('data-component-type') == 's-search-result':
                continue

            title_element = result.select_one('h2 a.a-link-normal span.a-text-normal')
            price_element = result.select_one('span.a-price-whole')
            url_element = result.select_one('h2 a.a-link-normal')

            if title_element and price_element and url_element:
                title = title_element.get_text(strip=True)
                price = int(price_element.get_text(strip=True).replace(',', ''))
                url = "https://www.amazon.co.jp" + url_element['href']

                products.append({
                    "title": title,
                    "price": price,
                    "url": url,
                    "source": "Amazon"
                })
        
        print(json.dumps(products, ensure_ascii=False))

    except Exception as e:
        sys.stderr.write(json.dumps({"error": f"An unexpected error occurred: {e}"}) + '\n')
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.stderr.write(json.dumps({"error": "Usage: python scrape_amazon.py \"<search query>\""}) + '\n')
        sys.exit(1)
    
    query = sys.argv[1]
    search_amazon(query)
