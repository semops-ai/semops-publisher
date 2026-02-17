# semops-publisher User Guide

This guide catalogs all content creation capabilities in semops-publisher.

## Quick Reference

| Capability | Location | Description |
|------------|----------|-------------|
| **Blog** | Agent-assisted pipeline | Research, outline, draft, format workflows |
| **Pages** | `content/pages/` | Website pages (marketing-narrative, hub/spoke) |
| **Whitepapers** | `content/whitepapers/` | Long-form thought leadership -> PDF |
| **GitHub READMEs** | `content/github/` | Marketing-narrative READMEs |
| **LinkedIn** | `content/linkedin/` or blog-derived | Standalone or Format Agent output |
| **Resume** | Manual corpus editing | Atomic composition with 75 bullets |
| **PDF** | `uv run scripts/export_pdf.py` | Pandoc + XeLaTeX with templates |

---

## 1. Blog Publishing Pipeline

### Overview

```text
notes.md (manual input)
    |
Research -> research.md
    |
HITL Review
    |
Outline -> outline_vN.md
    |
HITL Iteration
    |
Draft -> draft.md
    |
HITL Editing -> final.md (+ manifest frontmatter)
    |
Format -> linkedin.md, frontmatter.yaml
    |
Publish via semops-sites ingestion + LinkedIn manual
```

### Workflows

#### Create New Post

```bash
python publish.py new <slug>
```

Creates `posts/<slug>/` directory with `notes.md` template.

#### Research

The Research workflow:

- Queries the knowledge base via MCP tools (`search_knowledge_base`, `search_chunks`)
- Supports all content types: blog, page, whitepaper, github-readme, linkedin
- Extracts research queries from input (title, POV, research topics, key concepts)
- Generates `research.md` with KB-validated findings, citations, coverage gaps
- Pinned file references (`repo:owner/repo path:path`) still supported as fallback

#### Outline

```bash
python publish.py outline <slug>
python publish.py outline <slug> --version 2
```

- Takes `notes.md` + `research.md`
- Creates hierarchical outline with citations `[^N]`
- Suggests Mermaid/Excalidraw visuals
- Output: `outline_vN.md` -> copy to `outline_final.md` when approved

#### Draft

```bash
python publish.py draft <slug>
```

- Loads `style-guides/blog.md` for tone/voice
- Expands outline into full prose
- Integrates citations, adds diagram placeholders
- Output: `draft.md` -> edit to create `final.md`

#### Format

```bash
python publish.py format <slug>
```

- Generates platform outputs:
  - `linkedin.md` - Platform-optimized (shorter, punchier, ~3000 chars)
  - `frontmatter.yaml` - Metadata for semops-core integration

Publishing to semops-sites is handled by semops-sites's ingestion script, which reads the manifest frontmatter from `final.md` and generates MDX.

#### Status

```bash
python publish.py status <slug>
python publish.py status           # List all posts
```

Shows completion state and next steps.

### Directory Structure

```text
posts/
  <slug>/
    notes.md              # Your input - topic, POV, references
    research.md           # Agent output - findings, sources
    outline_v1.md         # Agent output - first outline
    outline_final.md      # Approved outline
    draft.md              # Agent output - full draft
    final.md              # Your edited version (with manifest frontmatter)
    linkedin.md           # Formatted for LinkedIn
    frontmatter.yaml      # Metadata for semops-core
    assets/               # Diagrams, images
```

---

## 2. Resume Management

### Overview

Resume composition uses atomic bullets selected for target roles. The system has:

- **75 bullets** across 14 jobs (10 companies)
- **MetricType tags** for selection (Output, Capability, Scope, etc.)
- **Pre-composed variants** for common role types

### Key Files

| File | Purpose |
|------|---------|
| [RESUME_CORPUS.md](resumes/corpus/RESUME_CORPUS.md) | 14 jobs with dimensional data |
| [BULLET_CORPUS.md](resumes/corpus/BULLET_CORPUS.md) | 75 bullets with metric types |
| [SKILL_MAPPING.md](resumes/corpus/SKILL_MAPPING.md) | 63 job->skill mappings (17 broad categories) |
| [SKILLS_TAXONOMY.md](resumes/corpus/SKILLS_TAXONOMY.md) | 91 granular skills for LinkedIn/ATS/composable resume |
| [pm-metrics-framework.md](resumes/frameworks/pm-metrics-framework.md) | Metric categories |
| [role-targeting-analysis.md](resumes/frameworks/role-targeting-analysis.md) | Role targeting guidance |

### Workflow

1. **Analyze job description** - Identify priority metrics (Capability, Output, etc.)
2. **Select bullets** - Match metric types to job requirements
3. **Compose variant** - Arrange bullets by job order
4. **Export** - Generate final resume (future: PDF via templates)

### Pre-composed Variants

| Variant | Target Role | Job Order |
|---------|-------------|-----------|
| [VARIANT-A](resumes/variants/VARIANT-A-AI-ML-PM.md) | AI/ML PM | Azure -> Books -> Fire TV |
| [VARIANT-B](resumes/variants/VARIANT-B-DATA-PM.md) | Data PM | Azure -> Fire TV -> Books |
| [VARIANT-C](resumes/variants/VARIANT-C-MEDIA-STREAMING-PM.md) | Media/Streaming PM | Fire TV -> Roku -> Books |

### Skills System

The resume system uses **two complementary skill layers**:

1. **Skill Mappings** (`SKILL_MAPPING.md`) -- 17 broad capability categories (e.g., `ml-ai`, `product-strategy`) mapped to jobs with proficiency levels. Used for dimensional analysis in the database (`resume_job_skill` bridge table).

2. **Skills Taxonomy** (`SKILLS_TAXONOMY.md`) -- 91 granular, LinkedIn-recognizable skills (e.g., "Machine Learning", "A/B Testing", "Agile / Scrum"). Used for LinkedIn profile optimization, ATS keyword matching, and composable resume generation.

Each taxonomy skill has:

- `display_name` -- matches LinkedIn's recognized skill strings for searchability and endorsements
- `category` -- internal classification (`technical`, `domain`, `methodology`, `tool`, `soft-skill`). These are **not** LinkedIn categories; LinkedIn uses a proprietary, undocumented taxonomy. Our categories serve the composable resume filtering use case.
- `target_roles` -- which resume variants use this skill (`ai-ml-pm`, `data-pm`, `media-pm`)
- `linkedin` -- whether to include on the LinkedIn profile (targeting AI/ML PM, ~45 skills)

**Filtering skills by role:**

- AI/ML PM resume: filter where `target_roles` contains `ai-ml-pm`
- Data PM resume: filter where `target_roles` contains `data-pm`
- Media PM resume: filter where `target_roles` contains `media-pm`

### Editing Management Data

Edit `RESUME_CORPUS.md` -- columns `mgmt`, `direct`, `indirect` in the Master Jobs Table:

| Column | Type | Description |
|--------|------|-------------|
| `mgmt` | Y/N | Has management responsibility |
| `direct` | Integer | Direct reports |
| `indirect` | Integer | Indirect reports (cross-functional team members who don't report to you) |

If `mgmt=N`, set both counts to `0`. Indirect can be non-zero even when direct is `0`.

### Adding Bullets

Edit `BULLET_CORPUS.md`:

```markdown
| books-12 | New bullet text here | Output, Capability | | validated |
```

ID convention: `{job-prefix}-{NN}` (e.g., `msft-01`, `books-12`, `firetv-03`)

### Database Sync

```bash
# Generate SQL for semops-sites
python scripts/corpus_to_sql.py > ../semops-sites/supabase/seed_resume.sql
```

---

## 3. PDF Export

### Quick Start

```bash
# Basic export
uv run scripts/export_pdf.py input.md -o output.pdf

# With template
uv run scripts/export_pdf.py input.md -o output.pdf --template semops

# With table of contents
uv run scripts/export_pdf.py input.md -o output.pdf --toc

# Batch export
uv run scripts/export_pdf.py *.md -o output_dir/
```

### Templates

| Template | Typography | Use Case |
|----------|------------|----------|
| `semops` | DM Sans + JetBrains Mono | Consulting proposals, professional |
| `timjmitchell` | Inter + Lora (serif) | Personal brand, elegant |
| `technical` | Inter + JetBrains Mono | Technical docs, code-heavy |
| `resume` | Inter + Lora (serif) | Resumes, 2-page format |

### Features

- **Mermaid diagrams** - Auto-rendered to PNG
- **Syntax highlighting** - Code blocks with tango theme
- **Custom fonts** - XeLaTeX with bundled fonts
- **Table of contents** - Optional via `--toc`

### Requirements

- `pandoc` (document converter)
- `xelatex` (TeX Live or MacTeX)
- `mermaid-cli` (optional, for diagrams)
- Fonts installed from semops-sites font packages

---

## 4. Content Types (Non-Blog)

All non-blog content lives in `content/` with embedded YAML frontmatter (the content manifest). See [CONTENT_MANIFEST.md](CONTENT_MANIFEST.md) for the full spec.

### Website Pages

Marketing-narrative pages for semops.ai. Hub/spoke structure for interconnected content.

- **Directory:** `content/pages/<hub-slug>/`
- **Style:** `marketing-narrative` (founder-practitioner voice)
- **Workflow:** Plan -> draft in `docs/drafts/` -> HITL editing -> move to `content/pages/` -> add frontmatter -> publish via semops-sites

See [content/pages/README.md](../content/pages/README.md) for full workflow.

### Whitepapers

Long-form thought leadership -> PDF via Pandoc.

- **Directory:** `content/whitepapers/<slug>/`
- **Style:** `whitepaper` (authoritative, evidence-backed)
- **Length:** 3,000-4,500 words (marketing) or 4,500-7,000 words (research)
- **Workflow:** Draft iterations in `posts/whitepaper-<slug>/` -> HITL editing -> move to `content/whitepapers/` -> add frontmatter -> export PDF

```bash
uv run scripts/export_pdf.py content/whitepapers/<slug>/<slug>.md -o output.pdf --template semops
```

See [content/whitepapers/README.md](../content/whitepapers/README.md) for full workflow.

### GitHub READMEs

Marketing-narrative READMEs for public repos. Simplest content type -- manual copy.

- **Directory:** `content/github/<repo-name>.md`
- **Style:** `marketing-narrative` (500-1,500 words)
- **Workflow:** Draft -> add frontmatter -> strip frontmatter and copy to target repo

See [content/github/README.md](../content/github/README.md) for full workflow.

### LinkedIn Posts

Two paths: blog-derived (Format Agent) or standalone originals.

- **Blog-derived:** `posts/<slug>/linkedin.md` (generated by Format workflow)
- **Standalone:** `content/linkedin/<slug>.md`
- **Style:** `blog` (conversational, ~3,000 chars, hashtags, CTA)

See [content/linkedin/README.md](../content/linkedin/README.md) for full workflow.

---

## 5. Style Guides

| Guide | Use For | Key Rules |
|-------|---------|-----------|
| [blog.md](../style-guides/blog.md) | Blog, social, LinkedIn | Voice, tone, formatting |
| [whitepaper.md](../style-guides/whitepaper.md) | Long-form, thought leadership | Authority, depth |
| [technical.md](../style-guides/technical.md) | Technical docs | Clarity, precision |
| [marketing-narrative.md](../style-guides/marketing-narrative.md) | Website pages, GitHub READMEs | Founder-practitioner voice |
| [semantic-funnel-section.md](../style-guides/semantic-funnel-section.md) | Semantic Funnel H2 sections in framework docs | Coverage diagram + OAR breakdown table |
| [DIAGRAM_STANDARDS.md](../DIAGRAM_STANDARDS.md) | Visuals | Mermaid, Excalidraw specs |

---

## 6. Edit Capture (Style Learning)

Capture edits with editorial intent for style guide hardening and training data.

### Two Capture Paths

**Agent edits (real-time sidecar):**

1. Enable capture for a target file
2. Agent edits the file -- each edit is logged with reason and style metadata to `edits/.pending/<stem>.yaml`
3. Review sidecar mid-session if desired
4. Disable capture

**Cross-repo editing:**

Edit capture accepts absolute paths to files in other repos. This repo is always the hub for edit capture. The file is edited in-place at its source location, while sidecar logs are written to semops-publisher's `edits/.pending/` directory.

Two ways to make cross-repo edits:

- **Agent-assisted:** Stay in semops-publisher and direct the agent to edit the file using its absolute path. Each edit is logged automatically.
- **Manual:** Navigate to the target repo and edit the file yourself. Return to semops-publisher to finalize.

On capture completion, the changes are committed in the source repo automatically. This gives lineage in both repos -- the source repo gets the commit, semops-publisher gets the edit corpus with `source_repo` provenance.

**Human edits (post-hoc diff):**

1. AI generates draft with commit tag: `git commit -m "[ai-draft] Description"`
2. Human edits the draft
3. Run capture for the file
4. Script diffs, merges any sidecar data, prompts for rationale on human edits
5. Output: `edits/<date>-<filename>.yaml`

### Output Format

```yaml
source_file: posts/example/content.md
ai_draft_commit: abc1234
editor_type: human
style: blog
session_reason: null
edits:
  - id: edit-001
    original: "Our focus is..."
    edited: "My focus is..."
    line_number: 42
    reason: "First person consistency"
    rule_applied: "blog.md#voice"
    editor_type: human
    flagged: false
```

### Key Files

| File | Purpose |
|------|---------|
| `scripts/log_edit.py` | Agent calls this to append edits to sidecar |
| `scripts/capture_edits.py` | Diff-based capture with sidecar merge |
| `edits/.pending/` | Transient sidecar logs (gitignored) |
| `edits/<date>-<stem>.yaml` | Final merged corpus (committed) |

### Corpus Review (Style Learning Feedback Loop)

Once you have a few corpus files in `edits/`, run the corpus review workflow.

This analyzes all corpus YAML files, clusters edit reasons by theme (jargon reduction, scannability, redundancy removal, etc.), ranks by frequency and flagged count, and presents candidate rules for triage.

For each cluster you can:
- **Promote** -- Save to `style-guides/distilled-rules.yaml` AND add to a style guide
- **Save** -- Save to `style-guides/distilled-rules.yaml` only
- **Skip** -- Not actionable yet

Distilled rules are automatically loaded as agent context when capture starts a new session, closing the feedback loop:

```
Edits -> Corpus -> Corpus Review -> Distilled rules -> Agent context on capture start
```

| File | Purpose |
|------|---------|
| `style-guides/distilled-rules.yaml` | Distilled rule set (output of corpus review) |

See ADR-0011 for full architecture.

---

## 7. Experimental Framework

### Setup Parallel Experiments

The experiment preparation workflow creates Docker-based A/B test environments in `experiments/`.

### Execute and Compare

The experiment execution workflow runs experiments and generates comparison report.

---

## 8. SpecKit (Feature Specification)

Advanced workflow for structured feature development.

| Capability | Purpose |
|------------|---------|
| Specify | Create feature spec from natural language |
| Clarify | Ask clarification questions |
| Plan | Generate implementation plan |
| Tasks | Create ordered task list |
| Tasks to Issues | Convert tasks to GitHub issues |
| Implement | Execute the plan |
| Analyze | Cross-artifact consistency check |

---

## Environment Setup

### Prerequisites

```bash
# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or with uv
uv sync
```

### Configuration

Copy `.env.example` to `.env`:

```bash
ANTHROPIC_API_KEY=sk-...
CLAUDE_MODEL=claude-sonnet-4-20250514
```

### PDF Export Dependencies

```bash
# macOS
brew install pandoc mactex

# Ubuntu/Debian
sudo apt install pandoc texlive-xetex texlive-fonts-extra

# Mermaid (optional)
npm install -g @mermaid-js/mermaid-cli
```

---

## Cross-Repo Dependencies

| Repo | Provides |
|------|----------|
| `semops-core` | Knowledge base, concept validation |
| `semops-docs` | 1P source documents for research |
| `semops-sites` | PDF templates, fonts, career dataviz |

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [RUNBOOK.md](RUNBOOK.md) - Operations reference
- [decisions/](decisions/) - Architecture decisions
