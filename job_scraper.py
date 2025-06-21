from deduplicator import deduplicate_processed
from rabota_scraper import scrape_rabota_jobs
from linkedin_scraper import scrape_linkedin_jobs
from processor import process_data
from config import *
from datetime import datetime, time, timezone, timedelta
import logging

logger = logging.getLogger(__name__)

def is_within_processing_window():
    """Check if current time is within the processing window (16:30 to 00:30 UTC)."""
    now_utc = datetime.now(timezone.utc).time()
    start = time(16, 30)
    end = time(0, 30)
    return now_utc >= start or now_utc <= end

def main():
    """Main function to orchestrate the job scraping and processing workflow."""
    try:
        # Scrape jobs from Rabota.md
        logger.info("[INFO:004] Starting Rabota.md scraping")
        scrape_rabota_jobs(db_file=DB_FILE)
        
        # Scrape jobs from LinkedIn
        logger.info("[INFO:005] Starting LinkedIn scraping")
        scrape_linkedin_jobs(db_file=DB_FILE)

        # Process data if within the processing window
        if is_within_processing_window():
            logger.info("[INFO:006] Current time is within the UTC range 16:30 - 00:30. Processing data...")
            # Process Rabota.md data
            process_data(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE)
            # Process LinkedIn data
            process_data(source=TABLE_LINKEDIN_RAW, db_file=DB_FILE)

            # Deduplicate processed data
            deduplicate_processed(DB_FILE)
        else:
            logger.info("[INFO:007] Current time in Moldova is outside the UTC range. Skipping processing.")

    except Exception as e:
        logger.error(f"[ERROR:001] An error occurred during job scraping: {e}", exc_info=True)

if __name__ == "__main__":
    main()






