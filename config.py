DB_FILE = "data.json"

# Table name constants
TABLE_ROBOTA_MD_RAW = "robota_md_raw_data"
TABLE_LINKEDIN_RAW = "linkedin_raw_data"
TABLE_PROCESSED = "processed_data"

# Base URL constants
URL_ROBOTA_MD = "https://www.rabota.md/ro/vacancies/category/it/developers/"
# URL_LINKEDIN = "https://www.linkedin.com/jobs/search/?keywords=developer&location=Moldova"
# this one should remove most EMEA jobs
URL_LINKEDIN = "https://www.linkedin.com/jobs/search/?currentJobId=4016661303&f_PP=103403991&geoId=106178099&keywords=Developer&origin=JOB_SEARCH_PAGE_LOCATION_HISTORY&refresh=true&sortBy=R&start=25&trk=public_jobs_jobs-search-bar_search-submit"

CONTEXT = """You are a job data extraction assistant. Extract job information into JSON following the provided schema.

Example extraction:
Input: "Senior Python Developer needed. 3+ years experience. Remote work available."
Output: {"title": "python developer", "experience": 3, "hard_skills": ["python"], "remote_work": "remote", ...}

Always follow the tokenization rules and return only valid JSON."""

JOB_SCHEMA_PROMPTv2 = """
INSTRUCTIONS:
Extract job market data into JSON format. Keep all values as SHORT TOKENS - use minimal essential keywords that can be compared across similar posts. All text lowercase, English only.

TOKENIZATION RULES:
- Use 1-3 word tokens maximum
- Normalize similar terms: "js"→"javascript", ".net" → "dotnet", "react.js"→"react", "ci/cd"→"cicd"
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