import logging
from tinydb import TinyDB, Query
from datetime import datetime
from config import *

logger = logging.getLogger(__name__)

# Fields to group by (for identifying duplicates)
GROUP_BY_FIELDS = [
    "title", "salary_min_eur", "salary_max_eur", "salary_currency",
    "minimum_education", "languages", "experience",
    "company_name", "company_size"
]

# Fields that should be merged as unique lists
LIST_FIELDS = [
    "skills", "soft_skills", "benefits", "job_type", "categories", "occurrences", "languages"
]

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d/%m/%Y")
    except Exception:
        return None

def deduplicate_processed(db_file):
    db = TinyDB(db_file)
    processed_table = db.table(TABLE_PROCESSED)
    raw_tables = {
        "robota.md": db.table(TABLE_ROBOTA_MD_RAW),
        "linkedin.com": db.table(TABLE_LINKEDIN_RAW)
    }

    records = processed_table.all()
    logger.info("[INFO:018] Loaded %d processed records", len(records))

    groups = {}
    for rec in records:
        key = tuple(
            rec.get(f) if not isinstance(rec.get(f), list) else tuple(sorted(rec.get(f)))
            for f in GROUP_BY_FIELDS
        )
        groups.setdefault(key, []).append(rec)

    logger.info("[INFO:019] Found %d unique groups by key fields", len(groups))

    for key, group_records in groups.items():
        if len(group_records) <= 1:
            continue  # no duplicates

        logger.info("[INFO:020] Processing duplicate group with %d records", len(group_records))

        group_records.sort(key=lambda r: parse_date(r.get("date")) or datetime.max)
        canonical = group_records[0]

        merged_occurrences = set(canonical.get("occurrences", []))
        merged_dates = [canonical.get("date")]

        for dup in group_records[1:]:
            merged_occurrences.update(dup.get("occurrences", []))
            merged_dates.append(dup.get("date"))

            for field in LIST_FIELDS:
                canonical_val = set(canonical.get(field) or [])
                dup_val = set(dup.get(field) or [])
                merged = canonical_val.union(dup_val)
                if merged:
                    canonical[field] = list(merged)

        earliest_date = min([d for d in merged_dates if d], default=canonical.get("date"))
        canonical["date"] = earliest_date
        canonical["occurrences"] = list(merged_occurrences)

        processed_table.update(canonical, doc_ids=[canonical.doc_id])

        to_remove_doc_ids = [dup.doc_id for dup in group_records[1:]]
        processed_table.remove(doc_ids=to_remove_doc_ids)
        logger.info("[INFO:021] Removed %d duplicate processed records", len(to_remove_doc_ids))

        for dup in group_records[1:]:
            source = dup.get("source")
            original_url = dup.get("original_url")
            if source not in raw_tables or not original_url:
                continue
            raw_table = raw_tables[source]

            RawQuery = Query()
            raw_record = raw_table.get(RawQuery.url == original_url)
            if raw_record is None:
                logger.warning("raw_record is None for URL: %s", original_url)
            elif raw_record.get("occurrences") is None:
                logger.warning("raw_record.occurrences is None for URL: %s", original_url)
            if raw_record:
                raw_occurrences = set(raw_record.get("occurrences") or [])
                merged_occurrences.update(raw_occurrences)

                raw_table.remove(doc_ids=[raw_record.doc_id])
                logger.info("[INFO:022] Removed duplicate raw record with URL: %s", original_url)

        canonical["occurrences"] = list(merged_occurrences)
        processed_table.update(canonical, doc_ids=[canonical.doc_id])

    logger.info("[INFO:023] Deduplication completed.")

if __name__ == "__main__":
    import sys
    import os
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python deduplicator.py <path_to_db.json>")
        sys.exit(1)

    db_file = sys.argv[1]
    if not os.path.exists(db_file):
        print(f"DB file not found: {db_file}")
        sys.exit(1)

    deduplicate_processed(db_file)
