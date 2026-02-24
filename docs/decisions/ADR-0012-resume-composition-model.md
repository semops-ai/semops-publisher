# ADR-0012: Resume Composition Object Model

> **Status:** In Progress
> **Date:** 2026-01-20 (Updated: 2026-01-21)
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/59)
> **Cross-Repo:** [](https://github.com/semops-ai/semops-sites/issues/44)
> **Depends On:** [ADR-0009](ADR-0009-resume-schema-design.md) (Resume Schema Design)

---

## Executive Summary

This ADR defines the object model for AI-assisted resume composition. The system takes a job description as input, analyzes it against a corpus of bullets and job history, and selects the optimal set of bullets for a targeted resume.

**Key insight:** Bullets are a superset for composition, not pre-curated winners. Selection happens at application time based on the target role.

---

## Part 1: Core Objects

### Bullet

The composable unit for resume building. An atomic statement of achievement that can be selected and arranged into variants.

```typescript
interface Bullet {
 id: string; // Unique identifier, e.g., "msft-01", "roku-03"
 job_id: string; // Reference to Job, e.g., "microsoft-azure"
 text: string; // The actual bullet text
 metric_types: MetricType[]; // 1-3 categories, e.g., ["Capability", "0-to-1"]
 highlight: boolean; // Recommended for leading sections
 status: BulletStatus; // Validation state
}

type BulletStatus =
 | "validated" // Research-backed, metrics confirmed
 | "enhanced" // Rewritten with additional context
 | "raw" // Original extraction, needs XYZ conversion
 ;
```

**Source:** `docs/resumes/corpus/BULLET_CORPUS.md`

**Current inventory:** 75 bullets (12 highlighted/recommended)

---

### MetricType (Enum)

Categories of PM achievement from the PM Metrics Framework. Used for bullet selection based on role priorities.

```typescript
type MetricType =
 | "Output" // Direct results: revenue, users, conversion
 | "Capability" // Platforms/infrastructure built
 | "Scope" // Scale of responsibility
 | "Speed" // Velocity of delivery
 | "Adoption" // Internal/external uptake
 | "Strategic" // Influence on direction
 | "Quality" // Reliability, satisfaction
 | "0-to-1" // Greenfield creation (modifier, can combine with others)
 ;
```

**Source:** `docs/resumes/frameworks/pm-metrics-framework.md`

**Usage:** Bullets typically have 1-3 metric types. Strong senior bullets "stack" 2-3 categories.

---

### RoleCategory (Enum)

Broad categorization of PM roles for setting selection constraints. Not for rigid matching - the agent analyzes the full JD text.

```typescript
type RoleCategory =
 | "AI_ML_PM" // ML lifecycle, AI products, model ownership
 | "Data_PM" // Data platforms, infrastructure, pipelines
 | "Media_PM" // Streaming, entertainment, advertising
 | "Growth_PM" // User acquisition, conversion, engagement
 | "Platform_PM" // Internal platforms, developer tools
 | "General_PM" // No specific category / mixed
 ;
```

**Purpose:** Enable category-specific constraints if needed (currently none defined).

**Example constraint (future):**
```
If RoleCategory == "AI_ML_PM":
 - Require at least 2 bullets with MetricType "Capability"
 - Prefer bullets mentioning ML/AI keywords
```

---

### Job

A position from Tim's employment history.

```typescript
interface Job {
 // Core identity
 id: string; // e.g., "microsoft-azure", "amazon-firetv"
 company: string;
 title: string;
 duration: string; // e.g., "Mar 2021 - Dec 2023 (2 yr 10 mo)"
 seniority: string; // Principal, Director, VP, etc.
 management: boolean;
 team_size?: string; // "5 direct, 20 indirect"

 // Dimensional attributes (for visualization/job search, not bullet selection)
 customer_type: CustomerType;
 business_model: string; // Usage-Based, Transactional, Subscription
 industry: string; // Communications Platform, Connected TV, etc.
 product_domains: string[]; // ["Data Platform", "Analytics/BI"]
 platforms: string[]; // ["Cloud", "Connected TV", "Voice"]
}

type CustomerType = "B2B" | "B2C" | "B2B2C";
```

**Source:** `docs/resumes/corpus/RESUME_CORPUS.md`

**Relationship:** Each Bullet belongs to exactly one Job (via `job_id`).

**Note on dimensional attributes:** `industry`, `platforms`, `customer_type`, `business_model`, and `product_domains` are primarily for:
1. **Portfolio visualization** on website (career timeline, skill breakdown)
2. **Job search filtering** (find roles matching experience profile)
3. **Not for bullet selection** - the agent uses MetricType matching instead

---

## Part 2: Input/Output Objects

### JobDescription (Input)

The target role being applied for. Provided by user, analyzed by agent.

```typescript
interface JobDescription {
 // User-provided
 company: string;
 title: string;
 url?: string;
 text: string; // Full JD text

 // Agent-derived (after analysis)
 role_category: RoleCategory;
 priority_metrics: MetricType[]; // Ordered by importance
 keywords: string[]; // For ATS matching
 industry?: string;
 seniority_level?: string;
 customer_type?: CustomerType;
}
```

**Analysis flow:** Agent reads full JD text → derives role_category, priority_metrics, keywords → uses these for bullet selection.

---

### Variant (Output)

A composed resume targeted for a specific job application.

```typescript
interface Variant {
 id: string;
 target: JobDescription;
 job_order: string[]; // Job IDs in display order
 selected_bullets: {
 job_id: string;
 bullet_ids: string[]; // Ordered within job section
 }[];
 created_at: Date;
 notes?: string; // Agent reasoning
}
```

**Source:** `docs/resumes/variants/` (pre-composed examples)

**Pre-composed variants:**
- `VARIANT-A-AI-ML-PM.md` - Leads with Azure → Books → Fire TV
- `VARIANT-B-DATA-PM.md` - Leads with Azure → Fire TV → Books
- `VARIANT-C-MEDIA-STREAMING-PM.md` - Leads with Fire TV → Roku → Books

---

## Part 3: Selection Algorithm

### Overview

```
JobDescription (input)
 ↓
Agent analyzes full JD text
 ↓
Derives: role_category, priority_metrics, keywords
 ↓
For each Job in preferred order:
 - Filter Bullets by metric_types ∩ priority_metrics
 - Prefer highlight=true bullets
 - Ensure coverage (at least 1 bullet per recent job)
 ↓
Compose Variant with selected bullets
```

### Selection Criteria

1. **Metric Type Match:** Bullet's metric_types should overlap with JD's priority_metrics
2. **Highlight Preference:** Bullets with `highlight=true` ranked higher
3. **Job Coverage:** Recent/relevant jobs should have at least 1-2 bullets
4. **Keyword Presence:** Bullets containing JD keywords ranked higher
5. **Seniority Match:** Job seniority should align with target role level

### Constraints (Future)

Currently no hard constraints defined. Examples for future:

```typescript
interface SelectionConstraint {
 condition: string; // e.g., "role_category == 'AI_ML_PM'"
 requirement: string; // e.g., "min 2 bullets with Capability"
}
```

---

## Part 4: Data Sources

### Current MD Files

| File | Contains | Objects |
|------|----------|---------|
| `corpus/RESUME_CORPUS.md` | Dimensional job data (14 jobs) | Job |
| `corpus/BULLET_CORPUS.md` | All 75 bullets | Bullet |
| `corpus/job-context/*.md` | Per-job working docs | (evidence, not schema) |
| `frameworks/pm-metrics-framework.md` | Metric definitions | MetricType |
| `frameworks/role-targeting-analysis.md` | Role mapping | RoleCategory |
| `variants/*.md` | Pre-composed examples | Variant |

### Database Tables (semops-sites)

Schema implemented in `semops-sites/supabase/migrations/002_resume_schema.sql`:

```sql
-- Fact table
resume_job -- Job objects (14 role-level jobs)

-- Dimension tables
resume_role -- Product Management, Engineering, etc.
resume_skill -- 2-level skill hierarchy
resume_platform -- Web, Mobile, Connected TV, etc.
resume_industry -- 3-level industry hierarchy
resume_product_domain -- Search, ML/AI, Data Platform, etc.
resume_business_model -- Subscription, Usage-Based, etc.

-- Bridge tables (many-to-many with attributes)
resume_job_role -- percentage allocation
resume_job_skill -- proficiency level
resume_job_platform -- simple join
resume_job_industry -- simple join
resume_job_product_domain
resume_job_business_model

-- Atomic content
resume_job_bullet -- Bullet objects (FK to resume_job)

-- Computed views
v_resume_job -- Job + duration_months
v_duration_by_role -- Aggregated time per role
v_company_tenure -- Aggregated tenure per company
```

---

## Part 5: Open Questions

### Resolved

1. **Is versioning needed?** → No, focus on selection not lineage
2. **What attributes for selection?** → metric_types, highlight, status
3. **Where do constraints live?** → Future: role_category-specific rules

### Open

1. **Should keywords be extracted and stored per bullet?**
 - Current: Agent extracts at selection time
 - Alternative: Pre-compute keyword tags per bullet

2. **How to handle bullet length variants?**
 - Same achievement, different verbosity
 - Currently: Different bullets with same base content
 - Alternative: Add `length: "short" | "medium" | "full"` attribute

3. **Should Job order be configurable per RoleCategory?**
 - Currently: Hard-coded in pre-composed variants
 - Alternative: Store preferred job order per RoleCategory

---

## Part 6: Cross-Repo Architecture

### Ownership Model

| Repo | Owns | Artifacts |
|------|------|-----------|
| **semops-publisher** | Content (source of truth) | `corpus/RESUME_CORPUS.md`, `corpus/BULLET_CORPUS.md`, `scripts/corpus_to_sql.py` |
| **semops-sites** | Schema & Visualization | `supabase/migrations/`, `supabase/seed.sql`, career timeline component |

### Data Flow

```
semops-publisher semops-sites
──────────────────────────── ─────────────────────
corpus/RESUME_CORPUS.md ─┐
corpus/BULLET_CORPUS.md ─┼─→ corpus_to_sql.py
 │ │
 │ ▼
 │ seed.sql (generated)
 │ │
 └─────────┼─────────────────────→ supabase/seed.sql
 │
 ▼
 002_resume_schema.sql
 │
 ▼
 Career DataViz Component
 (queries v_duration_by_role,
 v_company_tenure views)
```

### Handoff Process

1. **Content updates** happen in semops-publisher corpus files
2. **Generate seed.sql** via `python scripts/corpus_to_sql.py > seed.sql`
3. **Copy to semops-sites**: `cp seed.sql ../semops-sites/supabase/seed.sql`
4. **Test in semops-sites**: `supabase db reset` (runs migrations + seed)
5. **Commit** changes to both repos

### Job Granularity (Key Design Decision)

Jobs are split by **role change**, not just company change. This enables accurate duration aggregations in the visualization.

| Company | Role-Level Jobs |
|---------|-----------------|
| TuneUp Media | `job-tuneup-vp`, `job-tuneup-cmo` |
| IODA | `job-ioda-vp-bd`, `job-ioda-vp-marketing` |
| Lycos/TerraLycos | `job-lycos-sr-pm`, `job-terralycos-gpm` |
| Wired Digital | `job-wired-ops`, `job-wired-ad-pm` |

**Result:** 14 jobs (role-level) across 10 companies

### Why This Architecture?

1. **Content in semops-publisher**: Corpus files are the source of truth. Human-editable markdown is easier to maintain than database records.
2. **Schema in semops-sites**: Database schema, views, and aggregation logic belong with the frontend that consumes them.
3. **seed.sql as bridge**: Generated SQL is the contract between repos. Deterministic, version-controlled, testable.
4. **Views for aggregation**: `v_duration_by_role` and `v_company_tenure` compute duration metrics at query time, accounting for role percentages and ongoing positions.

---

## References

- [ADR-0009: Resume Schema Design](ADR-0009-resume-schema-design.md)
- [RESUME_SCHEMA.md](../resumes/RESUME_SCHEMA.md) - Full schema reference
- [PM Metrics Framework](../resumes/frameworks/pm-metrics-framework.md)
- [Role Targeting Analysis](../resumes/frameworks/role-targeting-analysis.md)
- [Issue #59: Resume Data Architecture](https://github.com/semops-ai/semops-publisher/issues/59)
- [Issue #56: Resume Atoms](https://github.com/semops-ai/semops-publisher/issues/56)
- [: Import updated seed.sql](https://github.com/semops-ai/semops-sites/issues/44)
