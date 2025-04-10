import requests
from bs4 import BeautifulSoup
import validators
import csv
from urllib.parse import urljoin, urlparse
from multiprocessing import Process, Manager, Queue, freeze_support, Pool

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
def get_link(url):
    try:
        resp = requests.get(url, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')
        links = set()
        for tag in soup.find_all('a', href=True):
            href = tag.get('href')
            full_url = urljoin(url, href)
            if validators.url(full_url):
                parsed = urlparse(full_url)
                if parsed.netloc == urlparse(url).netloc and (parsed.path.endswith(('.html', '.htm')) or not parsed.path.split('.')[-1]):
                    links.add(full_url)
        return links
    except requests.RequestException:
        return set()

# multi-process crawl task
def crl_task(url, visited, dead_links, max_dep, curr_dep):
    if url in visited or curr_dep > max_dep:
        return
    visited.append(url)
    print(f"Crawling: {url}")

    links = get_link(url)
    with Pool(processes=4) as pool:  #use 4 processes
        statuses = pool.map(check_link, links)

    for link, status in zip(links, statuses):
        if status != 200:
            dead_links.append({'source': url, 'dead_link': link, 'status': status})
        if link not in visited:
            crl_task(link, visited, dead_links, max_dep, curr_dep + 1)

# run the crawler task in a separate process
def run_crl(start_url, visited, dead_links, max_dep, result_queue):
    crl_task(start_url, visited, dead_links, max_dep, 0)
    result_queue.put(list(dead_links))  # put the result into the queue


def multiprocessing_crl(start_url, max_dep=3):
    manager = Manager()
    visited = manager.list()
    dead_links = manager.list()

    # create a queue for passing results
    result_queue = Queue()

    # create and start a process
    crl_pro = Process(target=run_crl, args=(start_url, visited, dead_links, max_dep, result_queue))
    crl_pro.start()
    crl_pro.join()  # wait for finish

    # get the result from the queue
    result = result_queue.get()

    # output results to CSV
    with open('dead_links_multiprocessing.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['source', 'dead_link', 'status'])
        writer.writeheader()
        writer.writerows(result)

    print("Finished. Dead links saved to dead_links_multiprocessing.csv")
    return result  # return dead link result

# make sure multiprocess code runs correctly in Windows
if __name__ == "__main__":
    freeze_support()
    multiprocessing_crl("https://www.scnu.edu.cn/")