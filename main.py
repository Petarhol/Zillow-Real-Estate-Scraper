from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from time import sleep

# --- CONFIGURATION ---
CHROME_DRIVER_PATH = "/Users/petarmacbook/Web Development Projects/chromedriver-mac-x64/chromedriver"
CHROME_BINARY_PATH = ("/Users/petarmacbook/Web Development Projects/chrome-mac-x64/Google Chrome for "
                      "Testing.app/Contents/MacOS/Google Chrome for Testing")
URL_LINK = ("https://docs.google.com/forms/d/e/1FAIpQLScpFDLnJiWog6enGhtZ374TZGlp6q7yCz1kZD9JCBjtftB2uQ/viewform?usp=header")

# --- SCRAPING WITH BEAUTIFULSOUP ---
try:
    response = requests.get(
        url="https://appbrewery.github.io/Zillow-Clone/",
        headers={
            "Accept-Language": "en-US",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/136.0.0.0 Safari/537.36"
        }
    )
    contents = response.text
    soup = BeautifulSoup(contents, "html.parser")
except requests.RequestException as e:
    print(f"Error fetching Zillow clone: {e}")
    soup = BeautifulSoup("", "html.parser")

addr_list, price_list, link_list = [], [], []

# --- PARSE ADDRESSES ---
try:
    addresses = soup.select('address[data-test="property-card-addr"]')
    for addr in addresses:
        addr = addr.text.strip()
        parts = [p.strip() for p in addr.split(',')]
        parts[-1] = parts[-1].split()[0]  # remove ZIP code
        addr = ', '.join(parts)
        if "|" not in addr:
            addr_list.append(addr)
        else:
            addr_list.append(addr.split('|')[-1].strip())
except Exception as e:
    print(f"Error parsing addresses: {e}")

# --- PARSE PRICES ---
try:
    prices = soup.select("div.PropertyCardWrapper")
    for price in prices:
        price_list.append(price.text.strip("\n +/mobd").split("+")[0].replace(",", ""))
except Exception as e:
    print(f"Error parsing prices: {e}")

# --- PARSE LINKS ---
for a in soup.find_all(name="a", class_="property-card-link"):
    link_list.append(a.get("href"))

# --- SELENIUM SETUP ---
try:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = CHROME_BINARY_PATH
    chrome_options.add_experimental_option("detach", True)
    service = Service(CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 20)
    driver.get(URL_LINK)
except WebDriverException as e:
    print(f"Selenium error: {e}")
    driver = None

# --- FILL GOOGLE FORM WITH SELENIUM ---
if driver:
    wait = WebDriverWait(driver, 20)
    for i in range(len(addr_list)):
        try:
            sleep(1)
            # Fill address
            answer_1 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-labelledby="i1 i4"]')))
            answer_1.send_keys(addr_list[i])

            # Fill price
            answer_2 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-labelledby="i6 i9"]')))
            answer_2.send_keys(price_list[i])

            # Fill link
            answer_3 = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'input[aria-labelledby="i11 i14"]')))
            answer_3.send_keys(link_list[i])

            # Submit form
            submit = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, 'div[role="button"]')))
            submit.click()

            # Confirm submission
            confirm = wait.until(ec.element_to_be_clickable((
                By.CSS_SELECTOR,
                'a[href="https://docs.google.com/forms/d/e/1FAIpQLScpFDLnJiWog6enGhtZ374TZGlp6q7yCz1kZD9JCBjtftB2uQ/viewform?usp=form_confirm"]'
            )))
            confirm.click()

            sleep(1)
        except TimeoutException:
            print(f"Timeout while filling form for entry {i}. Skipping...")
        except NoSuchElementException:
            print(f"Element not found for entry {i}. Skipping...")
        except Exception as e:
            print(f"Unexpected error at entry {i}: {e}")

    # Close driver after completion
    # driver.quit()
