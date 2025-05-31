# %%
from rabota_scraper import scrape_rabota_jobs
from linkedin_scraper import scrape_linkedin_jobs
from processor import process_data
from config import *

# import importlib
# import config
# importlib.reload(config)

# %%
# Scrape jobs from Rabota.md
scrape_rabota_jobs(db_file=DB_FILE)

# %%
# Scrape jobs from LinkedIn
scrape_linkedin_jobs(db_file=DB_FILE)

# %%
# Process Rabota.md data
process_data(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE)

# %%
# Process LinkedIn data
process_data(source=TABLE_LINKEDIN_RAW, db_file=DB_FILE)

# %%



