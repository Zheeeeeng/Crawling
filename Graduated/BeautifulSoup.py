import requests
from bs4 import BeautifulSoup
import validators
import csv
from urllib.parse import urljoin, urlparse
import time
import concurrent.futures
from functools import lru_cache

# cache checked link status to avoid duplicate requests
@lru_cache(maxsize=1000)
def check_link(url):
    try:
        resp = requests.head(url, allow_redirects=True, timeout=5)
        if resp.status_code in [404, 403, 500]:
            return resp.status_code
        return 200  # normal status
    except requests.RequestException:
        return None  #request failed

# extract all links from the page, leaving only the HTML page
def get_links(url):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = set()
        for tag in soup.find_all('a', href=True):
            href = tag.get('href')
            # convert relative links to absolute links
            full_url = urljoin(url, href)
            # only process valid HTML links
            if validators.url(full_url):
                parsed = urlparse(full_url)
                # only processed  links to the same domain name
                if parsed.netloc == urlparse(url).netloc and (parsed.path.endswith(('.html', '.htm')) or not parsed.path.split('.')[-1]):
                    links.add(full_url)
        return links
    except requests.RequestException:
        return set()

# multithreading checks link status
def check_concurrent(links, source_url, dead_links):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_link = {executor.submit(check_link, link): link for link in links}
        for future in concurrent.futures.as_completed(future_to_link):
            link = future_to_link[future]
            try:
                status = future.result()
                if status != 200:
                    dead_links.append({'source': source_url, 'dead_link': link, 'status': status})
            except Exception as e:
                print(f"Error checking link {link}: {e}")

# crawl the site and check the links
def beautifulsoup_crl(start_url, max_depth=50, delay=1):
    visited = set()
    dead_links = []
    queue = [(start_url, 0)]  # use tuples to store urls and current depths

    while queue:
        url, depth = queue.pop(0)
        if url in visited or depth > max_depth:
            continue
        visited.add(url)
        print(f"Crawling: {url}")

        # get the links of url
        links = get_links(url)
        # multithreading checks link status
        check_concurrent(links, url, dead_links)

        # add a new link to the queue, increasing the depth by 1
        for link in links:
            if link not in visited:
                queue.append((link, depth + 1))

        # add a delay to avoid triggering anti-reptile mechanisms
        time.sleep(delay)

    # output results to CSV
    with open('dead_links_beautifulsoup.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['source', 'dead_link', 'status'])
        writer.writeheader()
        writer.writerows(dead_links)

    print("Finished. Dead links saved to dead_links_beautifulsoup.csv")
    return dead_links  # return the dead link result