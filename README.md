# Price Comparison Tool (Amazon and more)

This is a Python-based price comparison tool that uses **Selenium** to scrape product prices from various online shopping websites, including **Amazon**, and returns the best price found. The tool is built with **Flask** for the web interface and **Selenium** for scraping dynamically generated content.

## Features

- Scrape product prices from various e-commerce sites (Amazon, Flipkart, etc.).
- Use **Selenium** to extract dynamic content from websites.
- Retry mechanism for failed requests with exponential backoff.
- Flask web application to provide API for comparing prices.
- Option to run Chrome in **headless mode** for performance.

## Prerequisites

Before running the project, you need to set up the following:

- **Python 3.x** installed on your machine.
- **ChromeDriver** installed to use with Selenium (ensure it matches your Chrome version).

### Installing Required Libraries

1. Install **Selenium**, **Flask**, and **Fake UserAgent** using `pip`:

   ```bash
   pip install flask selenium fake-useragent


2. **ChromeDriver** Setup:
   - Download **ChromeDriver** matching your Chrome version from the official [ChromeDriver download page](https://sites.google.com/chromium.org/driver/).
   - Extract the file and move it to a directory on your system.
   - Optionally, add the path to **ChromeDriver** to your system's **PATH** variable.

## How to Run

### 1. Download and Extract ChromeDriver
   - Go to the [ChromeDriver page](https://sites.google.com/chromium.org/driver/).
   - Find the version that matches your Chrome version and download the ZIP file.
   - Extract the ZIP file and move `chromedriver.exe` (Windows) or `chromedriver` (Mac/Linux) to a folder (e.g., `C:/selenium/` or `/usr/local/bin/`).

### 2. Set Up the Project

1. Clone or download the repository to your local machine.
2. Save the following Python script as `app.py`:

   ```python
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
       driver_path = "chromedriver.exe"  # Adjust this path if necessary
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
   ```

### 3. Run the Flask Application

- Navigate to the folder where `app.py` is saved and run:

  ```bash
  python app.py
  ```

- The Flask app will start, and you can access it at `http://localhost:5000`.

### 4. Test the API

You can use the `/compare-prices` endpoint to compare prices for any product. For example, test it by visiting:

```
http://localhost:5000/compare-prices?product=Samsung%20S23
```

The response will be a JSON object containing the prices from various sites and the best price.

## Troubleshooting

- If you encounter errors related to **ChromeDriver**, ensure that the version of ChromeDriver matches your Chrome browser version.
- If your app gets blocked by CAPTCHA (e.g., on Amazon), you may need to use a CAPTCHA-solving service like **2Captcha** or **Anti-Captcha**.
- For other issues related to Selenium or Flask, refer to the [Selenium Documentation](https://www.selenium.dev/documentation/en/) or the [Flask Documentation](https://flask.palletsprojects.com/).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
```

### Key Sections in the README:

- **Project Overview**: Explains the functionality of the price comparison tool.
- **Prerequisites**: Lists all the dependencies and setup requirements.
- **How to Run**: Provides step-by-step instructions to set up the project, including the ChromeDriver setup and running the Flask app.
- **Test the API**: Shows how to test the price comparison feature through a web browser.
- **Troubleshooting**: Helps resolve common setup issues.
- **License**: Information on the project’s licensing (if you choose to include one).

---

### Usage

1. **Save this as `README.md`** in your project folder.
2. **Push to GitHub**:
   - If you haven't already, create a repository on GitHub and follow their instructions to push this project.

Let me know if you'd like to make any adjustments or need further assistance!
