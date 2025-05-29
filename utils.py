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
        "occurrences": [],
        "date": get_now_date()
    }

def insert_if_new(table, Job, url, data):
    """Insert job data if URL hasn't already been processed.
    Adds current date (dd/mm/yyyy) uniquely to occurrences list in DB.
    """
    if not data:
        print(f"No data to insert for {url}")
        return False

    current_date = get_now_date()

    existing = table.search(Job.url == url)
    if not existing:
        # For new entries, add occurrences list with current_date
        occurrences = data.get('occurrences', [])
        if not isinstance(occurrences, list):
            occurrences = [occurrences]
        if current_date not in occurrences:
            occurrences.append(current_date)
        data['occurrences'] = occurrences

        table.insert(data)
        print(f"Saved data for {url}")
        return True
    else:
        # For existing entries, update occurrences field in DB
        record = existing[0]
        occurrences = record.get('occurrences', [])
        if not isinstance(occurrences, list):
            occurrences = [occurrences]
        if current_date not in occurrences:
            occurrences.append(current_date)
            table.update({'occurrences': occurrences}, Job.url == url)
            print(f"Updated occurrences for {url} with date {current_date}")
            return True
        else:
            print(f"Skipping already processed URL: {url} (date already recorded)")
            return False
