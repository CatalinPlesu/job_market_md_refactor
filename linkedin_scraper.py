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
from utils import default_job_data, insert_if_new

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
    """Collect all LinkedIn job links."""
    job_links = []
    
    try:
        driver.get(search_url)
        time.sleep(2)
        click_element(driver, "button.modal__dismiss")

        previous_count = 0
        retries = 0
        max_retries = 10

        while retries < max_retries:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            try:
                see_more = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.infinite-scroller__show-more-button"))
                )
                driver.execute_script("arguments[0].click();", see_more)
                time.sleep(2)
            except:
                pass

            jobs = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")
            current_count = len(jobs)

            if current_count > previous_count:
                previous_count = current_count
                retries = 0
            else:
                retries += 1

        # ✅ Extract job URLs here
        job_cards = driver.find_elements(By.CSS_SELECTOR, "ul.jobs-search__results-list li")
        for card in job_cards:
            try:
                link_elem = card.find_element(By.CSS_SELECTOR, "a.base-card__full-link")
                url = link_elem.get_attribute("href")
                if url:
                    job_links.append(url)
            except Exception as e:
                print(f"Failed to extract link from a job card: {e}")
        
        return job_links

    except Exception as e:
        print(f"Error collecting LinkedIn job links: {e}")
        return job_links

def scrape_linkedin_jobs(db_file):
    db = TinyDB(db_file)
    table = db.table(TABLE_LINKEDIN_RAW)
    Job = Query()

    options = Options()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(options=options)

    try:
        linkedin_login(driver, email, password)
        job_urls = get_linkedin_job_links(driver, URL_LINKEDIN)

        unique_urls = list(set(job_urls))
        print(f"Total unique URLs found for LinkedIn: {len(unique_urls)}")

        for url in unique_urls:
            job_data = scrape_linkedin_job(driver, url)
            wait = insert_if_new(table, Job, url, job_data)
            if wait:
                time.sleep(random.uniform(2, 10))
    finally:
        driver.quit()