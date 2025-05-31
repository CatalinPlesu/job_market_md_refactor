from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import random
from datetime import datetime
from tinydb import TinyDB, Query
from dotenv import load_dotenv
import os

load_dotenv()
email = os.getenv("LINKEDIN_EMAIL")
password = os.getenv("LINKEDIN_PASSWORD")

from config import *
from utils import *

def clean_text(text):
    """Clean and normalize text."""
    if not text:
        return None
    return re.sub(r'\s+', ' ', text.strip())

def click_element(driver, selector, wait_time=2):
    """Try to click an element with proper waiting."""
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for element in elements:
            if element.is_displayed():
                driver.execute_script("arguments[0].click();", element)
                time.sleep(wait_time)
                return True
    except Exception as e:
        print(f"Failed to click {selector}: {e}")
    return False

def linkedin_login(driver, email, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)  # wait for redirect or cookie set


def scrape_linkedin_job(driver, url):
    """Scrape a specific LinkedIn job listing page."""
    job_data = default_job_data(source="linkedin.com", url=url)
    
    try:
        driver.get(url)
        time.sleep(2)
        
        for selector in [
            "button.modal__dismiss",
            "button.contextual-sign-in-modal__modal-dismiss",
            "button[aria-label='Dismiss']"
        ]:
            if click_element(driver, selector):
                print("Modal closed successfully")
                break
        
        for selector in [
            ".jobs-description__footer-button",
            "button[aria-label='Click to see more description']",
            "button.show-more-less-html__button",
            "button[aria-label='i18n_show_more']"
        ]:
            click_element(driver, selector)
        
        job_data['job_title'] = clean_text(driver.find_element(
            By.CSS_SELECTOR, "h1.top-card-layout__title, h1.job-details-jobs-unified-top-card__job-title, h1"
        ).text) if driver.find_elements(By.CSS_SELECTOR, "h1.top-card-layout__title, h1.job-details-jobs-unified-top-card__job-title, h1") else None
        
        job_data['company_name'] = clean_text(driver.find_element(
            By.CSS_SELECTOR, "a.topcard__org-name-link, .job-details-jobs-unified-top-card__company-name"
        ).text) if driver.find_elements(By.CSS_SELECTOR, "a.topcard__org-name-link, .job-details-jobs-unified-top-card__company-name") else None
        
        job_data['location'] = clean_text(driver.find_element(
            By.CSS_SELECTOR, ".topcard__flavor--bullet, .job-details-jobs-unified-top-card__bullet"
        ).text) if driver.find_elements(By.CSS_SELECTOR, ".topcard__flavor--bullet, .job-details-jobs-unified-top-card__bullet") else None
        
        job_data['job_description'] = clean_text(driver.find_element(
            By.CSS_SELECTOR, ".description__text, .jobs-description__content"
        ).text) if driver.find_elements(By.CSS_SELECTOR, ".description__text, .jobs-description__content") else None
        
        job_data['company_info'] = clean_text(driver.find_element(
            By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-info, .jobs-company__box"
        ).text) if driver.find_elements(By.CSS_SELECTOR, ".job-details-jobs-unified-top-card__company-info, .jobs-company__box") else None
        
        criteria_elements = driver.find_elements(By.CSS_SELECTOR, ".description__job-criteria-item")
        for elem in criteria_elements:
            try:
                label = elem.find_element(By.CSS_SELECTOR, "h3.description__job-criteria-subheader").text.strip()
                value = elem.find_element(By.CSS_SELECTOR, ".description__job-criteria-text").text.strip()
                if "Seniority" in label:
                    job_data['seniority_level'] = value
                elif "Employment" in label:
                    job_data['employment_type'] = value
                elif "Function" in label:
                    job_data['job_function'] = value
                elif "Industries" in label:
                    job_data['industries'] = value
            except Exception:
                continue
        
        job_data['skills'] = clean_text(driver.find_element(
            By.CSS_SELECTOR, ".job-details-how-you-match, .jobs-unified-top-card__job-insight"
        ).text) if driver.find_elements(By.CSS_SELECTOR, ".job-details-how-you-match, .jobs-unified-top-card__job-insight") else None
        
        return job_data
    
    except Exception as e:
        print(f"Error scraping LinkedIn job {url}: {e}")
        return None

def get_linkedin_job_links(driver, search_url):
    """Collect all LinkedIn job links from all paginated results."""
    job_links = set()

    try:
        driver.get(search_url)
        time.sleep(2)
        click_element(driver, "button.modal__dismiss")

        while True:
            # Scroll the jobs list container to load more jobs
            try:
                scrollable = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "scaffold-layout__list"))
                )
                for _ in range(5):
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable)
                    time.sleep(1)
            except Exception as e:
                print("Scroll error:", e)

            # Collect all job cards on the current page
            job_cards = driver.find_elements(By.CSS_SELECTOR, 'a.job-card-container__link')
            for card in job_cards:
                try:
                    url = card.get_attribute("href")
                    if url:
                        job_links.add(url)
                except Exception as e:
                    print(f"Error extracting job link: {e}")

            # Try to go to the next page
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button.jobs-search-pagination__button--next")
                if not next_button.is_enabled():
                    break
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
            except Exception:
                break

        return list(job_links)

    except Exception as e:
        print(f"Error collecting LinkedIn job links: {e}")
        return list(job_links)

def scrape_linkedin_jobs(db_file):
    db = TinyDB(db_file)
    table = db.table(TABLE_LINKEDIN_RAW)
    Job = Query()

    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    try:
        linkedin_login(driver, email, password)
        job_urls = get_linkedin_job_links(driver, URL_LINKEDIN)

        unique_urls = list(set(job_urls))
        print(f"Total unique URLs found for LinkedIn: {len(unique_urls)}")

        for url in unique_urls:
            if check_if_new_url(table, Job, url):
                data = scrape_linkedin_job(driver, url)
                insert_job_data(table, data)
                time.sleep(random.uniform(2, 10))

    finally:
        driver.quit()