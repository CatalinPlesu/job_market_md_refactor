import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}

def get_now_date():
    """Return current date as string in DD/MM/YYYY format."""
    return datetime.now().strftime("%d/%m/%Y")

def parse_date(date_str):
    """Convert string in DD/MM/YYYY format back to datetime object."""
    return datetime.strptime(date_str, "%d/%m/%Y")

def default_job_data(source, url):
    """Return a default job dictionary with shared metadata."""
    return {
        "url": url,
        "source": source,
        "processed": False,
        "occurrences": [get_now_date()],
        "date": get_now_date()
    }


def upsert_job_data(table, Job, data):
    """
    Check if a job URL exists in the database.
    - If new, insert data with today's date in 'occurrences'.
    - If exists, update 'occurrences' with today's date if not present.
    No return value.
    """
    if not data or 'url' not in data:
        logger.warning("[WARN:001] No valid data to upsert.")
        return

    current_date = get_now_date()
    url = data['url']
    existing = table.search(Job.url == url)

    if not existing:
        # New URL, initialize occurrences and insert
        occurrences = data.get('occurrences', [])
        if not isinstance(occurrences, list):
            occurrences = [occurrences]
        if current_date not in occurrences:
            occurrences.append(current_date)
        data['occurrences'] = occurrences
        table.insert(data)
        logger.info(f"[INFO:003] Inserted new job data for {url}")
        return

    # URL exists, update occurrences if needed
    record = existing[0]
    occurrences = record.get('occurrences', [])
    if not isinstance(occurrences, list):
        occurrences = [occurrences]

    if current_date not in occurrences:
        occurrences.append(current_date)
        table.update({'occurrences': occurrences}, Job.url == url)
        logger.info(f"[INFO:001] Updated occurrences for {url} with date {current_date}")
    else:
        logger.info(f"[INFO:002] Skipping {url} — already recorded for today")

