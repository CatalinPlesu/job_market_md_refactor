DB_FILE = "data.json"

# Table name constants
TABLE_ROBOTA_MD_RAW = "robota_md_raw_data"
TABLE_LINKEDIN_RAW = "linkedin_raw_data"
TABLE_PROCESSED = "processed_data"

# Base URL constants
URL_ROBOTA_MD = "https://www.rabota.md/ro/vacancies/category/it/developers/"
URL_LINKEDIN = "https://www.linkedin.com/jobs/search/?keywords=developer&location=Moldova"

CONTEXT = """You are a job data extraction assistant. Extract job information into JSON following the provided schema.

Example extraction:
Input: "Senior Python Developer needed. 3+ years experience. Remote work available."
Output: {"title": "python developer", "experience": 3, "hard_skills": ["python"], "remote_work": "remote", ...}

Always follow the tokenization rules and return only valid JSON."""

JOB_SCHEMA_PROMPT = """
Keep values lowercase, generic and english only so they match other similar posts:
Extract the following minimal job market data from the following job postings into a JSON object. This is for market observation, not job-seeking.
Try to identify as many key words as possible, especially for tech and soft requirements.
All string values should be in lowercase English without special characters (e.g., accents, diacritics) to ensure uniformity.
{
  "title": "job title",
  "min_salary": null or number,
  "max_salary": null or number,
  "salary_currency": null or ISO codes: "mdl" | "eur" | "usd",
  "minimum_education": "none" | "unspecified" | "highschool" | "college" | "bachelor" | "master" | "phd",
  "languages": ["en", "fr", "ro", "ru"], //  ISO 639-1 
  "min_experience_years": null or minimum experience in years,
  "responsibilities": ["responsibility1", "responsibility2"],
  "hard_skills": ["hard skill1", "hard skill2", "hard skill3"],
  "soft_skills": ["soft skill1", "soft skill2", "soft skill3"],
  "certifications": ["cert1", "cert2"],
  "benefits": ["benefit1", "benefit2", "benefit3"],
  "city": "city name", //lowercase english
  "country": "country name", //lowercase english
  "company_name": "company name", //lowercase
  "company_size": "small" | "medium" | "large" | null,
  "employment_type": "full-time" | "part-time",
  "work_schedule": "9 am - 6 pm" | "flexible hours" | "shift-based" | "specific time range",
  "employment_type": "full-time permanent" | "part-time permanent" | "full-time temporary" | "part-time temporary" | "internship" | "freelance",
  "remote_work": true | false,
  "job_categories": ["category1", "category2"]
}
Respond only with the JSON object.
Job Posting Data:
"""

JOB_SCHEMA_PROMPTv2 = """
INSTRUCTIONS:
Extract job market data into JSON format. Keep all values as SHORT TOKENS - use minimal essential keywords that can be compared across similar posts. All text lowercase, English only.

TOKENIZATION RULES:
- Use 1-3 word tokens maximum
- Normalize similar terms: "js"→"javascript", "react.js"→"react", "ci/cd"→"cicd"
- Remove articles, prepositions, connecting words
- Use bare minimum essential keywords only
- Make tokens comparable across similar job posts

FIELD DEFINITIONS:
- title: Normalize job titles (e.g., "software engineer", "data analyst", "1c programmer")
- responsibilities: Short action tokens ["develop", "maintain", "configure", "integrate", "test"]
- hard_skills: Technical tokens ["python", "react", "aws", "mysql", "docker"]
- soft_skills: Behavioral tokens ["teamwork", "communication", "leadership", "problem solving"]
- benefits: Benefit tokens ["remote work", "health insurance", "training", "bonus"]
- certifications: Cert tokens ["aws certified", "pmp", "cissp"]

OTHER FIELDS:
- min_salary/max_salary: Numbers only, null if not specified
- salary_currency: "mdl" | "eur" | "usd" | "gbp" | null
- minimum_education: "none" | "unspecified" | "highschool" | "college" | "bachelor" | "master" | "phd"
- languages: ["en", "ro", "ru", "fr", "es", "de"]
- experience: Years as integer, null if not specified
- company_size: "startup" | "small" | "medium" | "large" | null
- employment_type: "full-time" | "part-time" | "contract"
- work_schedule: "standard" | "flexible" | "shift-based"
- contract_type: "permanent" | "temporary" | "internship" | "freelance"
- remote_work: "remote" | "hybrid" | "on-site"
- job_categories: Short category tokens ["programming", "marketing", "finance"]

JSON SCHEMA:
{
  "title": "string",
  "min_salary": number | null,
  "max_salary": number | null,
  "salary_currency": "mdl" | "eur" | "usd" | "gbp" | null,
  "minimum_education": "none" | "unspecified" | "highschool" | "college" | "bachelor" | "master" | "phd",
  "languages": ["string"],
  "experience": number | null,
  "responsibilities": ["string"],
  "hard_skills": ["string"],
  "soft_skills": ["string"],
  "certifications": ["string"],
  "benefits": ["string"],
  "city": "city name", //lowercase english
  "country": "country name", //lowercase english
  "company_name": "company name", //lowercase
  "company_size": "startup" | "small" | "medium" | "large" | null,
  "employment_type": "full-time" | "part-time" | "contract",
  "work_schedule": "standard" | "flexible" | "shift-based" | "custom",
  "contract_type": "permanent" | "temporary" | "internship" | "freelance",
  "remote_work": "remote" | "hybrid" | "on-site",
  "job_categories": ["string"]
}

Return only valid JSON. No explanations or additional text.

JOB POSTING DATA:
"""