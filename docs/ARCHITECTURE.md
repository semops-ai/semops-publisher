# Architecture

> **Repo:** `semops-publisher`
> **Role:** Publishing/Content - AI-assisted content creation for all publishing surfaces
> **Status:** ACTIVE
> **Version:** 1.4.0
> **Last Updated:** 2026-02-06

## Role

Publisher-pr is the **content creation** domain within SemOps. It transforms notes, ideas, and unstructured information into quality, properly formatted published content through AI-assisted workflows for multiple surfaces: blogs, social media, resumes, proposals, whitepapers, and more.

**Key Ownership:**

- **Style guides** - Voice, tone, and formatting standards for different content types and audiences
- **AI writing assistants** - Agents for research, outline, draft, format
- **Edit capture** - Workflow to capture human edits for style learning
- **Resume composition** - Dimensional schema for structured career data (migrating to own repo, see P-5)
- **Content manifest** - Contract format for finished content ([spec](CONTENT_MANIFEST.md))
- **Multi-surface publishing** - Pages, blogs, whitepapers, social, professional docs
- **23 slash commands** - Claude Code workflows for content creation

## System Overview

```text
┌─────────────────────────────────────────────────────────────────┐
│ semops-publisher │
│ │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│ │ Content │───▶│ Image/ │───▶│ Publishing │ │
│ │ Agents │ │ Video │ │ Surfaces │ │
│ │ │ │ Stack │ │ │ │
│ │ - Research │ │ │ │ - semops-sites (pages) │ │
│ │ - Outline │ │ - ComfyUI │ │ - semops-sites (blog) │ │
│ │ - Draft │ │ - RunPod │ │ - LinkedIn │ │
│ │ - Format │ │ - APIs │ │ - PDF │ │
│ └─────────────┘ └─────────────┘ └─────────────────────┘ │
│ │ │ │ │
│ └──────────────────┴──────────────────────┘ │
│ │ │
│ ~/models/ │
│ (centralized model storage) │
└─────────────────────────────────────────────────────────────────┘
```

## Slash Commands

23 Claude Code commands for content workflows:

| Command | Purpose |
|---------|---------|
| `/new-post` | Create new blog post structure |
| `/research` | RAG-powered research via semops-kb (all content types) |
| `/outline` | Generate outline |
| `/draft` | Generate draft |
| `/format` | Format for platforms |
| `/publish-mdx` | Generate MDX for semops-sites |
| `/capture-on` | Start edit capture session |
| `/capture-off` | End edit capture session |
| `/capture-edits` | Diff-based edit capture |
| `/corpus-review` | Review edit corpus for rules |
| `/status` | Post status check |
| `/speckit.*` | Specification toolkit (7 commands) |
| `/prime` | Prime context |
| `/prep-parallel-experiments` | Prepare parallel experiments |
| `/execute-parallel-experiments` | Execute experiments |

**Location:** `.claude/commands/`

## Core Components

### 1. Content Creation Agents

AI agents that assist with content creation. Currently Claude-based via Claude Code.

| Agent | Purpose | Input | Output |
|-------|---------|-------|--------|
| Research | RAG-powered evidence gathering via semops-kb | Notes/input file (any content type) | `research.md` |
| Outline | Structure argument | `notes.md` + `research.md` | `outline_vN.md` |
| Draft | Generate full prose | `outline_final.md` | `draft.md` |
| Format | Platform adaptation | `final.md` | `linkedin.md`, `frontmatter.yaml` |

The **Research** agent (`/research` command) queries the semops-kb knowledge base via MCP tools (`search_knowledge_base`, `search_chunks`) to find 1P evidence, validate concepts, and identify coverage gaps. It supports all content types (blog, page, whitepaper, github-readme, linkedin). A Python fallback (`publish.py research`) exists for non-interactive use but does not query the KB.

**Location:** `agents/` (Python agents), `.claude/commands/` (slash command orchestration)

**Entry Points:**

```bash
# Preferred: RAG-powered via slash command (queries KB)
/research [content-type] [slug]

# Fallback: Python CLI (no KB integration)
python publish.py research <slug>

# Other agents (Python CLI)
python publish.py new <slug>
python publish.py outline <slug> [-v N]
python publish.py draft <slug>
python publish.py format <slug>
```

### 2. Resume Composition System

Dimensional schema for structured career data, enabling adaptive resume generation.

**Architecture:**

```text
semops-publisher (Content Source) semops-sites (Schema Implementation)
───────────────────────────── ────────────────────────────────
corpus/RESUME_CORPUS.md ────┐
corpus/BULLET_CORPUS.md ────┼──→ scripts/corpus_to_sql.py
 │ │
 │ ▼
 │ seed.sql
 │ │
 │ ▼
 └────→ supabase/migrations/
 │
 ▼
 Career DataViz Component
```

**Dimensional Model:**

| Table | Purpose |
|-------|---------|
| `resume_job` (fact) | Atomic work experience units |
| `resume_role` (dim) | Job functions (PM, PMM, Eng) |
| `resume_company` (dim) | Company information |
| `resume_skill` (dim) | Skills taxonomy |
| `resume_bullet` (fact) | Achievement bullets with skill tags |

**Key Files:**

- `docs/resumes/RESUME_SCHEMA.md` - Schema reference
- `docs/resumes/corpus/` - Content corpus
- `docs/resumes/variants/` - Generated resume variants
- `scripts/corpus_to_sql.py` - Generate seed.sql

**See:** [ADR-0010: Resume Composition Schema](decisions/ADR-0010-resume-composition-schema.md)

### 3. Content Manifest

Publisher-pr defines a content manifest format — embedded YAML frontmatter in Markdown files — that serves as the contract between semops-publisher (content creation) and semops-sites (surface delivery). Publisher-pr produces clean Markdown with content-level metadata; semops-sites owns MDX/JSX transforms, surface-specific frontmatter, and routing.

**Spec:** [docs/CONTENT_MANIFEST.md](CONTENT_MANIFEST.md)

**Content types:** `page`, `blog`, `whitepaper`, `github-readme`, `linkedin`

**Key fields:** `content_type`, `title`, `slug`, `author`, `status`, `style_guide`, `audience_tier`

**See:** [ADR-0014: Content Manifest Conventions](decisions/ADR-0014-content-manifest-conventions.md)

> **Note:** `scripts/generate_mdx.py` has been archived to `archive/generate_mdx.py`. MDX generation is now semops-sites's responsibility via its ingestion script .

### 4. Website Page Workflow

Pages use the marketing-narrative style guide and support hub/spoke document structure for interconnected content (e.g., "What is SemOps?" hub with "Why SemOps?" and "How I Got Here" spokes).

**Workflow:**

```text
Plan structure (hub/spoke) → Draft in docs/drafts/ → HITL editing → Move to content/pages/ → Add manifest frontmatter → Publish via semops-sites
```

**Key conventions:**

- Hub/spoke groups co-locate in `content/pages/<hub-slug>/`
- Standalone pages live as `content/pages/<slug>.md`
- Hub pages list spokes by relative filename; spoke pages reference their hub
- Markdown links between siblings use relative paths (semops-sites converts to URLs)
- All pages use `style_guide: marketing-narrative` and declare `audience_tier`

**Location:** `content/pages/` — see [README](../content/pages/README.md) for full workflow documentation.

### 5. GitHub README Workflow

Marketing-narrative READMEs for public-facing repositories. The simplest content type — Markdown output, manual copy to target repo, no transform needed.

**Workflow:**

```text
Identify target repo → Draft with marketing-narrative style → Add manifest frontmatter → Manual copy to target repo (strip frontmatter)
```

**Key conventions:**

- One file per repo: `content/github/<repo-name>.md`
- Style: `marketing-narrative` (founder-practitioner voice, SCQ-A arc condensed)
- Audience: typically `accessible` tier (500–1,500 words)
- No semops-sites involvement — GitHub renders Markdown natively
- Source material: brand positioning docs, published pages, overview narratives

**Location:** `content/github/` — see [README](../content/github/README.md) for full workflow documentation.

### 6. Whitepaper Workflow

Long-form thought leadership documents exported as PDFs via Pandoc + XeLaTeX (ADR-0009).

**Workflow:**

```text
Plan scope → Research/outline → Draft iterations in posts/ → HITL editing → Move to content/whitepapers/<slug>/ → Add manifest frontmatter → Export PDF
```

**Key conventions:**

- Each whitepaper gets its own directory: `content/whitepapers/<slug>/`
- Working drafts iterate in `posts/whitepaper-<slug>/` before moving to `content/`
- Style: `whitepaper` (authoritative, evidence-backed, framework-oriented)
- Length: 3,000–4,500 words (marketing) or 4,500–7,000 words (research)
- Whitepaper-specific fields: `version`, `abstract`
- PDF export: `uv run scripts/export_pdf.py <input>.md -o <output>.pdf --template semops`

**Location:** `content/whitepapers/` — see [README](../content/whitepapers/README.md) for full workflow documentation.

### 7. LinkedIn Workflow

LinkedIn posts follow two paths: blog-derived (Format Agent) or standalone (original content).

**Blog-derived path:**

```text
posts/<slug>/final.md → python publish.py format <slug> → posts/<slug>/linkedin.md
```

**Standalone path:**

```text
Draft → Write with blog style + LinkedIn constraints → Save to content/linkedin/<slug>.md → Add frontmatter → Manual copy-paste
```

**Key conventions:**

- Blog-derived posts stay in `posts/<slug>/linkedin.md` (generated by Format Agent)
- Standalone posts go in `content/linkedin/<slug>.md` with manifest frontmatter
- Style: `blog` (conversational, punchier paragraphs, hooks and questions)
- Target: ~3,000 characters (LinkedIn truncates longer posts)
- No markdown rendering on LinkedIn — use line breaks and spacing for structure
- End with call-to-action and 3–5 hashtags

**Location:** `content/linkedin/` — see [README](../content/linkedin/README.md) for full workflow documentation.

### 8. Image/Video Generation Stack

Multi-environment architecture for AI image and video generation.

```text
┌─────────────────────────────┐
│ Local (GPU Box) │
│ - Interactive lookdev │
│ - SDXL + LoRAs │
│ - Basic ControlNets │
└─────────────┬───────────────┘
 │
 ▼
┌─────────────────────────────┐
│ RunPod (Cloud GPU) │
│ - Heavy/batch jobs │
│ - AnimateDiff, SVD │
│ - Advanced ControlNets │
│ - FastAPI proxy layer │
└─────────────┬───────────────┘
 │
 ▼
┌─────────────────────────────┐
│ External APIs │
│ - Kling, Fal, Replicate │
│ - Video generation │
└─────────────────────────────┘
```

**Location:** `comfyui/`

**Key Files:**

- `comfyui/docker-compose.yml` - Local ComfyUI setup
- `comfyui/generate.py` - Programmatic generation
- `comfyui/download-models.sh` - Model provisioning

**See:** [ADR-0004: ComfyUI for Image Generation](decisions/ADR-0004-COMFYUI-IMAGE-GENERATION.md)

### 9. Model Storage

Centralized storage for all ML models using tool-native directory structures.

**Location:** `~/models/` (dedicated data drive)

```text
~/models/
├── checkpoints/ # ComfyUI - Base models (SDXL, SD 1.5, etc.)
├── loras/ # ComfyUI - LoRA models
├── controlnet/ # ComfyUI - ControlNet models
├── vae/ # ComfyUI - VAE models
├── clip/ # ComfyUI - CLIP models
├── clip_vision/ # ComfyUI - CLIP vision models
├── ipadapter/ # ComfyUI - IP-Adapter models
├── upscale_models/ # ComfyUI - Upscalers
├── ollama/ # Ollama - LLM models
├── embeddings/ # Shared - Text embeddings
└── gguf/ # Local LLMs - GGUF format
```

**See:** [ADR-0006: Model Storage Architecture](decisions/ADR-0006-model-storage-architecture.md)

### 10. Style Guides

Style guides define voice, tone, and formatting for different content types.

| Guide | Purpose | Voice |
|-------|---------|-------|
| `technical.md` | Technical documentation | Objective 3rd person |
| `blog.md` | Blog posts, social | Conversational |
| `whitepaper.md` | Thought leadership | Authoritative |
| `marketing-narrative.md` | Evergreen web pages, framework overviews | Founder-practitioner |

**Location:** `style-guides/`

### 11. Edit Capture (Style Learning)

Captures edits with editorial intent for style guide hardening and training data.

**Two capture paths:**

| Path | Editor | Mechanism |
|------|--------|-----------|
| Sidecar append log | Agent | `scripts/log_edit.py` writes to `edits/.pending/` |
| Diff + rationale | Human | `scripts/capture_edits.py` diffs `[ai-draft]` commit |

**Key Files:**

- `scripts/log_edit.py` - CLI helper, appends structured YAML
- `scripts/capture_edits.py` - Diff-based capture with sidecar merge
- `edits/.pending/` - Transient sidecar logs (gitignored)
- `edits/<date>-<stem>.yaml` - Final merged corpus

**Schema:** `original`, `edited`, `reason`, `rule_applied`, `editor_type`, `style`, `flagged`, `timestamp`

**See:** [ADR-0011: Edit Capture Intent Architecture](decisions/ADR-0011-edit-capture-intent-architecture.md)

### 12. PDF Export

Export markdown to professional PDFs using Pandoc with custom LaTeX templates.

**Script:** `scripts/export_pdf.py`

**Templates:** (from `semops-sites/packages/pdf-templates/`)

| Template | Typography | Use Case |
|----------|------------|----------|
| `semops` | DM Sans + JetBrains Mono | Consulting proposals |
| `timjmitchell` | Inter + Lora | Personal brand docs |
| `technical` | Inter + JetBrains Mono | Technical documentation |
| `resume` | Inter + Lora | Resumes, 2-page format |

**See:** [ADR-0007: Pandoc PDF Export](decisions/ADR-0007-pandoc-pdf-export.md)

### 13. Publishing Surfaces

Target platforms for content distribution. Publisher-pr produces clean Markdown with manifest frontmatter; semops-sites handles the transform to MDX.

| Surface | Content Types | Method |
|---------|---------------|--------|
| semops-sites (pages) | `page` | Manifest → semops-sites ingestion script |
| semops-sites (blog) | `blog` | Manifest → semops-sites ingestion script |
| LinkedIn | `linkedin`, `blog` (derived) | Manual |
| PDF | `whitepaper`, `resume` | Pandoc + XeLaTeX |
| GitHub | `github-readme` | Manual copy |

**See:** [ADR-0014: Content Manifest Conventions](decisions/ADR-0014-content-manifest-conventions.md)

## Directory Structure

```text
semops-publisher/
├── .claude/
│ └── commands/ # 23 slash commands
├── content/ # Finished content (non-blog)
│ ├── pages/ # Website pages
│ │ └── what-is-semops/ # Hub/spoke group (co-located)
│ ├── whitepapers/ # Whitepapers/PDFs
│ ├── github/ # GitHub READMEs
│ └── linkedin/ # LinkedIn posts
├── posts/ # Blog posts (workflow stages)
│ ├── _references/
│ └── <post-slug>/
├── agents/ # AI agents for content creation
│ ├── research.py
│ ├── outline.py
│ ├── draft.py
│ └── formatter.py
├── comfyui/ # Image generation stack
│ ├── docker-compose.yml
│ ├── generate.py
│ └── workflows/
├── scripts/
│ ├── export_pdf.py # PDF export
│ ├── corpus_to_sql.py # Resume seed generation
│ ├── capture_edits.py # Edit capture
│ └── log_edit.py # Edit logging
├── docs/
│ ├── ARCHITECTURE.md # This file
│ ├── CONTENT_MANIFEST.md # Content manifest spec
│ ├── resumes/ # Resume composition system
│ │ ├── RESUME_SCHEMA.md
│ │ ├── corpus/
│ │ └── variants/
│ └── decisions/ # ADRs
├── style-guides/ # Voice and tone guides
├── edits/ # Edit capture corpus
├── experiments/ # Content experiments
├── prompts/ # Agent prompt templates
├── publish.py # Main CLI
├── config.py # Configuration
└── CLAUDE.md # Claude Code instructions
```

**See:** [Content Manifest Specification](CONTENT_MANIFEST.md) for directory conventions per content type.

## Integration Points

### semops-core

- **Knowledge Base:** PostgreSQL with pgvector (entities, document chunks)
- **MCP Server:** `/research` command queries KB directly via `semops-kb` MCP tools (`search_knowledge_base`, `search_chunks`, `list_corpora`). Configured globally in `~/.claude.json` (stdio transport).
- **Concept Validation:** Validate `{{concept-name}}` tags against KB entities
- **Frontmatter Integration:** Published content registers in knowledge graph

**See:** [ADR-0006: Knowledge Base Context Integration](decisions/ADR-0006-knowledge-base-context-integration.md)

### semops-sites

- **Content Ingestion:** Publisher-pr produces Markdown with manifest frontmatter; semops-sites transforms to MDX 
- **Page Publishing:** `content/pages/` → `apps/semops/content/pages/` (about, framework)
- **Blog Publishing:** `posts/<slug>/final.md` → `apps/semops/content/blog/` or `apps/timjmitchell/content/blog/`
- **Resume Schema:** `corpus_to_sql.py` generates seed.sql for Supabase
- **PDF Templates:** Uses fonts and templates from `semops-sites/packages/`

### semops-dx-orchestrator

- **Domain Patterns:** Style guides referenced by dx-hub domain-patterns
- **Edit Corpus:** Training data for style learning

## Configuration

### Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-... # Claude API
CLAUDE_MODEL=claude-sonnet-4-20250514

# Supabase (for knowledge base integration)
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...

# Hugging Face (for model registry)
HF_TOKEN=...
```

## Related ADRs

| ADR | Topic |
|-----|-------|
| [ADR-0001](decisions/ADR-0001-claude-code-runtime.md) | Claude Code as Agent Runtime |
| [ADR-0005](decisions/ADR-0005-publishing-architecture.md) | Publishing Architecture (Superseded by ADR-0015) |
| [ADR-0006](decisions/ADR-0006-knowledge-base-context-integration.md) | Knowledge Base Context Integration |
| [ADR-0007](decisions/ADR-0007-comfyui-image-generation.md) | ComfyUI for Image Generation |
| [ADR-0008](decisions/ADR-0008-model-storage-architecture.md) | Model Storage Architecture |
| [ADR-0009](decisions/ADR-0009-pandoc-pdf-export.md) | Pandoc PDF Export |
| [ADR-0012](decisions/ADR-0012-resume-composition-model.md) | Resume Composition Model |
| [ADR-0013](decisions/ADR-0013-edit-capture-intent-architecture.md) | Edit Capture Intent Architecture |
| [ADR-0014](decisions/ADR-0014-content-manifest-conventions.md) | Content Manifest Conventions |
| [ADR-0015](decisions/ADR-0015-publishing-pipeline-architecture.md) | Publishing Pipeline Architecture |

## Dependencies

| Repo | What We Use |
|------|-------------|
| semops-core | Knowledge base, MCP server, patterns |
| semops-sites | PDF templates, fonts, content ingestion target |

## Depended On By

| Repo | What They Use |
|------|---------------|
| semops-sites | MDX content, resume seed.sql |
| semops-dx-orchestrator | Style guides for domain patterns |

## References

- [CLAUDE.md](../CLAUDE.md) - Claude Code instructions for this repo
- [README.md](../README.md) - Quick start guide
- [GLOBAL_ARCHITECTURE.md](https://github.com/semops-ai/semops-dx-orchestrator/blob/main/docs/GLOBAL_ARCHITECTURE.md) - SemOps system overview
