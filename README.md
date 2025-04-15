def generate_readme():
    readme_content = """# SCNU Dead Link Checker

## Project Overview
This project provides a multi-method web crawler for detecting dead links on the South China Normal University (SCNU) website. It implements four distinct crawling approaches:

- **BeautifulSoup**: Lightweight HTML parser for static pages
- **Selenium**: Browser automation for dynamic content
- **Scrapy**: Scalable framework for large-scale crawling
- **Multiprocessing**: CPU-optimized parallel processing

## Installation

### Prerequisites
- Python 3.9+
- ChromeDriver 134.0.6998.178 ([Download](https://storage.googleapis.com/chrome-for-testing-public/134.0.6998.178/win64/chromedriver-win64.zip))

### Install dependencies
```bash
pip install -r requirements.txt
