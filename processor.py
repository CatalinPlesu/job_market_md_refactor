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

def send_to_openai(data, prompt=JOB_SCHEMA_PROMPT):
    """Sends data to OpenAI for processing."""
    client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")
    try:
        json_string = json.dumps(data)
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": prompt + json_string},
            ],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error sending to OpenAI: {e}")
        return None

def deduplicate_table(db, table_name, title_field, company_field):
    """Deduplicates entries in a TinyDB table."""
    table = db.table(table_name)
    Job = Query()
    df = pd.DataFrame(table.all())
    
    if df.empty:
        return
    
    df['datetime'] = pd.to_datetime(df['date'])
    df['processed'] = df.get('processed', False)
    df = df.sort_values(by=['datetime', 'processed'], ascending=[True, False])
    df_clean = df.drop_duplicates(subset=[title_field, company_field], keep='first')
    df_clean = df_clean.drop(columns=['datetime'])
    
    table.truncate()
    table.insert_multiple(df_clean.to_dict('records'))

def process_record(record, source, db_file=DB_FILE):
    """Processes a single record using OpenAI and stores in processed_data table."""
    db = TinyDB(db_file)
    processed_table = db.table(TABLE_PROCESSED)
    
    data = {
        "sidebar": record.get("sidebar", []),
        "vacancy_title": record.get("vacancy-title", record.get("job_title", "")),
        "company_title": record.get("company-title", record.get("company_name", "")),
        "job_description": record.get("job_description", ""),
        "company_info": record.get("company_info", ""),
        "location": record.get("location", "")
    }
    
    raw_content = send_to_openai(data)
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
    parsed_data["time"] = record["time"]
    parsed_data["source"] = source
    parsed_data["original_url"] = record["url"]
    
    processed_table.insert(parsed_data)
    return parsed_data

def process_data(source=TABLE_ROBOTA_MD_RAW, db_file=DB_FILE):
    """Processes unprocessed records from a source table."""
    db = TinyDB(db_file)
    raw_table = db.table(source)
    Job = Query()
    
    unprocessed = raw_table.search(Job.processed == False)
    for record in unprocessed:
        print(f"Processing record: {record.get('vacancy-title', record.get('job_title', 'Unknown'))}")
        process_record(record, source, db_file)
        raw_table.update({'processed': True}, Job.url == record['url'])
    
    title_field = "vacancy-title" if source == TABLE_ROBOTA_MD_RAW else "job_title"
    company_field = "company-title" if source == TABLE_ROBOTA_MD_RAW else "company_name"
    deduplicate_table(db, source, title_field, company_field)
    deduplicate_table(db, TABLE_PROCESSED, "title", "company_info.name")