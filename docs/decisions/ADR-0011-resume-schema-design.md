# ADR-0011: Resume Schema Design

> **Status:** In Progress
> **Date:** 2025-12-07 (migrated 2026-01-19)
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/55)
> **Migrated from:** [](https://github.com/semops-ai/semops-sites/issues/34), [](https://github.com/semops-ai/semops-sites/issues/9)
> **Prior Research:** , 

---

## Session Checkpoint (2025-12-09)

**Where we left off:** Issue #10 complete - bullet extraction and format rewriting done.

**Completed:**
- Issue #8 research: Bullet taxonomy (CAR/STAR/PAR formats, category types, O*NET skills)
- Schema design: Job as atomic fact, bridge tables, Job_Bullet as composition atom
- Integration pattern with semops-core Brand table
- **Issue #10:** Extracted ~75 unique bullets from 13 resume docs, rewrote in all 5 formats (CAR/STAR/PAR/XYZ/APR), gap analysis complete
 - Output: `data/resumes/bullet-analysis-staging.md`
 - Canonical XYZ bullet set ready for seed data

**Next steps after review:**
1. Iterate on schema based on feedback
2. Create Supabase migration SQL
3. Write migration script for existing CSV data
4. ~~Parse bullets from job descriptions (LLM-assisted)~~ → Done in #10
5. Verify Gemini LinkedIn metrics (200%, 50%, 15%, 20%, 40%)
6. Research Roku-era metrics (biggest gap - no quantifiable outcomes)

**Open questions for review:**
- ~~Is the bullet `category` taxonomy complete?~~ → Resolved (Issue #8 closed, taxonomy validated in #10)
- ~~Should `customer_mix` be a bridge table instead of JSONB in Job metadata?~~ → Resolved (see Decisions Made)
- ~~How granular should skill hierarchy be?~~ → Resolved (see Decisions Made)
- ~~Should we add a `Project` entity separate from Job?~~ → Resolved (see Decisions Made)
- ~~How should advisory/board roles be handled?~~ → Resolved (see Decisions Made)

**All open questions resolved.** Schema ready for migration.

---

## Decisions Made

### Skill Hierarchy: 2-Level (2025-12-11)

**Decision:** Use 2-level skill hierarchy (`skill_type` → `skill`) with `parent_id` reserved for future L3 expansion.

**Structure:**

```text
skill_type (L1) skill (L2)
─────────────────────────────────────────
technical → ml-ai, data-platform, cloud-infrastructure
cognitive → product-strategy, data-analysis, problem-solving
social → cross-functional-leadership, stakeholder-management
resource_mgmt → team-leadership, budget-management
domain → streaming-media, e-commerce, adtech
```

**Why 2-level:**

- **Platform reuse**: Schema will be used beyond resume (job postings, content tagging, learning paths)
- **LinkedIn alignment**: LinkedIn uses hierarchical skills graph internally (~39K skills with parent→child edges), but job postings reference flat skills. 2-level mirrors this practical usage.
- **Queryable**: Can filter by `skill_type` for broad matches, `skill` for specific requirements
- **Extensible**: `parent_id` field allows L3 sub-skills later (e.g., `ml-ai` → `llm`, `computer-vision`) without schema changes

**Why not flat:**

- Can't roll up "all technical skills" for duration calculations
- No semantic grouping for job matching

**Why not 3+ levels:**

- Over-engineering for current use cases
- Maintenance burden without clear benefit
- Job postings don't typically require sub-skill granularity

**References:**

- [LinkedIn Skills Graph Engineering Blog](https://engineering.linkedin.com/blog/2023/Building-maintaining-the-skills-taxonomy-that-powers-LinkedIns-Skills-Graph)

---

### Customer Type: Simple Enum (2025-12-11)

**Decision:** Use a single `customer_type` column on `resume_job` with enum values `'b2b'` or `'b2c'`.

```sql
-- Add to resume_job
customer_type TEXT CHECK (customer_type IN ('b2b', 'b2c'))
```

**Why simple enum:**

- At the job level, customer type is almost never mixed - your specific role targets B2B or B2C
- Even at companies that serve both (e.g., Amazon), individual jobs have clear customer focus
- No need for percentages, bridge tables, or JSONB complexity

**Removed from schema:**

- `resume_customer_type` dimension table (unnecessary)
- `resume_job_customer` bridge table (unnecessary)
- `customer_mix` JSONB in metadata (replaced by column)

**Why not bridge table:**

- Only 2 values - not worth the join overhead
- No percentage allocation needed at job level
- Simpler queries: `WHERE customer_type = 'b2b'`

---

### No Separate Project Entity (2025-12-11)

**Decision:** Do not add a `Project` entity. Use `resume_job` with granular records per initiative.

**Why Job already covers it:**

- Each Job record represents a distinct role/initiative, not just "time at a company"
- A single company tenure may have multiple Job records (e.g., Fire TV Search, Fire TV International)
- Side projects and consulting work use `employment_type` to distinguish: `'full_time'`, `'contract'`, `'consulting'`, `'project'`

**LinkedIn alignment:**

- LinkedIn Projects must link to a Job or Education entry - they're not standalone
- Our schema achieves the same by making Job the atomic unit at project granularity

**Why not a separate Project entity:**

- Would duplicate Job's structure (dates, company, bullets)
- No clear use case for cross-job project tracking
- `resume_asset` already handles portfolio items (screenshots, demos, case studies)

---

### Advisory/Board Roles: Extended Employment Types (2025-12-11)

**Decision:** Handle advisory and board roles via extended `employment_type` enum values on `resume_job`.

```sql
-- Extend employment_type in resume_job
employment_type TEXT CHECK (employment_type IN (
 'full_time', 'part_time', 'contract', 'consulting', 'project',
 'advisory', 'board_member', 'mentor' -- advisory-class roles
))
```

**Why this works:**

- **Overlapping dates allowed**: Advisory roles (2020-present) coexist with concurrent full_time jobs
- **Same structure, different rendering**: Front-end filters by `employment_type` to display advisory roles separately (no anniversary notifications)
- **Bullets still work**: Advisory contributions captured as `resume_job_bullet` records
- **No duplication**: Uses existing Job entity and relationships

**LinkedIn insight:**

LinkedIn separates Projects from Experience specifically so that long-running advisory/board roles don't trigger "5 year anniversary at Company X!" notifications. Our approach achieves the same UX differentiation via `employment_type` filtering at the display layer.

**Why not a separate Advisory entity:**

- Would duplicate Job's structure (dates, company, bullets)
- Roles, skills, and platforms already work via bridge tables
- Display-layer filtering is simpler than schema-layer separation

---

### Job Narratives: MDX Files (2025-12-11)

**Decision:** Store long-form job narratives as MDX files in `content/career/`, linked via `job_id` frontmatter.

**Structure:**

```
content/
├── blog/ # Blog posts
└── career/ # Job narratives
 ├── amazon-fire-tv-search.mdx # job_id: job-amazon-firetv-search
 ├── streaming-wars-2018.mdx # job_id: job-amazon-firetv-search
 └── microsoft-azure-comms.mdx # job_id: job-microsoft-azure
```

**Frontmatter:**

```yaml
---
job_id: "job-amazon-firetv-search" # or job_ids: ["id1", "id2"]
title: "Fire TV Search & Discovery"
type: "case-study" # case-study | industry-context | technical | lessons
---
```

**Why MDX files (not database):**

- Freeform rich content (diagrams, code blocks, images, embeds)
- Version controlled in git
- Same rendering pipeline as blog
- Chatbot can read raw markdown for context
- No schema changes needed
- Zero, one, or many narratives per job

**Two content types, one job:**

| Content | Purpose | Storage |
|---------|---------|---------|
| **Bullets** | Resume/ATS output | `resume_job_bullet` (DB) |
| **Narratives** | Portfolio, chatbot, data viz | `content/career/*.mdx` (files) |

---

**Bullet Metrics Quality by Job (from #10 analysis):**
| Company | Metrics Quality | Notes |
|---------|----------------|-------|
| Microsoft | Partial | Gemini version has 200%, 50% - needs verification |
| Amazon Books | Partial | Gemini has 15% sales lift - needs verification |
| Amazon Fire TV | Good | 20% relevancy, 40% yield |
| Roku | **None** | Biggest gap - needs research |
| TuneUp | Strong | 30% users, 40% revenue, 30% RPU |
| IODA | Strong | 1000% mobile revenue, 4X annual growth |
| Wired/HotBot | Good | 100% YoY ad revenue |

---

## Industry & Domain Taxonomy Research (2025-12-07)

This section documents research on standardized terminology for classifying industries, customer types, and business models.

### 1. Customer Type (Who you sell to)

Standard taxonomy for business model classification:

| Code | Name | Description | Example |
|------|------|-------------|---------|
| `B2C` | Business-to-Consumer | Direct to end consumers | Netflix, Fire TV |
| `B2B` | Business-to-Business | Selling to other businesses | Azure, AWS |
| `B2B2C` | Business-to-Business-to-Consumer | Platform enabling B2C | Roku (content partners → consumers) |
| `B2G` | Business-to-Government | Government/public sector contracts | Enterprise contracts |
| `D2C` | Direct-to-Consumer | Brand selling directly, no intermediary | Kindle Direct |
| `C2C` | Consumer-to-Consumer | Platform for consumer transactions | eBay, Etsy |

**For resume purposes, primary set:** `B2B`, `B2C`, `B2B2C`, `B2G`

**Sources:** [Wikipedia - Types of E-commerce](https://en.wikipedia.org/wiki/Types_of_e-commerce), [KIBO Commerce](https://kibocommerce.com/blog/commerce-landscape-b2g-b2b-b2b2c-d2c-b2c/)

---

### 2. Cloud Service Model (How software is delivered)

Standard NIST/industry taxonomy:

| Code | Name | Description | You Manage | Provider Manages |
|------|------|-------------|------------|------------------|
| `SaaS` | Software as a Service | Ready-to-use applications | Data, config | Everything else |
| `PaaS` | Platform as a Service | Development platform | App, data | Runtime, middleware, OS, infra |
| `IaaS` | Infrastructure as a Service | Virtualized infrastructure | App, data, runtime, middleware, OS | Virtualization, servers, storage, network |
| `CaaS` | Containers as a Service | Container orchestration | App, containers | Orchestration, infra |

**For Tim's Microsoft role (Azure Communications Services):** This is **PaaS** - developers use the platform to build communication features into their apps.

**Sources:** [IBM - IaaS, PaaS, SaaS](https://www.ibm.com/think/topics/iaas-paas-saas), [AWS - Types of Cloud Computing](https://aws.amazon.com/types-of-cloud-computing/)

---

### 3. Industry Classification Systems

Three major systems exist. Recommend using **LinkedIn Industries** for resume/job matching (most relevant to job search), with NAICS codes as reference for precision.

#### 3a. NAICS (North American Industry Classification System)

6-digit hierarchical system used by US government. 20 top-level sectors.

| Level | Digits | Example |
|-------|--------|---------|
| Sector | 2 | 51 - Information |
| Subsector | 3 | 516 - Publishing Industries |
| Industry Group | 4 | 5161 - Radio & TV Broadcasting |
| Industry | 5 | 51612 - Television Broadcasting |
| National Industry | 6 | 516210 - Media Streaming Distribution |

**Relevant NAICS for Tim's experience:**
- `516210` - Media Streaming Distribution (Fire TV, Roku)
- `518210` - Computing Infrastructure Providers (Azure)
- `519290` - Web Search Portals & All Other Information Services
- `511210` - Software Publishers (SaaS products)
- `334310` - Audio & Video Equipment Manufacturing (Fire TV hardware)

**Source:** [Census.gov NAICS](https://www.census.gov/naics/)

#### 3b. LinkedIn Industries (V2)

434 industries based on NAICS, grouped into categories. Most relevant for job matching.

**Technology, Information and Media** sub-categories:
- Technology, Information and Internet
- Media & Telecommunications
- Entertainment Providers

**Key industries for Tim's experience:**
- `software_development` - Software Development
- `technology_information_internet` - Technology, Information and Internet
- `entertainment_providers` - Entertainment Providers
- `media_telecommunications` - Media & Telecommunications
- `consumer_electronics` - Consumer Electronics (Fire TV)

**Source:** [LinkedIn Industry Codes V2](https://learn.microsoft.com/en-us/linkedin/shared/references/reference-tables/industry-codes-v2)

#### 3c. GICS (Global Industry Classification Standard)

Used in finance/investing. 11 sectors → 24 industry groups → 69 industries → 158 sub-industries.

Less relevant for resume but useful for company classification.

---

### 4. Proposed Industry Hierarchy for Resume Schema

A pragmatic 3-level hierarchy combining the best of the above:

```
Level 1: Sector (broad, ~10-15)
 Level 2: Industry (specific, ~50-100)
 Level 3: Vertical/Niche (optional, detailed)
```

#### Level 1: Sectors

| ID | Sector | Description |
|----|--------|-------------|
| `technology` | Technology | Software, hardware, platforms |
| `media_entertainment` | Media & Entertainment | Content, streaming, publishing |
| `telecommunications` | Telecommunications | Networks, carriers, infrastructure |
| `consumer_electronics` | Consumer Electronics | Devices, hardware products |
| `ecommerce_retail` | E-commerce & Retail | Online/offline retail |
| `cloud_infrastructure` | Cloud & Infrastructure | IaaS, PaaS, data centers |
| `advertising_marketing` | Advertising & Marketing | AdTech, MarTech, agencies |
| `financial_services` | Financial Services | Banking, fintech, payments |
| `enterprise_software` | Enterprise Software | SaaS, business applications |

#### Level 2: Industries (examples for Tim's background)

| ID | Industry | Parent Sector | NAICS Ref |
|----|----------|---------------|-----------|
| `streaming_ott` | Streaming / OTT | media_entertainment | 516210 |
| `connected_tv` | Connected TV / Smart TV | consumer_electronics | 334310 |
| `digital_books` | Digital Books / Publishing | media_entertainment | 511130 |
| `cloud_platform` | Cloud Platform (PaaS) | cloud_infrastructure | 518210 |
| `communications_platform` | Communications Platform | telecommunications | 517311 |
| `digital_music` | Digital Music | media_entertainment | 512290 |
| `search_discovery` | Search & Discovery | technology | 519290 |
| `adtech` | Advertising Technology | advertising_marketing | 541890 |

#### Level 3: Verticals/Niches (optional specificity)

| ID | Vertical | Parent Industry |
|----|----------|-----------------|
| `voice_assistant` | Voice / Alexa | connected_tv |
| `video_on_demand` | VOD / SVOD / AVOD | streaming_ott |
| `ebook_reader` | E-reader / Kindle | digital_books |
| `real_time_comms` | Real-time Communications (WebRTC) | communications_platform |

---

### 5. Recommended Schema Additions

Add these dimension tables to the schema:

```sql
-- Customer Type dimension
CREATE TABLE resume_customer_type (
 id TEXT PRIMARY KEY, -- 'b2b', 'b2c', 'b2b2c', 'b2g'
 name TEXT NOT NULL,
 description TEXT
);

-- Cloud Service Model dimension
CREATE TABLE resume_service_model (
 id TEXT PRIMARY KEY, -- 'saas', 'paas', 'iaas', 'on_premise'
 name TEXT NOT NULL,
 description TEXT
);

-- Industry dimension (hierarchical)
CREATE TABLE resume_industry (
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 level INTEGER NOT NULL CHECK (level IN (1, 2, 3)), -- sector, industry, vertical
 parent_id TEXT REFERENCES resume_industry(id),
 naics_code TEXT, -- optional reference
 linkedin_code TEXT, -- optional reference
 description TEXT
);

-- Bridge: Job → Customer Type (with percentage)
CREATE TABLE resume_job_customer (
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,
 customer_type_id TEXT REFERENCES resume_customer_type(id),
 percentage NUMERIC(3,2) CHECK (percentage > 0 AND percentage <= 1),
 PRIMARY KEY (job_id, customer_type_id)
);

-- Bridge: Job → Industry (company's industry)
-- Note: This is at Job level because company industry can change or job focus differs
CREATE TABLE resume_job_industry (
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,
 industry_id TEXT REFERENCES resume_industry(id),
 PRIMARY KEY (job_id, industry_id)
);
```

---

### 6. Example Classifications for Tim's Jobs

| Job | Customer Type | Service Model | Sector | Industry |
|-----|---------------|---------------|--------|----------|
| Microsoft Azure Comms | B2B (100%) | PaaS | cloud_infrastructure | communications_platform |
| Amazon Books | B2C (100%) | SaaS | media_entertainment | digital_books |
| Amazon Fire TV | B2C (100%) | - | consumer_electronics | connected_tv |
| Roku | B2C (100%) | - | consumer_electronics | connected_tv |
| IODA | B2B (100%) | SaaS | media_entertainment | digital_music |
| Wired/HotBot | B2C (80%) B2B (20%) | - | advertising_marketing | adtech |

---

**Sources:**
- [NAICS - Census.gov](https://www.census.gov/naics/)
- [LinkedIn Industry Codes V2](https://learn.microsoft.com/en-us/linkedin/shared/references/reference-tables/industry-codes-v2)
- [IBM Cloud Service Models](https://www.ibm.com/think/topics/iaas-paas-saas)
- [Wikipedia - Industry Classification](https://en.wikipedia.org/wiki/Industry_classification)

---

### 7. Product Domain (Cross-cutting capability areas)

Product domains are **problem spaces / capability areas** that span industries. Unlike industry (where the company operates), product domain describes **what you built/owned**.

#### Product Domain Taxonomy

| ID | Domain | Description | Example Products |
|----|--------|-------------|------------------|
| `search` | Search | Query-based finding (keyword, semantic, NLP) | HotBot, Fire TV search |
| `discovery` | Discovery | Algorithmic content surfacing, recommendations | Fire TV home, Books recs |
| `personalization` | Personalization | User-tailored experiences, A/B testing | Kindle reading experience |
| `browse` | Browse & Navigation | Categorical exploration, taxonomy-driven UX | Fire TV browse, MP3.com |
| `ml_ai` | ML / AI | Machine learning systems, models, inference, MLOps | Recommendation engines |
| `data_platform` | Data Platform | Pipelines, data lakes, ETL, infrastructure | Azure data, Fire TV analytics |
| `analytics_bi` | Analytics / BI | Reporting, dashboards, product insights | IODA dashboard, Azure metrics |
| `content_ingestion` | Content Ingestion | Metadata, cataloging, enrichment, onboarding | Music/video catalog systems |
| `voice_conversational` | Voice / Conversational | NLU, voice UX, Alexa, chatbots | Fire TV Alexa integration |
| `advertising` | Advertising | Ad serving, targeting, yield optimization | HotBot ads, Fire TV ads |
| `real_time_comms` | Real-time Comms | WebRTC, video/audio, messaging, presence | Azure Communications Services |
| `payments_commerce` | Payments / Commerce | Checkout, transactions, billing | - |
| `internationalization` | Internationalization | i18n, localization, multi-market launch | Fire TV 40+ countries |

#### Key Distinction: ML/AI vs. ML-Powered Features

| Tag | Meaning | Example |
|-----|---------|---------|
| `ml_ai` | Worked *on* ML systems (models, training, MLOps, data science) | Built recommendation model |
| `personalization` + `discovery` | Worked *with* ML (PM driving ML-powered features) | Owned personalization roadmap using ML |

Most PM roles are the latter - driving ML-powered product features, not building the models themselves.

---

### 8. Business Model (Revenue model)

| ID | Business Model | Description | Example |
|----|----------------|-------------|---------|
| `subscription` | Subscription | Recurring fee (monthly/annual) | Netflix, Spotify |
| `usage_based` | Usage-Based | Pay per use / API call / consumption | Azure, AWS |
| `transactional` | Transactional | One-time purchase per item | Fire TV device, Kindle books |
| `freemium` | Freemium | Free tier + paid upgrades | Spotify free → Premium |
| `advertising` | Advertising | Ad-supported revenue | HotBot, Fire TV AVOD |
| `marketplace` | Marketplace | Transaction fees / rev share | Roku channel store |
| `licensing` | Licensing | Per-seat or enterprise license | Enterprise SaaS |
| `hybrid` | Hybrid | Multiple revenue streams | Amazon (transactional + subscription + ads) |

---

### 9. Schema Additions for Product Domain & Business Model

```sql
-- Product Domain dimension
CREATE TABLE resume_product_domain (
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 description TEXT,
 created_at TIMESTAMPTZ DEFAULT NOW
);

-- Seed data
INSERT INTO resume_product_domain (id, name, description) VALUES
 ('search', 'Search', 'Query-based finding (keyword, semantic, NLP)'),
 ('discovery', 'Discovery', 'Algorithmic content surfacing, recommendations'),
 ('personalization', 'Personalization', 'User-tailored experiences, A/B testing'),
 ('browse', 'Browse & Navigation', 'Categorical exploration, taxonomy-driven UX'),
 ('ml_ai', 'ML / AI', 'Machine learning systems, models, inference, MLOps'),
 ('data_platform', 'Data Platform', 'Pipelines, data lakes, ETL, infrastructure'),
 ('analytics_bi', 'Analytics / BI', 'Reporting, dashboards, product insights'),
 ('content_ingestion', 'Content Ingestion', 'Metadata, cataloging, enrichment'),
 ('voice_conversational', 'Voice / Conversational', 'NLU, voice UX, Alexa, chatbots'),
 ('advertising', 'Advertising', 'Ad serving, targeting, yield optimization'),
 ('real_time_comms', 'Real-time Comms', 'WebRTC, video/audio, messaging'),
 ('payments_commerce', 'Payments / Commerce', 'Checkout, transactions, billing'),
 ('internationalization', 'Internationalization', 'i18n, localization, multi-market');

-- Business Model dimension
CREATE TABLE resume_business_model (
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 description TEXT,
 created_at TIMESTAMPTZ DEFAULT NOW
);

-- Seed data
INSERT INTO resume_business_model (id, name, description) VALUES
 ('subscription', 'Subscription', 'Recurring fee (monthly/annual)'),
 ('usage_based', 'Usage-Based', 'Pay per use / API call'),
 ('transactional', 'Transactional', 'One-time purchase'),
 ('freemium', 'Freemium', 'Free tier + paid upgrades'),
 ('advertising', 'Advertising', 'Ad-supported revenue'),
 ('marketplace', 'Marketplace', 'Transaction fees / rev share'),
 ('licensing', 'Licensing', 'Per-seat or enterprise license');

-- Bridge: Job → Product Domain (many-to-many)
CREATE TABLE resume_job_product_domain (
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,
 product_domain_id TEXT REFERENCES resume_product_domain(id),
 PRIMARY KEY (job_id, product_domain_id)
);

-- Bridge: Job → Business Model (many-to-many)
CREATE TABLE resume_job_business_model (
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,
 business_model_id TEXT REFERENCES resume_business_model(id),
 PRIMARY KEY (job_id, business_model_id)
);
```

---

### 10. Complete Job Classification Matrix

| Job | Customer | Service | Business Model | Industry | Product Domains |
|-----|----------|---------|----------------|----------|-----------------|
| **Microsoft Azure Comms** | B2B | PaaS | usage_based | communications_platform | real_time_comms, data_platform, analytics_bi |
| **Amazon Books** | B2C | SaaS | transactional | digital_books | discovery, personalization, browse, ml_ai |
| **Amazon Fire TV** | B2C | - | transactional, advertising | connected_tv | search, discovery, personalization, voice_conversational, data_platform, ml_ai, internationalization |
| **Roku** | B2C, B2B2C | - | marketplace, advertising | connected_tv | search, discovery, personalization |
| **IODA** | B2B | SaaS | subscription | digital_music | analytics_bi, data_platform, content_ingestion |
| **Wired/HotBot** | B2C (80%), B2B (20%) | - | advertising | adtech | search, advertising |
| **Lycos Music** | B2C | - | advertising | digital_music | content_ingestion, browse |
| **CNET/MP3.com** | B2C | - | advertising | digital_music | search, discovery, browse, content_ingestion |

---

### 11. Dimension Summary

| Dimension | Type | Cardinality | % Allocation? | Purpose |
|-----------|------|-------------|---------------|---------|
| **Customer Type** | Enum | ~4 | Yes | Who you sell to (B2B/B2C) |
| **Service Model** | Enum | ~4 | No | How product is delivered (SaaS/PaaS) |
| **Business Model** | Enum | ~7 | No | How you make money |
| **Industry** | Hierarchy | ~50-100 | No | Market/sector where company operates |
| **Product Domain** | Flat | ~15-20 | No | Cross-cutting capability you owned |
| **Role** | Flat | ~10-15 | Yes | Function/discipline (PM, Eng, Marketing) |
| **Skill** | Hierarchy | ~100+ | No | Technical/domain competencies |
| **Platform** | Flat | ~10 | No | Tech platform (web, mobile, voice) |

---

## Executive Summary

Design a dimensional resume schema where **Job is the atomic fact entity**, with bridge tables for multi-valued dimensions (Roles, Skills, Platforms, Customers). Experience bullets are stored as **atomic content units** with structured metadata enabling composition into tailored resumes, cover letters, and outreach messages.

---

## Context

### Problem Statement

Traditional resume data is flat and inflexible:
- Can't answer "How much B2B product experience do you have?"
- Can't allocate duration across multiple roles within a single job
- Can't compose tailored outputs from atomic experience units
- No structured way to match experience against job requirements

### Design Goals

1. **Dimensional analysis**: Calculate duration by Role, Customer, Platform, Skill
2. **Atomic composition**: Break experience into recomposable bullets
3. **Pattern matching**: Match experience atoms against job requirements
4. **Schema.org alignment**: Use industry standards with documented deviations
5. **Integration**: Work with existing semops-core Brand/Entity patterns

### Prior Art

- **Schema.org**: `Person`, `Organization`, `JobPosting`, `EmployeeRole`
- **JSON Resume**: Open standard with `work[].highlights[]` structure
- **O*NET**: BLS taxonomy for skills, knowledge, abilities, work activities
- **Issue #8 Research**: CAR/STAR/PAR bullet formats, category taxonomy

---

## Decision

### Core Design Principles

1. **Job as Atomic Fact**: Not Company, not Title - Job is the grain
2. **Bridge Tables for Many-to-Many**: Roles, Skills, Platforms, Customers
3. **Percentage Allocation**: Duration can be split across dimensions
4. **Bullets as Atoms**: Each bullet is a composable content unit
5. **Tags vs Hard Schema**: Use JSONB for classifier-decorated fields

### Schema Overview

```
┌─────────────┐ ┌──────────────────┐ ┌─────────────┐
│ Company │────<│ Job │>────│ Job_Bullet │
│ (dim) │ │ (fact/grain) │ │ (atom) │
└─────────────┘ └──────────────────┘ └─────────────┘
 │
 ┌──────────────────┼──────────────────┐
 ▼ ▼ ▼
 ┌───────────┐ ┌────────────┐ ┌─────────────┐
 │ Job_Role │ │ Job_Skill │ │Job_Platform │
 │ (bridge) │ │ (bridge) │ │ (bridge) │
 └───────────┘ └────────────┘ └─────────────┘
 │ │ │
 ▼ ▼ ▼
 ┌───────────┐ ┌────────────┐ ┌─────────────┐
 │ Role │ │ Skill │ │ Platform │
 │ (dim) │ │ (dim) │ │ (dim) │
 └───────────┘ └────────────┘ └─────────────┘
```

---

## Schema Definitions

### 1. Company (Dimension)

Maps to existing `Brand` entity in semops-core with `brand_type: 'organization'`.

```sql
-- Uses existing Brand table from semops-core
-- brand_type = 'organization'
-- Additional resume-specific fields in metadata JSONB:
-- industry, size_range, customer_type (B2B/B2C/B2B2C)
```

**Schema.org Alignment**: `schema:Organization`
- `name` ← `schema:name`
- `url` ← `schema:url`
- `metadata.industry` ← `schema:industry`

### 2. Job (Fact Table / Grain)

The atomic unit of work experience. One row per distinct role/responsibility period.

```sql
CREATE TABLE resume_job (
 id TEXT PRIMARY KEY, -- e.g., 'job-amazon-firetv-search'

 -- Foreign Keys
 company_id TEXT REFERENCES brand(id), -- Links to Brand (organization)

 -- Core Attributes
 title TEXT NOT NULL, -- Job title held
 start_date DATE NOT NULL,
 end_date DATE, -- NULL = current
 duration_months NUMERIC GENERATED ALWAYS AS (
 EXTRACT(EPOCH FROM (COALESCE(end_date, CURRENT_DATE) - start_date)) / 2628000
 ) STORED,

 -- Scope & Level
 seniority_level TEXT, -- 'principal', 'director', 'vp', 'c-level'
 level_equivalent TEXT, -- 'L7', 'L66', 'E7' (for calibration)

 -- Management
 is_manager BOOLEAN DEFAULT FALSE,
 direct_reports INTEGER DEFAULT 0,
 indirect_reports INTEGER DEFAULT 0,

 -- Description (for display, not composition)
 summary TEXT, -- 1-2 sentence overview

 -- Employment Classification
 employment_type TEXT CHECK (employment_type IN (
 'full_time', 'part_time', 'contract', 'consulting', 'project',
 'advisory', 'board_member', 'mentor'
 )),
 customer_type TEXT CHECK (customer_type IN ('b2b', 'b2c')),

 -- Metadata (classifier-decorated)
 metadata JSONB DEFAULT '{}',
 -- Expected fields:
 -- scope: { budget: 2000000, team_size: 20, user_scale: '40M' }

 -- Audit
 created_at TIMESTAMPTZ DEFAULT NOW,
 updated_at TIMESTAMPTZ DEFAULT NOW
);
```

**Schema.org Alignment**: `schema:EmployeeRole` + `schema:Occupation`
- `title` ← `schema:roleName`
- `start_date` ← `schema:startDate`
- `end_date` ← `schema:endDate`
- `company_id` → `schema:worksFor`

**Deviation from Schema.org**: We use Job as grain (not Person→worksFor→Organization) because:
- Allows multiple roles at same company
- Enables duration allocation across dimensions
- Supports scope changes without title change

### 3. Job_Bullet (Atomic Content Unit)

Each bullet is a composable experience atom following issue #8 taxonomy.

```sql
CREATE TABLE resume_job_bullet (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid,
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,

 -- Content
 text TEXT NOT NULL, -- Full bullet text

 -- Structure (issue #8 formats)
 format TEXT CHECK (format IN ('CAR', 'STAR', 'PAR', 'XYZ', 'APR', 'simple')),

 -- Parsed Components (for composition)
 components JSONB DEFAULT '{}',
 -- CAR: { challenge, action, result }
 -- STAR: { situation, task, action, result }
 -- XYZ: { accomplishment, method, metric }

 -- Category (issue #8 taxonomy)
 category TEXT CHECK (category IN (
 'achievement', -- Quantified outcome/win
 'responsibility', -- Scope/ownership
 'skill', -- Competency demonstration
 'leadership', -- Team/org influence
 'technical', -- Systems/tools/methods
 'strategic', -- Vision/planning
 'cross_functional' -- Collaboration
 )),

 -- Extracted Metrics
 metrics JSONB DEFAULT '[]',
 -- Array of: { type: 'percentage'|'currency'|'count'|'duration',
 -- value: 60, context: 'reduction in reporting time' }

 -- Display Order
 display_order INTEGER DEFAULT 0,

 -- Composition Hints
 is_highlight BOOLEAN DEFAULT FALSE, -- Top achievement for this job
 composition_tags TEXT[] DEFAULT '{}', -- ['data-platform', 'zero-to-one']

 -- Embedding for semantic matching
 embedding VECTOR(1536),

 -- Audit
 created_at TIMESTAMPTZ DEFAULT NOW,
 updated_at TIMESTAMPTZ DEFAULT NOW
);

-- Index for semantic search
CREATE INDEX idx_bullet_embedding ON resume_job_bullet
USING hnsw (embedding vector_cosine_ops);
```

**Issue #8 Alignment**:
- `format`: CAR/STAR/PAR/XYZ from accomplishment statement research
- `category`: Achievement/responsibility/leadership/technical taxonomy
- `components`: Parsed structure for recomposition
- `metrics`: Extracted quantifiable results

### 4. Role (Dimension)

Generic discipline/function for duration allocation.

```sql
CREATE TABLE resume_role (
 id TEXT PRIMARY KEY, -- e.g., 'product-management'
 name TEXT NOT NULL,
 category TEXT, -- 'product', 'engineering', 'marketing', 'operations'
 description TEXT,
 created_at TIMESTAMPTZ DEFAULT NOW
);

-- Seed data
INSERT INTO resume_role (id, name, category) VALUES
 ('product-management', 'Product Management', 'product'),
 ('product-marketing', 'Product Marketing', 'marketing'),
 ('business-development', 'Business Development', 'sales'),
 ('engineering', 'Engineering', 'engineering'),
 ('data-analytics', 'Data & Analytics', 'data'),
 ('leadership', 'Leadership/Management', 'leadership');
```

### 5. Job_Role (Bridge Table)

Allocates job duration across roles with percentages.

```sql
CREATE TABLE resume_job_role (
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,
 role_id TEXT REFERENCES resume_role(id),

 -- Duration Allocation
 percentage NUMERIC(3,2) NOT NULL CHECK (percentage > 0 AND percentage <= 1),
 -- Calculated: allocated_months = job.duration_months * percentage

 PRIMARY KEY (job_id, role_id)
);

-- Constraint: percentages must sum to 1.0 per job
-- (Enforced via trigger or application logic)
```

### 6. Skill (Dimension)

O*NET-aligned skill taxonomy.

```sql
CREATE TABLE resume_skill (
 id TEXT PRIMARY KEY, -- e.g., 'ml-ai'
 name TEXT NOT NULL,

 -- O*NET Alignment
 skill_type TEXT CHECK (skill_type IN (
 'cognitive', -- Analysis, problem-solving
 'technical', -- Tools, platforms, languages
 'social', -- Communication, leadership
 'resource_mgmt', -- People, budget, time
 'domain' -- Industry-specific knowledge
 )),

 -- Hierarchy
 parent_id TEXT REFERENCES resume_skill(id),

 -- Aliases for matching
 aliases TEXT[] DEFAULT '{}', -- ['machine learning', 'artificial intelligence']

 created_at TIMESTAMPTZ DEFAULT NOW
);

-- Seed examples
INSERT INTO resume_skill (id, name, skill_type, aliases) VALUES
 ('ml-ai', 'Machine Learning / AI', 'technical', ARRAY['ML', 'AI', 'machine learning']),
 ('data-platform', 'Data Platform', 'technical', ARRAY['data infrastructure', 'data lake']),
 ('product-strategy', 'Product Strategy', 'cognitive', ARRAY['roadmap', 'vision']),
 ('cross-functional', 'Cross-functional Leadership', 'social', ARRAY['stakeholder management']);
```

### 7. Job_Skill (Bridge Table)

Links jobs to skills with optional proficiency.

```sql
CREATE TABLE resume_job_skill (
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,
 skill_id TEXT REFERENCES resume_skill(id),

 -- Optional proficiency (for weighted matching)
 proficiency TEXT CHECK (proficiency IN ('novice', 'intermediate', 'advanced', 'expert')),

 PRIMARY KEY (job_id, skill_id)
);
```

### 8. Platform (Dimension)

Product/technology platforms worked on.

```sql
CREATE TABLE resume_platform (
 id TEXT PRIMARY KEY,
 name TEXT NOT NULL,
 platform_type TEXT CHECK (platform_type IN (
 'web', 'mobile', 'connected_tv', 'iot', 'voice',
 'cloud', 'enterprise', 'consumer', 'saas'
 )),
 created_at TIMESTAMPTZ DEFAULT NOW
);
```

### 9. Job_Platform (Bridge Table)

```sql
CREATE TABLE resume_job_platform (
 job_id TEXT REFERENCES resume_job(id) ON DELETE CASCADE,
 platform_id TEXT REFERENCES resume_platform(id),
 PRIMARY KEY (job_id, platform_id)
);
```

### 10. Asset (Portfolio Items)

Links to portfolio assets, screenshots, demos.

```sql
CREATE TABLE resume_asset (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid,
 job_id TEXT REFERENCES resume_job(id), -- Optional: can be standalone

 -- Asset Info
 title TEXT NOT NULL,
 description TEXT,
 asset_type TEXT CHECK (asset_type IN (
 'screenshot', 'demo', 'case_study', 'presentation',
 'video', 'article', 'repo', 'archive'
 )),

 -- Location
 url TEXT,
 archive_url TEXT, -- web.archive.org snapshot
 file_path TEXT, -- local file reference

 -- Metadata
 metadata JSONB DEFAULT '{}',

 created_at TIMESTAMPTZ DEFAULT NOW
);
```

---

## Calculated Views

### Duration by Role

```sql
CREATE VIEW v_duration_by_role AS
SELECT
 r.id AS role_id,
 r.name AS role_name,
 SUM(j.duration_months * jr.percentage) AS total_months
FROM resume_job j
JOIN resume_job_role jr ON j.id = jr.job_id
JOIN resume_role r ON jr.role_id = r.id
GROUP BY r.id, r.name;
```

### Duration by Customer Type

```sql
CREATE VIEW v_duration_by_customer AS
SELECT
 customer_type,
 SUM(duration_months * customer_pct) AS total_months
FROM (
 SELECT
 j.id,
 j.duration_months,
 key AS customer_type,
 value::numeric AS customer_pct
 FROM resume_job j,
 jsonb_each_text(j.metadata->'customer_mix')
) sub
GROUP BY customer_type;
```

### Company Tenure

```sql
CREATE VIEW v_company_tenure AS
SELECT
 c.id AS company_id,
 c.name AS company_name,
 MIN(j.start_date) AS first_start,
 MAX(COALESCE(j.end_date, CURRENT_DATE)) AS last_end,
 EXTRACT(EPOCH FROM (
 MAX(COALESCE(j.end_date, CURRENT_DATE)) - MIN(j.start_date)
 )) / 2628000 AS tenure_months,
 COUNT(j.id) AS job_count
FROM brand c
JOIN resume_job j ON j.company_id = c.id
WHERE c.brand_type = 'organization'
GROUP BY c.id, c.name;
```

---

## Integration with semops-core

### Brand Table Extension

Companies map to `Brand` with `brand_type = 'organization'`:

```sql
-- No schema changes needed to Brand table
-- Resume-specific company data stored in metadata JSONB:
UPDATE brand SET metadata = metadata || '{
 "resume": {
 "industry": "Streaming Entertainment",
 "size_range": "1000-5000",
 "customer_type": "B2C"
 }
}'::jsonb
WHERE id = 'amazon-devices';
```

### Entity Integration (Optional)

Job bullets can optionally be stored as Entity records for the content graph:

```sql
-- Optional: Create Entity records for bullets
INSERT INTO entity (id, asset_type, title, primary_concept_id, metadata)
SELECT
 'bullet-' || b.id,
 'file',
 LEFT(b.text, 100),
 NULL, -- Orphan until connected to concept
 jsonb_build_object(
 'content_type', 'experience_bullet',
 'job_id', b.job_id,
 'category', b.category
 )
FROM resume_job_bullet b;
```

---

## Composition Pattern

### Experience Hubs (L2)

Themed groupings for composition, stored as views or materialized:

```sql
CREATE TABLE resume_hub (
 id TEXT PRIMARY KEY,
 label TEXT NOT NULL,
 narrative TEXT, -- 1-2 sentence positioning
 filter_criteria JSONB, -- How to select bullets
 -- e.g., { "skills": ["ml-ai"], "categories": ["achievement", "technical"] }
 created_at TIMESTAMPTZ DEFAULT NOW
);

-- Example hubs
INSERT INTO resume_hub (id, label, narrative, filter_criteria) VALUES
 ('ai-ml-product', 'AI/ML Product Leadership',
 'Built ML-driven products at scale + shipping AI tools independently',
 '{"skills": ["ml-ai", "data-platform"], "categories": ["achievement", "leadership"]}'),

 ('data-platform', 'Data Platform & Analytics',
 'Zero-to-one data infrastructure at enterprise scale',
 '{"skills": ["data-platform", "data-analytics"], "categories": ["technical", "achievement"]}'),

 ('builder-executive', 'Executive Who Builds',
 'Unique differentiation - I don''t just manage builders, I build',
 '{"composition_tags": ["hands-on", "zero-to-one", "shipped"]}');
```

### Composition Query

Select bullets for a specific job requirement:

```sql
-- Find bullets matching job requirements
WITH job_requirements AS (
 SELECT
 ARRAY['ml-ai', 'data-platform'] AS required_skills,
 ARRAY['achievement', 'leadership'] AS preferred_categories,
 'principal' AS target_level
)
SELECT
 b.id,
 b.text,
 b.category,
 b.metrics,
 j.title,
 c.name AS company,
 1 - (b.embedding <=> :query_embedding) AS semantic_similarity
FROM resume_job_bullet b
JOIN resume_job j ON b.job_id = j.id
JOIN brand c ON j.company_id = c.id
JOIN resume_job_skill js ON j.id = js.job_id
WHERE js.skill_id = ANY((SELECT required_skills FROM job_requirements))
 AND b.category = ANY((SELECT preferred_categories FROM job_requirements))
ORDER BY semantic_similarity DESC
LIMIT 10;
```

---

## Migration Path

### From Existing CSV Data

```python
# Pseudocode for migrating existing CSVs
def migrate_resume_data:
 # 1. Companies → Brand (brand_type='organization')
 for row in read_csv('resume-company.csv'):
 upsert_brand(
 id=slugify(row['CompanyName']),
 brand_type='organization',
 name=row['CompanyName'],
 metadata={'resume': {'industry': row['CompanyIndustry']}}
 )

 # 2. Jobs → resume_job
 for row in read_csv('resume-jobs.csv'):
 insert_job(
 id=f"job-{row['JobID']}",
 company_id=slugify(row['Company']),
 title=row['Title'],
 start_date=parse_date(row['JobStart']),
 end_date=parse_date(row['JobEnd']),
 is_manager=row['Mgr'] == 'Y',
 direct_reports=int(row['MgrDir'] or 0),
 indirect_reports=int(row['MgrIndir'] or 0),
 summary=row['Desc']
 )

 # 3. Job_Roles → resume_job_role
 for row in read_csv('job-roles.csv'):
 insert_job_role(
 job_id=f"job-{row['JobID(fk)']}",
 role_id=slugify(row['Role']),
 percentage=float(row['Role%'])
 )

 # 4. Parse bullets from job descriptions
 for job in get_all_jobs:
 bullets = parse_bullets(job.summary) # Split by newline, classify
 for i, bullet in enumerate(bullets):
 insert_bullet(
 job_id=job.id,
 text=bullet.text,
 format=detect_format(bullet),
 category=classify_category(bullet),
 display_order=i
 )
```

---

## Consequences

### Positive

- **Dimensional flexibility**: Can answer "How much B2B PM experience?" precisely
- **Composition-ready**: Bullets as atoms enable tailored output generation
- **ATS-aligned**: Category taxonomy matches what recruiters look for
- **Semantic matching**: Embeddings enable job-to-experience matching
- **Schema.org compatible**: Can export to standard formats

### Negative

- **Data entry overhead**: Must allocate percentages for roles/customers
- **Complexity**: More tables than simple flat resume
- **Maintenance**: Bridge tables need consistency enforcement

### Risks

- **Over-engineering**: Might be overkill for simple resume display
- **Percentage accuracy**: Estimates may not be precise

### Mitigations

- Start with required dimensions (Role, Skill), add others incrementally
- Use sensible defaults (100% for single-role jobs)
- Provide views for simple display use cases

---

## Implementation Plan

1. **Create Supabase migration** - Tables, indexes, seed data
2. **Migrate existing CSVs** - Python script to populate
3. **Parse bullets from descriptions** - LLM-assisted extraction
4. **Generate embeddings** - OpenAI text-embedding-3-small
5. **Build composition API** - Query bullets by job requirements
6. **Create views for resumator** - Duration by Role, Company tenure

---

## References

- [Schema.org JobPosting](https://schema.org/JobPosting)
- [JSON Resume Schema](https://jsonresume.org/schema)
- [O*NET Content Model](https://www.onetcenter.org/content.html)
- 
- [semops-core UBIQUITOUS_LANGUAGE.md](https://github.com/semops-ai/semops-core/blob/main/schemas/UBIQUITOUS_LANGUAGE.md)

---

**Document Status:** Draft | **Next Review:** After implementation
**Maintainer:** Tim Mitchell
