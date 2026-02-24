# Content Manifest Specification

> **ADR:** [ADR-0014](decisions/ADR-0014-content-manifest-conventions.md)
> **Version:** 1.0
> **Last Updated:** 2026-02-08

## Overview

The content manifest is YAML frontmatter embedded in Markdown content files. It serves as semops-publisher's contract describing finished content. Downstream consumers (semops-sites, PDF export, manual publishing) use it to drive surface-specific transforms.

Publisher-pr frontmatter contains **content-level metadata only** — no surface-specific fields (routing, excerpt mapping, JSX directives). Sites-pr owns the transform from this contract to its own schema.

## Universal Fields

All content types include these fields in their YAML frontmatter:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `content_type` | enum | Yes | `page` \| `blog` \| `whitepaper` \| `github-readme` \| `linkedin` |
| `title` | string | Yes | Content title |
| `slug` | string | Yes | Kebab-case identifier (unique within content type) |
| `author` | string | Yes | Author name |
| `status` | string | Yes | Lifecycle status (see below) |
| `date_created` | date | Yes | YYYY-MM-DD |
| `date_updated` | date | Yes | YYYY-MM-DD |
| `style_guide` | enum | Yes | `marketing-narrative` \| `blog` \| `whitepaper` \| `technical` |
| `audience_tier` | enum | Yes | `accessible` \| `practitioner` \| `technical` |
| `description` | string | No | One-liner summary for use by any surface |
| `tags` | list | No | Topic tags |

### Status Lifecycle

```
draft-v1 → draft-v2 → ... → review → final → published
```

- `draft-vN` — Work in progress, numbered for version tracking
- `review` — Content complete, pending final review
- `final` — Approved for publishing
- `published` — Live on at least one surface

## Content Types

### page

Website pages using the marketing-narrative style. Supports hub/spoke structure for interconnected content.

**Directory:** `content/pages/`

**Layout:**
- Hub/spoke groups: `content/pages/<hub-slug>/` (all related files co-located)
- Standalone pages: `content/pages/<slug>.md`

**Additional fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `doc_type` | enum | Yes | `hub` \| `spoke` |
| `spokes` | list | Hub only | Filenames of spoke documents (relative) |
| `hub` | string | Spoke only | Filename of hub document (relative) |

**Example (hub):**

```yaml
---
content_type: page
doc_type: hub
title: "What is Semantic Operations?"
slug: what-is-semops
author: Tim Mitchell
spokes:
 - why-semops.md
 - framework.md
 - how-i-got-here.md
audience_tier: accessible
style_guide: marketing-narrative
status: published
date_created: 2026-02-03
date_updated: 2026-02-06
tags:
 - semops
 - framework
---
```

**Example (spoke):**

```yaml
---
content_type: page
doc_type: spoke
title: "Why SemOps?"
slug: why-semops
author: Tim Mitchell
hub: what-is-semops.md
audience_tier: accessible
style_guide: marketing-narrative
status: published
date_created: 2026-02-03
date_updated: 2026-02-06
---
```

### blog

Blog posts with a multi-stage workflow (notes → research → outline → draft → final).

**Directory:** `posts/<slug>/` (existing convention, unchanged)

**Workflow files:**

```
posts/<slug>/
 notes.md # Manual input
 research.md # Agent output
 outline_v1.md # Outline drafts
 outline_final.md # Approved outline
 draft.md # Agent-generated draft
 final.md # Edited final version
 linkedin.md # LinkedIn format
 frontmatter.yaml # Metadata (legacy; P-4 migrates to embedded)
 assets/ # Diagrams, images
```

**Current state:** Blog metadata lives in a separate `frontmatter.yaml` file with fields like `title`, `slug`, `categories`, `concepts`, `citations`. Issue P-4 (#81) will migrate this to embedded frontmatter matching the universal manifest format.

### whitepaper

Long-form thought leadership documents.

**Directory:** `content/whitepapers/<slug>/`

**Additional fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | No | Version identifier (e.g., "v1", "v2") |
| `abstract` | string | No | Extended summary |

### github-readme

Marketing-narrative READMEs for public repositories.

**Directory:** `content/github/<repo-name>.md`

No additional fields beyond universal. Simplest content type — Markdown output, manual copy to target repo.

### linkedin

LinkedIn posts, either derived from blog posts or original.

**Directory:** `content/linkedin/<slug>.md`

No additional fields beyond universal. The blog format agent currently generates `linkedin.md` within `posts/<slug>/`; standalone LinkedIn content goes here.

## Directory Layout

```text
semops-publisher/
├── content/ # Finished content (non-blog)
│ ├── pages/ # Website pages
│ │ └── what-is-semops/ # Hub/spoke group
│ │ ├── what-is-semops.md # Hub
│ │ ├── why-semops.md # Spoke
│ │ └── how-i-got-here.md # Spoke
│ ├── whitepapers/ # Whitepapers/PDFs
│ ├── github/ # GitHub READMEs
│ └── linkedin/ # LinkedIn posts
├── posts/ # Blog posts (workflow stages)
│ ├── _references/ # Style reference posts
│ └── <slug>/ # Per-post workflow directory
└── docs/drafts/ # Working drafts (not published)
```

## Ownership Boundary

| Concern | Owner | In Manifest? |
|---------|-------|-------------|
| Title, slug, author | semops-publisher | Yes |
| Style guide, audience tier | semops-publisher | Yes |
| Status, dates | semops-publisher | Yes |
| Tags, description | semops-publisher | Yes |
| Hub/spoke structure | semops-publisher | Yes |
| Excerpt (derived from description) | semops-sites | No |
| URL routing | semops-sites | No |
| Category/taxonomy mapping | semops-sites | No |
| MDX/JSX transforms | semops-sites | No |
| Open Graph metadata | semops-sites | No |

## References

- [ADR-0014: Content Manifest Conventions](decisions/ADR-0014-content-manifest-conventions.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
