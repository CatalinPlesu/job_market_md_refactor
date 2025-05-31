from datetime import datetime

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

def check_if_new_url(table, Job, url):
    """
    Check if a job URL is new or already exists in the database.
    If it exists, update its 'occurrences' field with today's date (if not already there).
    Returns True if the URL is new and should be scraped. False if already processed today.
    """
    current_date = get_now_date()
    existing = table.search(Job.url == url)

    if not existing:
        return True  # New URL, should be scraped and inserted

    # Update occurrences if current date not yet recorded
    record = existing[0]
    occurrences = record.get('occurrences', [])
    if not isinstance(occurrences, list):
        occurrences = [occurrences]

    if current_date not in occurrences:
        occurrences.append(current_date)
        table.update({'occurrences': occurrences}, Job.url == url)
        print(f"Updated occurrences for {url} with date {current_date}")
    else:
        print(f"Skipping {url} — already recorded for today")

    return False  # Not new, skip scraping

def insert_job_data(table, data):
    """
    Insert job data into the database.
    Assumes the data is for a new job URL.
    Initializes occurrences with today's date.
    """
    if not data:
        print("No data to insert.")
        return False

    current_date = get_now_date()
    occurrences = data.get('occurrences', [])
    if not isinstance(occurrences, list):
        occurrences = [occurrences]

    if current_date not in occurrences:
        occurrences.append(current_date)

    data['occurrences'] = occurrences
    table.insert(data)
    print(f"Inserted new job data for {data['url']}")
    return True
