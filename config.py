DB_FILE = "data.json"

# Table name constants
TABLE_ROBOTA_MD_RAW = "robota_md_raw_data"
TABLE_LINKEDIN_RAW = "linkedin_raw_data"
TABLE_PROCESSED = "processed_data"

# Base URL constants
URL_ROBOTA_MD = "https://www.rabota.md/ro/vacancies/category/it/developers/"
URL_LINKEDIN = "https://www.linkedin.com/jobs/search/?keywords=developer&location=Moldova"

JOB_SCHEMA_PROMPT = """
Keep values lowercase, generic and english only so they match other similar posts:
Extract the following minimal job market data from the following job postings into a JSON object. This is for market observation, not job-seeking.
Try to identify as many key words as possible, especially for tech and soft requirements.
{
  "title": "job title",
  "min_salary": null or number,
  "max_salary": null or number,
  "salary_currency": "mdl" | "eur" | "usd" or null,
  "degree": "degree requirements",
  "languages": ["english", "french", "romanian", "russian"],
  "exp": null or minimum experience in years,
  "tech": ["technology1", "technology2", "hard skill3"],
  "soft": ["soft skill1", "soft skill2"],
  "benefits": ["benefit1", "benefit2", "benefit3"],
  "city": "city name",
  "office_location": "full office address",
  "country": "country name",
  "company_name": "company name",
  "company_description": "a brief description of the company and its mission.",
  "company_size": "small" | "medium" | "large" | null,
  "company_industry": "industry type",
  "employment_type": "full-time" | "part-time",
  "work_schedule": "9 am - 6 pm" | "flexible hours" | "shift-based" | "specific time range",
  "contract_type": "permanent" | "temporary" | "internship" | "freelance",
  "remote_work": true | false,
  "job_categories": ["category1", "category2"]
}
Respond only with the JSON object.
Job Posting Data:
"""
