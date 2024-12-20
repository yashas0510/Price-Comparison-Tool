from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from urllib.parse import quote_plus
import time
import random
import requests

app = Flask(__name__)

# Function to retry failed requests with exponential backoff
def fetch_with_retries(url, headers, retries=5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            print(f"Attempt {attempt + 1} failed with status {response.status_code}. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        time.sleep(2 ** attempt + random.uniform(0, 1))  # Exponential backoff with random jitter
    return None

# Function to setup Selenium WebDriver with options
def get_selenium_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU for performance
    chrome_options.add_argument("--no-sandbox")  # Disable sandboxing for compatibility

    # Provide the path to your chromedriver executable
    driver_path = "C:/Users/yashas/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"  # Adjust this path if necessary
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# Function to scrape prices from a specific site using Selenium
def fetch_price_from_site(site, product):
    if site == 'amazon':
        product_encoded = quote_plus(product)
        url = f'https://www.amazon.in/s?k={product_encoded}'
        ua = UserAgent()
        headers = {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.amazon.in/',
            'Cache-Control': 'max-age=0'
        }

        # Fetch the page with retries using requests first (for initial page load)
        page = fetch_with_retries(url, headers)
        
        if not page or page.status_code != 200:
            print(f"Failed to fetch page for {product} from Amazon. Status Code: {page.status_code if page else 'No Response'}")
            return None
        
        # Use Selenium for dynamic content
        driver = get_selenium_driver()
        driver.get(url)  # Load the Amazon page

        time.sleep(2)  # Give time for the page to load

        # Extract price using Selenium
        try:
            price_element = driver.find_element(By.CLASS_NAME, 'a-price-whole')
            price = price_element.text.replace(',', '').replace('₹', '').strip()
            print(f"Found price: {price}")
            driver.quit()
            return float(price)
        except Exception as e:
            print(f"Error extracting price: {e}")
            driver.quit()
            return None

    return None

# Serve the index.html file
@app.route('/')
def index():
    return render_template('index.html')  # Make sure this is looking inside the 'templates' folder

# Endpoint to compare prices from various sites
@app.route('/compare-prices', methods=['GET'])
def compare_prices():
    product = request.args.get('product')
    sites = ['amazon', 'flipkart', 'ajio', 'myntra', 'tatacliq', 'reliance', 'croma', 'vijay_sales', 'kohinoor']
    
    prices = []
    for site in sites:
        price = fetch_price_from_site(site, product)
        if price:
            prices.append({'site': site, 'price': price})

    if not prices:
        return jsonify({'error': 'No prices found for this product.'})
    
    best_price = min(prices, key=lambda x: x['price'])
    
    return jsonify({'prices': prices, 'bestPrice': best_price})

if __name__ == '__main__':
    app.run(debug=True)
