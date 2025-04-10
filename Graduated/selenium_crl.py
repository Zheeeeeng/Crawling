from selenium import webdriver
#from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin, urlparse
import requests
import csv
import time
from selenium.webdriver.chrome.service import Service

import os
# initialize Selenium WebDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  #  Headless mode
    chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration
    chrome_options.add_argument("--no-sandbox")  #  Disable the sandbox mode
    chrome_options.add_argument("--disable-dev-shm-usage")  # Solve the memory shortage problem

    # find ChromeDriver
    cache_dir = os.path.expanduser(r"~\.cache\selenium\chromedriver\win64")

    # Go through the directory and find the chromedriver.exe
    for root, dirs, files in os.walk(cache_dir):
        if "chromedriver.exe" in files:
            chromedriver_path = os.path.join(root, "chromedriver.exe")
            service = Service(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            return driver
    #service = Service(executable_path=r"C:\Users\郑慧琳\.cache\selenium\chromedriver\win64\134.0.6998.178/chromedriver.exe")
    #driver = webdriver.Chrome(service=service)
    #return driver



# check link status
def check_link(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        if resp.status_code in [404, 403, 500]:
            return resp.status_code
        return 200  # normal status
    except requests.RequestException:
        return None  # request failed

# extract all the links in the page
def get_links(driver, url):
    driver.get(url)
    time.sleep(2)  # wait for the page to load

    # extracts the href attribute of all <a> tags
    links = set()
    for element in driver.find_elements(By.TAG_NAME, "a"):
        href = element.get_attribute("href")
        if href:
            full_url = urljoin(url, href)
            parsed = urlparse(full_url)
            if parsed.netloc == urlparse(url).netloc:  # only processed links of the same domain name
                links.add(full_url)
    return links

# crawl the site and check the links
def selenium_crl(start_url, max_dep=3):
    driver = init_driver()
    visited = set()
    dead_links = []
    queue = [(start_url, 0)]  # use tuples to store urls and current depths

    while queue:
        url, dep = queue.pop(0)
        if url in visited or dep > max_dep:
            continue
        visited.add(url)
        print(f"Crawling: {url}")

        # extract all the links in the page
        links = get_links(driver, url)
        for link in links:
            if link not in visited:
                status = check_link(link)
                if status != 200:
                    dead_links.append({'source': url, 'dead_link': link, 'status': status})
                queue.append((link, dep + 1))  # added to the queue to continue climbing

    # close drive
    driver.quit()

    # Output results to CSV
    with open('dead_links_selenium.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['source', 'dead_link', 'status'])
        writer.writeheader()
        writer.writerows(dead_links)

    print("Finished. Dead links saved to dead_links_selenium.csv")
    return dead_links  # return dead link result






