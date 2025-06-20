"""
Log message codes and their descriptions for the job market scraper system.
"""

ERROR_CODES = {
    "001": "An error occurred during job scraping",
    "002": "Failed to click element",
    "003": "Failed to login to LinkedIn",
    "004": "Error scraping LinkedIn job",
    "005": "Error collecting LinkedIn job links",
    "006": "Error in LinkedIn scraping process",
    "007": "Error scraping Rabota.md URL",
    "008": "Error fetching Rabota.md page",
    "009": "Error fetching Rabota.md page",
    "010": "Error in Rabota.md scraping process",
    "011": "Invalid JSON",
    "012": "Error sending to OpenAI",
    "013": "Error processing record",
    "014": "Error syncing occurrences",
    "015": "Error in data processing",
    "016": "Failed to scroll scrollable div child",
    "017": "Error verifying processed flags"
}

WARN_CODES = {
    "001": "No valid data to upsert",
    "002": "Scroll error",
    "003": "Error extracting job link",
    "004": "Failed to fetch page (status code error)",
    "005": "Failed to get content from OpenAI",
    "006": "Failed to extract JSON from content",
    "007": "Failed to parse JSON",
    "008": "Scrollable div child not found",
    "009": "No matching processed entry"
}

INFO_CODES = {
    "001": "Updated occurrences for URL with date",
    "002": "Skipping URL — already recorded for today",
    "003": "Inserted new job data",
    "004": "Starting Rabota.md scraping",
    "005": "Starting LinkedIn scraping",
    "006": "Current time is within UTC processing window",
    "007": "Current time outside UTC processing window",
    "008": "Successfully logged in to LinkedIn",
    "009": "Total unique URLs found for LinkedIn",
    "010": "Starting Rabota.md scraping process",
    "011": "Total unique URLs found for Rabota.md",
    "012": "Successfully processed record",
    "013": "Synced occurrences for URL",
    "014": "Processing record",
    "014": "Reset 'processed' to False "
}

DEBUG_CODES = {
    "001": "Modal closed successfully",
    "002": "Failed to extract criteria",
    "003": "Checking page",
    "004": "Checking page"
}

def get_message(level: str, code: str) -> str:
    """
    Get the message for a given log level and code.
    
    Args:
        level (str): Log level (ERROR, WARN, INFO, DEBUG)
        code (str): Three-digit code
        
    Returns:
        str: Message description or None if not found
    """
    code_maps = {
        "ERROR": ERROR_CODES,
        "WARN": WARN_CODES,
        "INFO": INFO_CODES,
        "DEBUG": DEBUG_CODES
    }
    
    return code_maps.get(level, {}).get(code, "Unknown message code") 