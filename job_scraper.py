# %%
from rabota_scraper import scrape_rabota_jobs
from linkedin_scraper import scrape_linkedin_jobs
from processor import process_data
from config import *
from datetime import datetime, time, timezone, timedelta

# Scrape jobs from Rabota.md
scrape_rabota_jobs(db_file=DB_FILE)
# Scrape jobs from LinkedIn
scrape_linkedin_jobs(db_file=DB_FILE)


# Get current UTC time as time object
now_utc = datetime.now(timezone.utc).time()
# Define UTC range (16:30 to 00:30 next day)
start = time(16, 30)
end = time(0, 30)

if now_utc >= start or now_utc <= end:
    # In this period DeepSeek has discount price 50% off
    print("Current time is within the UTC range 16:30 - 00:30.")
    # Process Rabota.md data
    process_data(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE)
    # Process LinkedIn data
    process_data(source=TABLE_LINKEDIN_RAW, db_file=DB_FILE)
else:
    print("Current time in Moldova is outside the UTC range.")






