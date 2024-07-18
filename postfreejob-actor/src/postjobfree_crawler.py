import requests
import json
import random
import time
from lxml import html
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent
import re
from functools import reduce

# Load XPath configurations from config file
config = {
    "job_title": {
        "value": "Delivery Driver",
        "xpath": "//h1"
    },
    "company_name": {
        "value": "Ivantis Group, Inc.",
        "xpath": "//span[@class='colorCompany']"
    },
    "location": {
        "value": "Nottingham, MD (White Marsh Area)",
        "xpath": "//div[@class='innercontent']//div[@class='labelHeader'][contains(text(), 'Location:')]/following-sibling::a[@class='colorLocation']"
    },
    "description": {
        "value": "This position is responsible for performing part-time janitorial services for government client offices in Nottingham, MD. We offer on the job paid training.",
        "xpath": "//h4[contains(text(),'Description:')]/following-sibling::div[@class='normalText']"
    },
  
    
}

# Headers with random user agents
ua = UserAgent()

# Function to fetch and parse a URL
def fetch_url(url):
    retries = 5
    for _ in range(retries):
        try:
            headers = {'User-Agent': ua.random}
            response = requests.get(url, headers=headers)
            tree = html.fromstring(response.text)
            return url, tree
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            time.sleep(random.choice([4, 7]))  # Random sleep between retries
    return url, None

# Function to scrape job details from a parsed HTML tree
def scrape_job_details(url, tree):
    job_details = {"url": url}
    for key, value in config.items():
        try:
            element = tree.xpath(value['xpath'])
            if element:
                # Strip HTML tags using regex
                clean_text = re.sub(r'<.*?>', '', element[0].text_content().strip())
                 # Remove \r\n characters
                clean_text = clean_text.replace('\r\n', ' ')
                job_details[key] = clean_text
            else:
                job_details[key]=None

            # job_details[key] = element[0].text_content().strip() if element else None
        except Exception as e:
            print(f"Error extracting {key}: {e}")
            job_details[key] = None
    return job_details

# Main function to handle threading and JSON output
def crawl(location="United States", radius=25, keyword="python"):
    urls =listing_page(location, radius, keyword)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(fetch_url, urls))
    
    job_details_list = [scrape_job_details(url, tree) for url, tree in results if tree is not None]
    
    # Save to JSON
    with open('postjobfree_crawler.json', 'w', encoding='utf-8') as output_file:
        json.dump(job_details_list, output_file, ensure_ascii=False, indent=4)
    
    return job_details_list

def get_list_urls(url):
    print(f'Running page >> {url}')
    _, response = fetch_url(url)
    items = response.xpath("//div/h3//a/@href")
    if items:
        items = list(set(items))
        urls = [f'https://www.postjobfree.com{item}' for item in items]
        return urls
    else:
        []


def listing_page(location, radius, keyword):
    page_number = 1
    total_urls = list()
    total_limit_pages = 50 # Seems like it doesn't show more than 500
    keyword = '+'.join(keyword.split())
    location = '+'.join(location.split())
    url = f'https://www.postjobfree.com/jobs?q={keyword}&l={location}&radius={radius}&p={page_number}'
    _, response = fetch_url(url)
    items = response.xpath("//div/h3//a/@href")
    total_count = response.xpath("//td[contains(text(),'Jobs')]/b/text()")[-1] if response.xpath("//td[contains(text(),'Jobs')]/b/text()") else 0
    total_pages = int(total_count) // 10 
    if total_pages > total_limit_pages:
        total_pages = total_limit_pages
    listing_urls = [f'https://www.postjobfree.com/jobs?q={keyword}&l={location}&radius={radius}&p={page_number}' for page_number in range(2,total_pages+1)]
    
    items = list(set(items))
    urls = [f'https://www.postjobfree.com{item}' for item in items]
    total_urls.extend(urls)
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(get_list_urls, listing_urls))
    
    job_urls = reduce(lambda x, y: x + y, results, [])
    total_urls.extend(job_urls)
    
    return total_urls

if __name__ == "__main__":
    crawl()
