# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role in Global Architecture

**Role:** Content Creation

```
semops-dx-orchestrator [PLATFORM/DX]
 │
 └── semops-core [ORCHESTRATOR]
 │
 ├── semops-publisher [CONTENT] ◄── YOU ARE HERE
 │ - Content creation for ALL publishing surfaces
 │ - Style guides (blog, technical, whitepaper, social)
 │ - AI writing assistants and agents
 │ - Edit capture for style learning
 │
 ├── semops-docs [DOCUMENTS]
 └── semops-sites [FRONTEND]
```

**Key Ownership Boundary:**
- This repo owns **content creation** - AI-assisted writing for all formats (blogs, social, resumes, proposals, whitepapers)
- This repo owns **style guides** - voice, tone, and formatting standards for different content types
- This repo owns **AI writing tools** - agents, edit capture, style learning workflows
- `semops-core` owns **knowledge** - schema, knowledge graph, semantic operations
- `semops-docs` owns **theory** - implementation docs, conceptual documentation

**Coordinates With:**
- `semops-core` - Knowledge base queries, concept validation, frontmatter integration
- `semops-docs` - Source documents for 1P research content
- `semops-sites` - Content ingestion target (owns MDX/JSX transforms), fonts, PDF templates

## Project Overview

**AI-Assisted Content Creation System**

A content creation workflow using AI agents to research, outline, draft, and format content for multiple publishing surfaces: blogs, social media, resumes, proposals, whitepapers, and more.

**Philosophy:** Start manual, learn the workflow, automate what hurts.

### Publishing Surfaces

- Website pages (semops-sites, marketing-narrative style)
- Blog posts (semops-sites)
- Social media (LinkedIn)
- Thought leadership (whitepapers, PDFs via Pandoc)
- GitHub READMEs (manual copy)

### Content Manifest

All finished content uses embedded YAML frontmatter as a manifest — semops-publisher's contract to downstream consumers. See [docs/CONTENT_MANIFEST.md](docs/CONTENT_MANIFEST.md) for the spec and [ADR-0014](docs/decisions/ADR-0014-content-manifest-conventions.md) for the decision.

## Workflows

### Blog (agent-assisted)

```
notes.md → /research → research.md → /outline → outline_vN.md → /draft → draft.md
 → HITL Editing → final.md (+ manifest frontmatter) → /format → linkedin.md
 → Publish via semops-sites ingestion + LinkedIn manual
```

### Website Pages (manual + style guide)

```text
Plan hub/spoke → Draft in docs/drafts/ → HITL editing (marketing-narrative style)
 → Move to content/pages/ → Add manifest frontmatter → Publish via semops-sites ingestion
```

### Whitepapers, GitHub READMEs, LinkedIn (manual)

```text
Draft → HITL editing with style guide → Save to content/<type>/ → Add manifest frontmatter
 → Export (PDF for whitepapers, manual copy for GitHub/LinkedIn)
```

All content types use embedded YAML frontmatter as the manifest contract. See [docs/CONTENT_MANIFEST.md](docs/CONTENT_MANIFEST.md).

## Development Commands

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Linting
ruff check .
ruff format .

# Tests
pytest
```

## File Structure

```
content/ # Finished content (non-blog)
 pages/ # Website pages (hub/spoke groups)
 <hub-slug>/
 hub.md # Hub page with manifest frontmatter
 spoke.md # Spoke pages
 whitepapers/<slug>/ # Whitepapers/PDFs
 github/<repo-name>.md # GitHub READMEs
 linkedin/<slug>.md # LinkedIn posts

posts/ # Blog posts (workflow stages)
 <slug>/
 notes.md # Manual input - topic, POV, references
 research.md # Agent output - findings, sources
 outline_v1.md # Agent output - first outline
 outline_final.md # Final approved outline
 draft.md # Agent output - full draft
 final.md # Edited draft ready for publishing
 linkedin.md # Formatted for LinkedIn
 frontmatter.yaml # Metadata (legacy; migrating to embedded)
 assets/ # Diagrams, images, workflows
```

## Core Components

### Research Agent
- **Input:** `notes.md` with topic, POV, repo references
- **Process:** Search repos for 1P content, find 3P citations, extract concepts
- **Output:** `research.md`

### Outline Agent
- **Input:** `research.md` + `notes.md`
- **Process:** Structure argument, integrate citations, suggest visuals
- **Output:** `outline_vN.md`

### Draft Agent
- **Input:** `outline_final.md` + style references
- **Process:** Generate prose, match style, integrate citations
- **Output:** `draft.md`

### Format Agent

- **Input:** `final.md` (blog post with manifest frontmatter)
- **Process:** LinkedIn adaptation, metadata extraction
- **Output:** `linkedin.md`, `frontmatter.yaml`

## Key Concepts

### 1P vs 3P Sources
- **1P (First-Party):** Proprietary content in local repos (semops-core, semops-docs)
- **3P (Third-Party):** External sources for citations and traffic

### Style Guides

| Guide | Use For |
|-------|---------|
| [technical.md](style-guides/technical.md) | Technical documentation |
| [blog.md](style-guides/blog.md) | Blog posts, social content |
| [whitepaper.md](style-guides/whitepaper.md) | Whitepapers, thought leadership |
| [marketing-narrative.md](style-guides/marketing-narrative.md) | Website pages, framework overviews |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for full style guide documentation.

### Edit Capture Convention

When `/capture-on` is active (state file at `edits/.capture-state.json`), the agent MUST:

1. After each Edit tool call on the target file, log the edit:
 ```bash
 uv run scripts/log_edit.py --file <path> --line <N> \
 --original "<before>" --edited "<after>" \
 --reason "<why>" --style <style>
 ```
2. Always include `--reason` with a clear rationale for the edit
3. Include `--rule <guide.md#section>` when applying a known style guide rule
4. Include `--flagged` when the rationale is uncertain or the rule is new/important

**State files:**
- `edits/.capture-state.json` — Active capture session (transient, gitignored)
- `edits/.pending/<stem>.yaml` — Sidecar edit log per file (transient, gitignored)
- `edits/<date>-<stem>.yaml` — Final merged corpus (committed)

**See:** [ADR-0011: Edit Capture Intent Architecture](docs/decisions/ADR-0011-edit-capture-intent-architecture.md)

### Asset Creation (Manual in Phase 1)

- **Diagrams:** Mermaid (technical) and Excalidraw (conceptual)
- **Images:** ComfyUI workflows (save JSON for future automation)
- See [DIAGRAM_STANDARDS.md](DIAGRAM_STANDARDS.md) for specifications

## Configuration

Environment variables in `.env`:
```bash
ANTHROPIC_API_KEY=sk-...
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

## Dependencies

```
anthropic # Claude API
pydantic # Settings and data models
python-frontmatter # YAML parsing
rich # CLI output
click # CLI framework
```

## Phase Roadmap

### Phase 1 (Current): Manual & Learning
- Manual workflow, file-based, version-controlled
- Content manifest contract established (ADR-0014)
- Pipeline architecture defined (ADR-0015): semops-publisher owns content, semops-sites owns delivery
- Five content types with documented workflows: pages, blogs, whitepapers, LinkedIn, GitHub READMEs
- WordPress removed as publishing surface; `generate_mdx.py` archived
- Goal: Publish across content types, learn workflow pain points

### Phase 2: Selective Automation

- Sites-pr ingestion script  automates content delivery
- Full RAG with Project Ike knowledge base
- Edit capture corpus drives style guide hardening

### Phase 3: Scale & Learning

- Dataset collection for fine-tuning from edit corpus
- Agent-driven content workflows beyond blog (pages, whitepapers)

## Archive

See `archive/phase2-implementation-options/` for reference implementations (~80% complete) of:
- Google Drive integration
- Dual model generation
- GitHub Issues automation
- Project Ike Supabase integration
