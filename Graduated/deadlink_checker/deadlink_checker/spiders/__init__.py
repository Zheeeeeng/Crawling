import scrapy
from urllib.parse import urljoin, urlparse
import validators
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import time
import psutil
class DeadlinkSpider(scrapy.Spider):
    name = "deadlink"
    custom_settings = {
        "DEPTH_LIMIT": 3,  # limit climbing depth
        "DOWNLOAD_DELAY": 1,  # request delay
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    }

    def __init__(self, start_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [start_url]  # set the start url dynamically
        self.seen = set()  # records visited links

    def parse(self, response):
        # check the current page status
        if response.status in [404, 403, 500]:
            yield {
                'source': response.request.headers.get('Referer', b'').decode('utf-8'),
                'dead_link': response.url,
                'status': response.status,
            }

        # extract all the links in the page
        for link in response.css('a::attr(href)').getall():
            full_url = urljoin(response.url, link)
            if validators.url(full_url):
                parsed = urlparse(full_url)
                if parsed.netloc == urlparse(response.url).netloc:  # filter only domain names
                    if full_url not in self.seen:  # check for access
                        self.seen.add(full_url)  # mark as visited
                        yield scrapy.Request(full_url, callback=self.parse, errback=self.handle_error)

    # handling the request failed
    def handle_error(self, fail):
        if fail.value.response:
            yield {
                'source': fail.request.headers.get('Referer', b'').decode('utf-8'),
                'dead_link': fail.request.url,
                'status': fail.value.response.status,
            }


def scrapy_crl(start_url):
    start_time = time.time()
    initial_mem = psutil.virtual_memory().used / 1024 / 1024

    if os.path.exists("dead_links_scrapy.csv"):
        os.remove("dead_links_scrapy.csv")

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # get Scrapy project Settings
    settings = get_project_settings()
    settings.set("FEEDS", {
        "dead_links_scrapy.csv": {
            "format": "csv",
            "fields": ["source", "dead_link", "status"],
        }
    })

    settings.set("INSTALL_SIGNAL_HANDLERS", False)

    process = CrawlerProcess(settings)
    process.crawl(DeadlinkSpider, start_url=start_url)
    process.start()


    end_time = time.time()
    peak_mem = psutil.virtual_memory().used / 1024 / 1024

    print(f"\n[performance report] Scrapy method:")
    print(f"- Time taken: {end_time - start_time:.2f}second")
    print(f"- Memory usage: Initial {initial_mem:.1f}MB → Peak {peak_mem:.1f}MB")
    print(f"- Number of CPU cores used: {psutil.cpu_count(logical=False)}/{psutil.cpu_count()}")

    # read the result and filter invalid rows
    try:
        with open("dead_links_scrapy.csv", "r", encoding="utf-8") as file:
            import csv
            reader = csv.DictReader(file)
            results = []
            for row in reader:

                if row['source'] != 'source' and row['dead_link'] != 'dead_link' and row['status'] != 'status':
                    results.append(row)
            return results
    except FileNotFoundError:
        return None