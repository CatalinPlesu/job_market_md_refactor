import json
import re
import pandas as pd
from tinydb import TinyDB, Query
from openai import OpenAI
from datetime import datetime
from config import *
from dotenv import load_dotenv
import os

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
        print(f"Invalid JSON: {e}")
        return None

def send_to_openai(data, context=CONTEXT, prompt=JOB_SCHEMA_PROMPTv2):
    """Sends data to OpenAI for processing."""
    client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
    try:
        json_string = json.dumps(data)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt + json_string},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error sending to OpenAI: {e}")
        return None

def process_record(record, source, db_file=DB_FILE):
    """Processes a single record using OpenAI and stores in processed_data table."""
    db = TinyDB(db_file)
    processed_table = db.table(TABLE_PROCESSED)
    
    raw_content = send_to_openai(record)
    if not raw_content:
        return None
    
    cleaned_content = clean_raw_content(raw_content)
    json_string = extract_json_from_content(cleaned_content)
    if not json_string:
        return None
    
    parsed_data = parse_json(json_string)
    if not parsed_data:
        return None
    
    parsed_data["date"] = record["date"]
    parsed_data["source"] = record["source"]
    parsed_data["occurrences"] = record["occurrences"]
    parsed_data["original_url"] = record["url"]

    processed_table.insert(parsed_data)
    return parsed_data


def sync_occurrences_from_raw_to_processed(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE):
    """For all raw records marked as processed, sync occurrences into the processed table."""
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
                print(f"Synced occurrences for: {record['url']}")

def process_data(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE):
    """Processes unprocessed records and syncs occurrences."""
    db = TinyDB(db_file)
    raw_table = db.table(source)

    for doc in raw_table.all():
        if not doc.get("processed", False):
            print(f"Processing record: {doc.get('vacancy-title', doc.get('job_title', 'Unknown'))}")
            process_record(doc, source, db_file)
            raw_table.update({"processed": True}, doc_ids=[doc.doc_id])

    sync_occurrences_from_raw_to_processed(source, db_file)
