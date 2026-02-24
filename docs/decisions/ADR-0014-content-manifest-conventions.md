# ADR-0014: Content Manifest Conventions

> **Status:** Complete
> **Date:** 2026-02-08
> **Related Issue:** [#78 Content Type Manifest and Directory Conventions](https://github.com/semops-ai/semops-publisher/issues/78)
> **Builds On:** [ADR-0005: Publishing Architecture](./ADR-0005-publishing-architecture.md)

---

## Executive Summary

Establishes a content manifest format and directory conventions for semops-publisher to support multiple content types (pages, blogs, whitepapers, GitHub READMEs, LinkedIn posts). The manifest is embedded YAML frontmatter that serves as semops-publisher's contract — semops-sites and other consumers use it to drive surface-specific transforms.

---

## Context

Issue #77 (publishing marketing narrative pages to semops.ai) revealed that the existing pipeline assumes all content is blog posts. `generate_mdx.py` hardcodes semops-sites's `BlogFrontmatter` schema, destination paths, and JSX transforms. Publishing website pages required a completely ad-hoc workflow.

The @publishing-pipeline project (12 issues across 3 repos) establishes clean ownership:
- **semops-publisher** produces clean Markdown with content-level metadata
- **semops-sites** owns the "last mile" transform (MDX, surface-specific frontmatter, JSX, routing)

This ADR defines the contract format and directory organization that all pipeline issues depend on.

ADR-0005 (Publishing Architecture) deferred all pipeline complexity in favor of manual-first. This decision supersedes that deferral for content organization while preserving the incremental philosophy — we define the contract now but automate transforms later.

---

## Decision

### 1. Manifest Format: Embedded YAML Frontmatter

The content manifest is YAML frontmatter embedded in Markdown content files. This mirrors the existing hub/spoke page pattern and is simpler to maintain than a separate registry file.

**Universal fields** (all content types):

| Field | Required | Description |
|-------|----------|-------------|
| `content_type` | Yes | `page`, `blog`, `whitepaper`, `github-readme`, `linkedin` |
| `title` | Yes | Content title |
| `slug` | Yes | Kebab-case identifier |
| `author` | Yes | Author name |
| `status` | Yes | `draft-v1`, `draft-v2`, ..., `review`, `final`, `published` |
| `date_created` | Yes | YYYY-MM-DD |
| `date_updated` | Yes | YYYY-MM-DD |
| `style_guide` | Yes | `marketing-narrative`, `blog`, `whitepaper`, `technical` |
| `audience_tier` | Yes | `accessible`, `practitioner`, `technical` |
| `description` | No | One-liner summary |
| `tags` | No | List of topic tags |

**Type-specific extensions:**
- **Pages:** `doc_type` (hub/spoke), `spokes` (hub only), `hub` (spoke only)
- **Blogs:** `categories`, `concepts`, `citations` (in separate `frontmatter.yaml` for now; P-4 migrates to embedded)
- **Whitepapers:** `version`, `abstract`

### 2. Directory Conventions

```text
semops-publisher/
├── content/ # Finished content (non-blog)
│ ├── pages/ # Website pages
│ │ └── <hub-slug>/ # Hub/spoke groups (co-located)
│ │ ├── hub.md
│ │ └── spoke.md
│ ├── whitepapers/ # Whitepapers/PDFs
│ │ └── <slug>/
│ ├── github/ # GitHub READMEs
│ │ └── <repo-name>.md
│ └── linkedin/ # LinkedIn posts
│ └── <slug>.md
├── posts/ # Blog posts (existing, unchanged)
│ └── <slug>/ # Workflow stages (notes → final)
```

- `content/` holds finished (or near-finished) content for non-blog types
- `posts/` remains unchanged for the blog workflow with its stage-based convention
- Hub/spoke page groups are co-located in a subdirectory so relative references resolve

### 3. Ownership Boundary

Publisher-pr frontmatter contains **content-level metadata only**. It does not include:
- Surface-specific fields (excerpt, category mapping, Open Graph)
- Routing information (URL paths, nav placement)
- Component directives (JSX transforms, MDX imports)

Sites-pr maps semops-publisher fields to its own schema during ingestion.

### 4. WordPress Removed

WordPress is no longer a target publishing surface. All WordPress-related outputs (`wordpress.md`, `rankmathseo.yaml`) will be archived as encountered in P-4.

---

## Alternatives Considered

| Alternative | Rejected Because |
|-------------|-----------------|
| Central `content-manifest.yaml` registry | Duplicates metadata, creates sync issues with in-file frontmatter |
| Move blogs into `content/blog/` | Blogs have a multi-stage workflow (notes → draft → final); forcing them into `content/` conflates finished content with workflow stages. Deferred to P-4 evaluation. |
| Include surface fields in manifest | Violates ownership boundary; semops-sites owns surface-specific concerns |
| Flat files only (no hub/spoke directories) | Hub references spokes by relative filename; co-location keeps references valid |

---

## Consequences

**Positive:**
- Clear contract between semops-publisher and semops-sites
- Supports multiple content types without conflation
- Preserves existing blog workflow (no disruption)
- Hub/spoke co-location keeps cross-references valid
- Extensible — new content types add a directory and optional type-specific fields

**Negative:**
- Two content locations (`content/` and `posts/`) until blog migration (P-4)
- Blog posts still use separate `frontmatter.yaml` until P-4

**Risks:**
- Field names may not align perfectly with what semops-sites already built — mitigated by semops-sites owning the transform mapping

---

## Implementation Plan

### Issue #78: Foundation
- [x] Create content manifest spec (`docs/CONTENT_MANIFEST.md`)
- [x] Create `content/` directory structure
- [x] Migrate three finished pages to `content/pages/what-is-semops/`
- [x] Update frontmatter on migrated pages
- [x] Update ARCHITECTURE.md and CLAUDE.md

### Future Issues
- P-3 (#80): Formalize page creation workflow
- P-4 (#81): Migrate blog frontmatter to embedded format
- S-1 : Build ingestion script that consumes this manifest

---

## Session Log

### 2026-02-08: Initial Implementation
**Status:** In Progress
**Tracking Issue:** [#78](https://github.com/semops-ai/semops-publisher/issues/78)

**Completed:**
- Created this ADR
- Created content manifest spec
- Established directory conventions
- Migrated finished pages

---

## References

- [Content Manifest Specification](../CONTENT_MANIFEST.md)
- [ADR-0005: Publishing Architecture](./ADR-0005-publishing-architecture.md) — Superseded for content organization
- [Issue #66](https://github.com/semops-ai/semops-publisher/issues/66) — Original blog pipeline spec (closed as superseded)
- [Issue #77](https://github.com/semops-ai/semops-publisher/issues/77) — Publishing pages that exposed the gap

---

**End of Document**
