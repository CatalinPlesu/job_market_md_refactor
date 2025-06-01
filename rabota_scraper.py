import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from datetime import datetime
from tinydb import TinyDB, Query
import logging

logger = logging.getLogger(__name__)

from config import *
from utils import *

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

def scrape_rabota_page(url):
    """Scrape a single Rabota.md job page."""
    classes_to_extract = ["sidebar", "vacancy-content", "vacancy-title", "company-title"]
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        extracted = default_job_data(source="robota.md", url=url)

        for class_name in classes_to_extract:
            elements = soup.find_all(class_=class_name)
            texts = [el.get_text(separator="\n", strip=True) for el in elements]
            if class_name in ["vacancy-title", "company-title"]:
                extracted[class_name] = texts[0] if texts else None
            else:
                extracted[class_name] = texts

        return extracted

    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping {url}: {e}")
        return None

def get_rabota_pages(base_url):
    """Discover all pages for Rabota.md."""
    page_number = 1
    all_pages = []

    while True:
        url = f"{base_url}{page_number}"
        logger.debug(f"Checking page: {url}")
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                break
            all_pages.append(url)
            page_number += 1
            time.sleep(2.1)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching page {url}: {e}")
            break
    return all_pages

def get_rabota_job_urls(page_url):
    """Extract job URLs from a Rabota.md page."""
    logger.debug(f"Checking page: {page_url}")
    try:
        res = requests.get(page_url, headers=headers)
        if res.status_code != 200:
            logger.warning(f"Failed to fetch page {page_url} (status code: {res.status_code}).")
            return []
        
        soup = BeautifulSoup(res.text, 'html.parser')
        job_links = soup.find_all('a', class_='vacancyShowPopup')
        urls = [urljoin(page_url, link['href']) for link in job_links if 'href' in link.attrs]
        time.sleep(2.1)
        return urls
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching page {page_url}: {e}")
        return []

def scrape_rabota_jobs(db_file=DB_FILE):
    """Main function to scrape Rabota.md job listings and store in TinyDB."""
    try:
        db = TinyDB(db_file)
        table = db.table(TABLE_ROBOTA_MD_RAW)
        Job = Query()

        logger.info("Starting Rabota.md scraping process")
        all_pages = get_rabota_pages(URL_ROBOTA_MD)
        all_job_urls = []
        
        for page_url in all_pages:
            job_urls = get_rabota_job_urls(page_url)
            all_job_urls.extend(job_urls)

        unique_urls = list(set(all_job_urls))
        logger.info(f"Total unique URLs found for Rabota.md: {len(unique_urls)}")

        for url in unique_urls:
            if check_if_new_url(table, Job, url):
                data = scrape_rabota_page(url)
                insert_job_data(table, data)
                
    except Exception as e:
        logger.error(f"Error in Rabota.md scraping process: {e}", exc_info=True)