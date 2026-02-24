#!/usr/bin/env python3
"""
Transform BULLET_CORPUS.md and RESUME_CORPUS.md into SQL seed data.

Generates a complete seed.sql compatible with semops-sites schema including:
- Companies table
- Dimension tables (roles, skills, platforms, industries, domains, business models)
- resume_job fact table
- resume_job_bullet table
- Bridge tables (job→role, job→skill, job→platform, etc.)

Usage:
 python scripts/corpus_to_sql.py > ../semops-sites/supabase/seed.sql
 python scripts/corpus_to_sql.py --jobs-only
 python scripts/corpus_to_sql.py --bullets-only
"""

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Job:
 id: str
 company: str
 title: str
 start: str
 end: str
 seniority: str
 is_manager: bool
 direct_reports: int
 indirect_reports: int
 customer_type: str
 business_model: list[str]
 industry: str
 domains: list[str]
 platforms: list[str]


@dataclass
class Bullet:
 id: str
 job_id: str
 text: str
 metric_types: list[str]
 is_highlight: bool
 status: str


@dataclass
class SkillMapping:
 job_id: str
 skill_id: str
 proficiency: str


@dataclass
class SkillTag:
 skill_id: str
 display_name: str
 category: str
 target_roles: list[str]
 linkedin: bool


# Company UUID mapping (matches semops-sites seed.sql)
COMPANY_UUIDS = {
 "Microsoft": "c1000000-0000-0000-0000-000000000001",
 "Amazon": "c2000000-0000-0000-0000-000000000002",
 "Roku": "c3000000-0000-0000-0000-000000000003",
 "TuneUp Media": "c4000000-0000-0000-0000-000000000004",
 "Warner Brothers": "c5000000-0000-0000-0000-000000000005",
 "IODA": "c6000000-0000-0000-0000-000000000006",
 "CNET": "c7000000-0000-0000-0000-000000000007",
 "TerraLycos": "c8000000-0000-0000-0000-000000000008",
 "Lycos": "c9000000-0000-0000-0000-000000000009",
 "Wired Digital": "ca000000-0000-0000-0000-00000000000a",
}


def parse_array(value: str) -> list[str]:
 """Parse comma-separated values into a list."""
 if not value or value.strip == "":
 return []
 return [v.strip for v in value.split(",") if v.strip]


def parse_bool(value: str) -> bool:
 """Parse Y/N into boolean."""
 return value.strip.upper == "Y"


def parse_int(value: str) -> int:
 """Parse integer, defaulting to 0."""
 try:
 return int(value.strip)
 except (ValueError, AttributeError):
 return 0


def escape_sql(value: str) -> str:
 """Escape single quotes for SQL."""
 return value.replace("'", "''")


def parse_jobs_table(content: str) -> list[Job]:
 """Parse the Master Jobs Table from RESUME_CORPUS.md."""
 jobs = []

 # Find the Master Jobs Table section
 pattern = r"## Master Jobs Table.*?\n\|[^\n]+\|\n\|[-\s|]+\|\n((?:\|[^\n]+\|\n)+)"
 match = re.search(pattern, content, re.DOTALL)

 if not match:
 print("Warning: Could not find Master Jobs Table", file=sys.stderr)
 return jobs

 table_rows = match.group(1).strip.split("\n")

 for row in table_rows:
 if not row.strip or row.strip.startswith("|--"):
 continue

 cols = [c.strip for c in row.split("|")][1:-1]

 if len(cols) < 14:
 print(f"Warning: Skipping row with {len(cols)} columns: {row[:50]}...", file=sys.stderr)
 continue

 job = Job(
 id=cols[0],
 company=cols[1],
 title=cols[2],
 start=cols[3],
 end=cols[4],
 seniority=cols[5],
 is_manager=parse_bool(cols[6]),
 direct_reports=parse_int(cols[7]),
 indirect_reports=parse_int(cols[8]),
 customer_type=cols[9],
 business_model=parse_array(cols[10]),
 industry=cols[11],
 domains=parse_array(cols[12]),
 platforms=parse_array(cols[13]) if len(cols) > 13 else [],
 )
 jobs.append(job)

 return jobs


def parse_bullets_table(content: str) -> list[Bullet]:
 """Parse bullet tables from BULLET_CORPUS.md."""
 bullets = []

 # Find each job section with its bullets table
 sections = re.split(r"\n## ([a-z0-9-]+)\n", content)

 current_job_id = None
 for i, section in enumerate(sections):
 if i % 2 == 1:
 current_job_id = section
 continue

 if current_job_id is None:
 continue

 # Skip non-job sections
 if current_job_id in ["Parsing", "Adding", "Summary", "References"]:
 current_job_id = None
 continue

 # Find the bullets table in this section
 table_pattern = r"\| id \| text \|[^\n]+\n\|[-\s|]+\|\n((?:\|[^\n]+\|\n)+)"
 table_match = re.search(table_pattern, section)

 if not table_match:
 continue

 table_rows = table_match.group(1).strip.split("\n")

 for row in table_rows:
 if not row.strip:
 continue

 cols = [c.strip for c in row.split("|")][1:-1]

 if len(cols) < 5:
 continue

 bullet = Bullet(
 id=cols[0],
 job_id=current_job_id,
 text=cols[1],
 metric_types=parse_array(cols[2]),
 is_highlight="⭐" in cols[3],
 status=cols[4] if cols[4] else "raw",
 )
 bullets.append(bullet)

 current_job_id = None

 return bullets


def parse_skill_mapping(content: str) -> list[SkillMapping]:
 """Parse the skill mapping table from SKILL_MAPPING.md."""
 mappings = []

 # Find the Master Skill Mapping Table
 pattern = r"## Master Skill Mapping Table.*?\n\| job_id \| skill_id \| proficiency \|\n\|[-\s|]+\|\n((?:\|[^\n]+\|\n)+)"
 match = re.search(pattern, content, re.DOTALL)

 if not match:
 print("Warning: Could not find Master Skill Mapping Table", file=sys.stderr)
 return mappings

 table_rows = match.group(1).strip.split("\n")

 for row in table_rows:
 if not row.strip or row.strip.startswith("|--"):
 continue

 cols = [c.strip for c in row.split("|")][1:-1]

 if len(cols) < 3:
 continue

 mapping = SkillMapping(
 job_id=cols[0],
 skill_id=cols[1],
 proficiency=cols[2],
 )
 mappings.append(mapping)

 return mappings


def parse_skills_taxonomy(content: str) -> list[SkillTag]:
 """Parse skill tags from SKILLS_TAXONOMY.md."""
 tags = []

 # Find all tables in category sections (Technical, Domain, Methodology, Tool, Soft Skills)
 # Each has: | skill_id | display_name | category | target_roles | linkedin |
 table_pattern = r"\| skill_id \| display_name \| category \| target_roles \| linkedin \|\n\|[-\s|]+\|\n((?:\|[^\n]+\|\n)+)"
 matches = re.findall(table_pattern, content)

 for table_block in matches:
 for row in table_block.strip.split("\n"):
 if not row.strip or row.strip.startswith("|--"):
 continue

 cols = [c.strip for c in row.split("|")][1:-1]
 if len(cols) < 5:
 continue

 tag = SkillTag(
 skill_id=cols[0],
 display_name=cols[1],
 category=cols[2],
 target_roles=parse_array(cols[3]),
 linkedin=cols[4].strip.upper == "Y",
 )
 tags.append(tag)

 return tags


def generate_skill_tags_sql(tags: list[SkillTag]) -> str:
 """Generate SQL INSERT for resume_skill_tag table."""
 if not tags:
 return "-- No skill tags found"

 lines = [
 "-- =============================================================================",
 "-- SKILL TAGS (LinkedIn / ATS / Composable Resume)",
 "-- =============================================================================",
 "",
 "CREATE TABLE IF NOT EXISTS resume_skill_tag (",
 " id TEXT PRIMARY KEY,",
 " display_name TEXT NOT NULL,",
 " category TEXT NOT NULL CHECK (category IN ('technical', 'domain', 'methodology', 'tool', 'soft-skill')),",
 " target_roles TEXT[] NOT NULL DEFAULT '{}',",
 " linkedin BOOLEAN NOT NULL DEFAULT FALSE",
 ");",
 "",
 "INSERT INTO resume_skill_tag (id, display_name, category, target_roles, linkedin) VALUES",
 ]

 values = []
 for tag in tags:
 roles_array = "ARRAY[" + ", ".join(f"'{r}'" for r in tag.target_roles) + "]::text[]"
 values.append(
 f" ('{tag.skill_id}', '{escape_sql(tag.display_name)}', '{tag.category}', "
 f"{roles_array}, {'TRUE' if tag.linkedin else 'FALSE'})"
 )

 lines.append(",\n".join(values) + ";")
 return "\n".join(lines)


def generate_companies_sql(jobs: list[Job]) -> str:
 """Generate SQL INSERT for companies table."""
 companies = {}
 for job in jobs:
 if job.company not in companies:
 companies[job.company] = COMPANY_UUIDS.get(job.company, f"c0000000-0000-0000-0000-{len(companies):012d}")

 lines = [
 "-- Companies",
 "INSERT INTO companies (id, name, logo_url, website) VALUES",
 ]

 values = []
 for company, uuid in companies.items:
 logo = f"'/logos/{company.lower.replace(' ', '-')}.svg'" if company in ["Microsoft", "Amazon", "Roku", "CNET", "Wired Digital"] else "NULL"
 values.append(f" ('{uuid}', '{escape_sql(company)}', {logo}, NULL)")

 lines.append(",\n".join(values) + ";")
 return "\n".join(lines)


def generate_dimension_tables_sql -> str:
 """Generate SQL INSERTs for all dimension tables."""
 return """-- =============================================================================
-- DIMENSION TABLES
-- =============================================================================

-- Roles
INSERT INTO resume_role (id, name, category, description) VALUES
 ('product-management', 'Product Management', 'product', 'Product strategy, roadmap, and execution'),
 ('product-marketing', 'Product Marketing', 'marketing', 'GTM, positioning, and market research'),
 ('engineering', 'Engineering', 'engineering', 'Software development and architecture'),
 ('data-analytics', 'Data & Analytics', 'data', 'Data infrastructure, BI, and insights'),
 ('leadership', 'Leadership/Management', 'leadership', 'Team and org leadership'),
 ('business-development', 'Business Development', 'sales', 'Partnerships, deals, market expansion');

-- Skills (2-level hierarchy)
INSERT INTO resume_skill (id, name, skill_type, parent_id, aliases) VALUES
 -- Technical skills
 ('ml-ai', 'Machine Learning / AI', 'technical', NULL, ARRAY['ML', 'AI', 'machine learning', 'artificial intelligence']),
 ('data-platform', 'Data Platform', 'technical', NULL, ARRAY['data infrastructure', 'data lake', 'ETL']),
 ('cloud-infrastructure', 'Cloud Infrastructure', 'technical', NULL, ARRAY['AWS', 'Azure', 'GCP']),
 ('search-systems', 'Search Systems', 'technical', NULL, ARRAY['search', 'information retrieval', 'NLP']),
 ('advertising-tech', 'Advertising Technology', 'technical', NULL, ARRAY['adtech', 'ad serving', 'yield']),
 -- Cognitive skills
 ('product-strategy', 'Product Strategy', 'cognitive', NULL, ARRAY['roadmap', 'vision', 'strategy']),
 ('data-analysis', 'Data Analysis', 'cognitive', NULL, ARRAY['analytics', 'insights', 'metrics']),
 ('gtm', 'Go-to-Market', 'cognitive', NULL, ARRAY['launch', 'positioning', 'messaging']),
 -- Social skills
 ('cross-functional-leadership', 'Cross-functional Leadership', 'social', NULL, ARRAY['stakeholder management', 'collaboration']),
 ('communication', 'Communication', 'social', NULL, ARRAY['presentation', 'writing']),
 ('business-dev-skill', 'Business Development', 'social', NULL, ARRAY['partnerships', 'deal-making']),
 -- Resource management
 ('team-leadership', 'Team Leadership', 'resource_mgmt', NULL, ARRAY['management', 'team building']),
 -- Domain skills
 ('streaming-media', 'Streaming Media', 'domain', NULL, ARRAY['OTT', 'video', 'connected TV']),
 ('e-commerce', 'E-commerce', 'domain', NULL, ARRAY['retail', 'marketplace']),
 ('real-time-comms', 'Real-time Communications', 'domain', NULL, ARRAY['WebRTC', 'video calling', 'messaging']),
 ('digital-music-domain', 'Digital Music', 'domain', NULL, ARRAY['music distribution', 'record labels']);

-- Platforms
INSERT INTO resume_platform (id, name, platform_type) VALUES
 ('connected-tv', 'Connected TV', 'connected_tv'),
 ('mobile', 'Mobile', 'mobile'),
 ('web', 'Web', 'web'),
 ('voice', 'Voice / Alexa', 'voice'),
 ('cloud', 'Cloud Platform', 'cloud'),
 ('kindle', 'Kindle / E-reader', 'consumer');

-- Industries (3-level hierarchy)
INSERT INTO resume_industry (id, name, level, parent_id, naics_code) VALUES
 -- Level 1: Sectors
 ('technology', 'Technology', 1, NULL, '51'),
 ('media-entertainment', 'Media & Entertainment', 1, NULL, '51'),
 ('cloud-infrastructure', 'Cloud & Infrastructure', 1, NULL, '518'),
 -- Level 2: Industries
 ('streaming-ott', 'Streaming / OTT', 2, 'media-entertainment', '516210'),
 ('connected-tv-industry', 'Connected TV', 2, 'media-entertainment', '334310'),
 ('digital-books', 'Digital Books', 2, 'media-entertainment', '511130'),
 ('communications-platform', 'Communications Platform', 2, 'cloud-infrastructure', '517311'),
 ('digital-music', 'Digital Music', 2, 'media-entertainment', '512290'),
 ('adtech', 'Advertising Technology', 2, 'technology', '541890'),
 ('search-industry', 'Search & Discovery', 2, 'technology', '519290'),
 ('consumer-software', 'Consumer Software', 2, 'technology', '511210');

-- Product Domains
INSERT INTO resume_product_domain (id, name, description) VALUES
 ('search', 'Search', 'Query-based finding (keyword, semantic, NLP)'),
 ('discovery', 'Discovery', 'Algorithmic content surfacing, recommendations'),
 ('personalization', 'Personalization', 'User-tailored experiences, A/B testing'),
 ('ml-ai-domain', 'ML / AI', 'Machine learning systems, models, inference'),
 ('data-platform-domain', 'Data Platform', 'Pipelines, data lakes, ETL, infrastructure'),
 ('analytics-bi', 'Analytics / BI', 'Reporting, dashboards, product insights'),
 ('voice-conversational', 'Voice / Conversational', 'NLU, voice UX, Alexa, chatbots'),
 ('internationalization', 'Internationalization', 'i18n, localization, multi-market'),
 ('content-ingestion', 'Content Ingestion', 'Metadata, cataloging, enrichment, onboarding'),
 ('browse', 'Browse & Navigation', 'Categorical exploration, taxonomy-driven UX'),
 ('advertising-domain', 'Advertising', 'Ad serving, targeting, yield optimization'),
 ('business-development-domain', 'Business Development', 'Partnerships, deals, market expansion');

-- Business Models
INSERT INTO resume_business_model (id, name, description) VALUES
 ('subscription', 'Subscription', 'Recurring fee (monthly/annual)'),
 ('usage-based', 'Usage-Based', 'Pay per use / API call'),
 ('transactional', 'Transactional', 'One-time purchase'),
 ('advertising', 'Advertising', 'Ad-supported revenue'),
 ('marketplace', 'Marketplace', 'Transaction fees / rev share');"""


def generate_jobs_sql(jobs: list[Job]) -> str:
 """Generate SQL INSERT statements for resume_job table."""
 lines = [
 "-- =============================================================================",
 "-- JOBS (Fact Table)",
 "-- =============================================================================",
 "",
 "INSERT INTO resume_job (id, company_id, title, start_date, end_date, seniority_level, is_manager, direct_reports, indirect_reports, employment_type, customer_type) VALUES",
 ]

 seniority_map = {
 "Mid": "mid",
 "Senior": "senior",
 "Director": "director",
 "Principal": "principal",
 "VP": "vp",
 "C-Level": "c_level",
 }

 values = []
 for job in jobs:
 company_uuid = COMPANY_UUIDS.get(job.company, "NULL")
 end_date = "NULL" if job.end == "present" else f"'{job.end}-01'"
 seniority = seniority_map.get(job.seniority, job.seniority.lower)
 customer = job.customer_type.lower
 employment = "consulting" if "Consultant" in job.title else "full_time"

 value = (
 f" ('{job.id}', '{company_uuid}', '{escape_sql(job.title)}', "
 f"'{job.start}-01', {end_date}, '{seniority}', "
 f"{'TRUE' if job.is_manager else 'FALSE'}, {job.direct_reports}, {job.indirect_reports}, "
 f"'{employment}', '{customer}')"
 )
 values.append(value)

 lines.append(",\n".join(values) + ";")
 return "\n".join(lines)


def generate_bullets_sql(bullets: list[Bullet]) -> str:
 """Generate SQL INSERT statements for resume_job_bullet table."""
 lines = [
 "-- =============================================================================",
 "-- BULLETS (Atomic Content)",
 "-- =============================================================================",
 "",
 "INSERT INTO resume_job_bullet (job_id, text, format, category, is_highlight, composition_tags, display_order) VALUES",
 ]

 # Map metric types to categories
 category_map = {
 "Output": "achievement",
 "0-to-1": "achievement",
 "Capability": "technical",
 "Strategic": "strategic",
 "Scope": "leadership",
 "Adoption": "achievement",
 "Speed": "achievement",
 "Quality": "technical",
 }

 values = []
 job_bullet_count = {}
 for bullet in bullets:
 # Track display order per job
 job_bullet_count[bullet.job_id] = job_bullet_count.get(bullet.job_id, 0) + 1
 display_order = job_bullet_count[bullet.job_id]

 # Determine category from first metric type
 category = "achievement"
 for mt in bullet.metric_types:
 if mt in category_map:
 category = category_map[mt]
 break

 # Build composition tags array
 tags = [f"id:{bullet.id}", f"status:{bullet.status}"]
 tags.extend(bullet.metric_types)
 tags_array = "ARRAY[" + ", ".join(f"'{t}'" for t in tags) + "]::text[]"

 value = (
 f" ('{bullet.job_id}', '{escape_sql(bullet.text)}', 'XYZ', '{category}', "
 f"{'TRUE' if bullet.is_highlight else 'FALSE'}, {tags_array}, {display_order})"
 )
 values.append(value)

 lines.append(",\n".join(values) + ";")
 return "\n".join(lines)


def generate_bridge_tables_sql(jobs: list[Job]) -> str:
 """Generate SQL INSERTs for bridge tables based on job data."""
 lines = [
 "-- =============================================================================",
 "-- BRIDGE TABLES",
 "-- =============================================================================",
 "",
 ]

 # Job → Role (with percentage allocation)
 # This is manually defined based on job characteristics
 role_data = {
 "job-microsoft-azure": [("product-management", 0.60), ("data-analytics", 0.30), ("leadership", 0.10)],
 "job-amazon-books": [("product-management", 0.80), ("data-analytics", 0.20)],
 "job-amazon-firetv-search": [("product-management", 0.70), ("data-analytics", 0.30)],
 "job-roku": [("product-marketing", 0.80), ("leadership", 0.20)],
 "job-tuneup-cmo": [("product-marketing", 0.50), ("product-management", 0.30), ("leadership", 0.20)],
 "job-tuneup-vp": [("product-management", 1.00)],
 "job-wb-consultant": [("product-management", 1.00)],
 "job-ioda-vp-marketing": [("product-management", 0.50), ("product-marketing", 0.50)],
 "job-ioda-vp-bd": [("product-management", 0.50), ("business-development", 0.50)],
 "job-cnet-director": [("product-management", 0.70), ("leadership", 0.30)],
 "job-terralycos-gpm": [("product-management", 1.00)],
 "job-lycos-sr-pm": [("product-management", 1.00)],
 "job-wired-ad-pm": [("product-management", 1.00)],
 "job-wired-ops": [("product-management", 0.70), ("leadership", 0.30)],
 }

 lines.append("-- Job → Role bridges")
 lines.append("INSERT INTO resume_job_role (job_id, role_id, percentage) VALUES")
 values = []
 for job_id, roles in role_data.items:
 for role_id, pct in roles:
 values.append(f" ('{job_id}', '{role_id}', {pct})")
 lines.append(",\n".join(values) + ";")
 lines.append("")

 # Job → Platform (derived from job data)
 platform_map = {
 "Cloud": "cloud",
 "Connected TV": "connected-tv",
 "Voice/Alexa": "voice",
 "Web": "web",
 "Mobile": "mobile",
 "Kindle": "kindle",
 }

 lines.append("-- Job → Platform bridges")
 lines.append("INSERT INTO resume_job_platform (job_id, platform_id) VALUES")
 values = []
 for job in jobs:
 for platform in job.platforms:
 platform_id = platform_map.get(platform)
 if platform_id:
 values.append(f" ('{job.id}', '{platform_id}')")
 lines.append(",\n".join(values) + ";")
 lines.append("")

 # Job → Industry (derived from job data)
 industry_map = {
 "Communications Platform": "communications-platform",
 "Digital Books": "digital-books",
 "Connected TV": "connected-tv-industry",
 "Streaming/OTT": "streaming-ott",
 "Consumer Software": "consumer-software",
 "Digital Music": "digital-music",
 "AdTech": "adtech",
 }

 lines.append("-- Job → Industry bridges")
 lines.append("INSERT INTO resume_job_industry (job_id, industry_id) VALUES")
 values = []
 for job in jobs:
 industry_id = industry_map.get(job.industry)
 if industry_id:
 values.append(f" ('{job.id}', '{industry_id}')")
 lines.append(",\n".join(values) + ";")
 lines.append("")

 # Job → Product Domain (derived from job data)
 domain_map = {
 "Data Platform": "data-platform-domain",
 "Analytics/BI": "analytics-bi",
 "Real-time Comms": "real-time-comms",
 "Personalization": "personalization",
 "Discovery": "discovery",
 "ML/AI": "ml-ai-domain",
 "Search": "search",
 "Voice/Conversational": "voice-conversational",
 "Internationalization": "internationalization",
 "Content Ingestion": "content-ingestion",
 "Advertising": "advertising-domain",
 }

 lines.append("-- Job → Product Domain bridges")
 lines.append("INSERT INTO resume_job_product_domain (job_id, product_domain_id) VALUES")
 values = []
 for job in jobs:
 for domain in job.domains:
 domain_id = domain_map.get(domain)
 if domain_id:
 values.append(f" ('{job.id}', '{domain_id}')")
 lines.append(",\n".join(values) + ";")
 lines.append("")

 # Job → Business Model (derived from job data)
 biz_model_map = {
 "Usage-Based": "usage-based",
 "Transactional": "transactional",
 "Advertising": "advertising",
 "Marketplace": "marketplace",
 "Subscription": "subscription",
 }

 lines.append("-- Job → Business Model bridges")
 lines.append("INSERT INTO resume_job_business_model (job_id, business_model_id) VALUES")
 values = []
 for job in jobs:
 for bm in job.business_model:
 bm_id = biz_model_map.get(bm)
 if bm_id:
 values.append(f" ('{job.id}', '{bm_id}')")
 lines.append(",\n".join(values) + ";")

 return "\n".join(lines)


def generate_job_skills_sql(mappings: list[SkillMapping]) -> str:
 """Generate SQL INSERT statements for resume_job_skill bridge table."""
 if not mappings:
 return "-- No skill mappings found"

 lines = [
 "-- Job → Skill bridges",
 "INSERT INTO resume_job_skill (job_id, skill_id, proficiency) VALUES",
 ]

 values = []
 for mapping in mappings:
 values.append(
 f" ('{mapping.job_id}', '{mapping.skill_id}', '{mapping.proficiency}')"
 )

 lines.append(",\n".join(values) + ";")
 return "\n".join(lines)


def main:
 script_dir = Path(__file__).parent
 repo_root = script_dir.parent
 corpus_dir = repo_root / "docs" / "resumes" / "corpus"

 resume_corpus = corpus_dir / "RESUME_CORPUS.md"
 bullet_corpus = corpus_dir / "BULLET_CORPUS.md"
 skill_mapping = corpus_dir / "SKILL_MAPPING.md"
 skills_taxonomy = corpus_dir / "SKILLS_TAXONOMY.md"

 jobs_only = "--jobs-only" in sys.argv
 bullets_only = "--bullets-only" in sys.argv

 output_lines = [
 "-- =============================================================================",
 "-- RESUME SEED DATA",
 "-- Generated by semops-publisher/scripts/corpus_to_sql.py",
 f"-- Source: {resume_corpus.name}, {bullet_corpus.name}, {skill_mapping.name}, {skills_taxonomy.name}",
 "-- =============================================================================",
 "",
 ]

 jobs = []
 bullets = []
 skill_mappings = []
 skill_tags = []

 if resume_corpus.exists:
 content = resume_corpus.read_text
 jobs = parse_jobs_table(content)
 print(f"Parsed {len(jobs)} jobs from RESUME_CORPUS.md", file=sys.stderr)
 else:
 print(f"Warning: {resume_corpus} not found", file=sys.stderr)

 if bullet_corpus.exists:
 content = bullet_corpus.read_text
 bullets = parse_bullets_table(content)
 print(f"Parsed {len(bullets)} bullets from BULLET_CORPUS.md", file=sys.stderr)
 else:
 print(f"Warning: {bullet_corpus} not found", file=sys.stderr)

 if skill_mapping.exists:
 content = skill_mapping.read_text
 skill_mappings = parse_skill_mapping(content)
 print(f"Parsed {len(skill_mappings)} skill mappings from SKILL_MAPPING.md", file=sys.stderr)
 else:
 print(f"Warning: {skill_mapping} not found", file=sys.stderr)

 if skills_taxonomy.exists:
 content = skills_taxonomy.read_text
 skill_tags = parse_skills_taxonomy(content)
 print(f"Parsed {len(skill_tags)} skill tags from SKILLS_TAXONOMY.md", file=sys.stderr)
 else:
 print(f"Warning: {skills_taxonomy} not found", file=sys.stderr)

 if not bullets_only and jobs:
 output_lines.append(generate_companies_sql(jobs))
 output_lines.append("")
 output_lines.append(generate_dimension_tables_sql)
 output_lines.append("")
 output_lines.append(generate_jobs_sql(jobs))
 output_lines.append("")
 output_lines.append(generate_bridge_tables_sql(jobs))
 output_lines.append("")
 if skill_mappings:
 output_lines.append(generate_job_skills_sql(skill_mappings))
 output_lines.append("")

 if not jobs_only and bullets:
 output_lines.append(generate_bullets_sql(bullets))
 output_lines.append("")

 if not jobs_only and not bullets_only and skill_tags:
 output_lines.append(generate_skill_tags_sql(skill_tags))
 output_lines.append("")

 print("\n".join(output_lines))


if __name__ == "__main__":
 main
