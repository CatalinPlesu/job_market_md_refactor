import json
import re
import pandas as pd
from tinydb import TinyDB, Query
from openai import OpenAI
from datetime import datetime
from config import *
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

load_dotenv()
API_KEY = os.getenv("API_KEY")

def clean_raw_content(raw_content):
    """Cleans the raw content by removing JSON markdown."""
    return re.sub(r'```json\n|\n```', '', raw_content)

def extract_json_from_content(cleaned_content):
    """Extracts the first valid JSON object from the cleaned content."""
    pattern = r'\{.*\}'
    match = re.search(pattern, cleaned_content, re.DOTALL)
    return match.group(0) if match else None

def parse_json(json_string):
    """Parses the extracted JSON string into a Python dictionary."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"[ERROR:011] Invalid JSON: {e}")
        return None

def send_to_openai(data, context=CONTEXT, prompt=JOB_SCHEMA_PROMPTv2):
    """Sends data to OpenAI for processing."""
    client = OpenAI(api_key=API_KEY, base_url=API_URL)
    try:
        fields_to_remove = ['date', 'occurrences', 'processed', 'source', 'url']
        cleaned_data = {k: v for k, v in data.items() if k not in fields_to_remove}
        json_string = json.dumps(cleaned_data)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt + json_string},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"[ERROR:012] Error sending to OpenAI: {e}")
        return None

def process_record(record, source, db_file=DB_FILE):
    """Processes a single record using OpenAI and stores in processed_data table."""
    try:
        db = TinyDB(db_file)
        processed_table = db.table(TABLE_PROCESSED)
        
        raw_content = send_to_openai(record)
        if not raw_content:
            logger.warning(f"[WARN:005] Failed to get content from OpenAI for record: {record.get('url', 'Unknown URL')}")
            return None
        
        cleaned_content = clean_raw_content(raw_content)
        json_string = extract_json_from_content(cleaned_content)
        if not json_string:
            logger.warning(f"[WARN:006] Failed to extract JSON from content for record: {record.get('url', 'Unknown URL')}")
            return None
        
        parsed_data = parse_json(json_string)
        if not parsed_data:
            logger.warning(f"[WARN:007] Failed to parse JSON for record: {record.get('url', 'Unknown URL')}")
            return None
        
        parsed_data["date"] = record["date"]
        parsed_data["source"] = record["source"]
        parsed_data["occurrences"] = record["occurrences"]
        parsed_data["original_url"] = record["url"]

        processed_table.insert(parsed_data)
        logger.info(f"[INFO:012] Successfully processed record: {record.get('url', 'Unknown URL')}")
        return parsed_data
    except Exception as e:
        logger.error(f"[ERROR:013] Error processing record: {e}", exc_info=True)
        return None

def sync_occurrences_from_raw_to_processed(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE):
    """For all raw records marked as processed, sync occurrences into the processed table."""
    try:
        db = TinyDB(db_file)
        raw_table = db.table(source)
        processed_table = db.table(TABLE_PROCESSED)

        Job = Query()
        ProcessedJob = Query()

        processed_raw = raw_table.search(Job.processed == True)

        for record in processed_raw:
            existing = processed_table.get(
                (ProcessedJob.date == record["date"]) &
                (ProcessedJob.original_url == record["url"])
            )

            if existing:
                raw_occurrences = set(record.get("occurrences", []))
                proc_occurrences = set(existing.get("occurrences", []))
                merged = list(proc_occurrences.union(raw_occurrences))

                if merged != existing.get("occurrences", []):
                    processed_table.update({"occurrences": merged}, doc_ids=[existing.doc_id])
                    logger.info(f"[INFO:013] Synced occurrences for: {record['url']}")
    except Exception as e:
        logger.error(f"[ERROR:014] Error syncing occurrences: {e}", exc_info=True)

def verify_processed_flags(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE, fix=False):
    """
    Verifies if records marked as processed in the raw table have a matching entry in the processed table.
    Logs any inconsistencies. If fix=True, sets 'processed' to False for invalid records.
    Shows a simple progress bar without external libraries.
    """
    try:
        db = TinyDB(db_file)
        raw_table = db.table(source)
        processed_table = db.table(TABLE_PROCESSED)

        Job = Query()
        ProcessedJob = Query()

        processed_records = raw_table.search(Job.processed == True)
        total = len(processed_records)
        broken_doc_ids = []

        def print_progress(current, total, bar_width=40):
            progress = int((current / total) * bar_width)
            bar = '#' * progress + '-' * (bar_width - progress)
            print(f"\r[VERIFY] [{bar}] {current}/{total}", end='', flush=True)

        for idx, record in enumerate(processed_records, start=1):
            url = record.get("url")
            date = record.get("date")
            if not url or not date:
                continue

            match = processed_table.get(
                (ProcessedJob.original_url == url) & (ProcessedJob.date == date)
            )

            if not match:
                logger.warning(f"[WARN:009] No matching processed entry for: {url} on {date}")
                broken_doc_ids.append(record.doc_id)

            print_progress(idx, total)

        print()  # move to next line after progress bar

        if fix and broken_doc_ids:
            raw_table.update({"processed": False}, doc_ids=broken_doc_ids)
            logger.info(f"[INFO:016] Reset 'processed' to False for {len(broken_doc_ids)} records")

        logger.info(f"[INFO:017] Verified {total} records. Invalid: {len(broken_doc_ids)}.")

    except Exception as e:
        logger.error(f"[ERROR:017] Error verifying processed flags: {e}", exc_info=True)


def process_data(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE):
    """Processes unprocessed records and syncs occurrences."""
    try:
        db = TinyDB(db_file)
        raw_table = db.table(source)

        for doc in raw_table.all():
            if not doc.get("processed", False):
                logger.info(f"[INFO:014] Processing record: {doc.get('vacancy-title', doc.get('job_title', 'Unknown'))}")
                process_record(doc, source, db_file)
                raw_table.update({"processed": True}, doc_ids=[doc.doc_id])

        sync_occurrences_from_raw_to_processed(source, db_file)
    except Exception as e:
        logger.error(f"[ERROR:015] Error in data processing: {e}", exc_info=True)
