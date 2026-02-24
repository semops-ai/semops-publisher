# ADR-0015: Publishing Pipeline Architecture

> **Status:** Complete
> **Date:** 2026-02-08
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/79)
> **Supersedes:** [ADR-0005: Publishing Architecture](./ADR-0005-publishing-architecture.md)
> **Builds On:** [ADR-0014: Content Manifest Conventions](./ADR-0014-content-manifest-conventions.md)

---

## Executive Summary

Establishes a clean ownership split for the publishing pipeline: semops-publisher produces finished Markdown with embedded YAML frontmatter (the content manifest); semops-sites owns surface-specific transforms, MDX/JSX generation, routing, and deployment. WordPress is removed as a target surface. Resume is designated for extraction to its own bounded context.

---

## Context

### What Changed Since ADR-0005

ADR-0005 (Dec 2025) was a "defer complexity" decision — the right call at the time. After publishing several posts and building the first website pages, real pain points emerged:

1. **Issue #66** (Blog Publishing Pipeline spec) baked semops-sites concerns into semops-publisher — `generate_mdx.py` imports `BlogFrontmatter` from semops-sites, hardcodes destination paths, and does JSX transforms that belong in the delivery layer.

2. **Issue #77** (Publish marketing-narrative pages to semops.ai) revealed that the blog-only pipeline couldn't handle website pages at all. Pages required a completely ad-hoc workflow — manual copying, frontmatter rewriting, no defined conventions.

3. **Issue #67** (V1 manual MDX generation) shipped `generate_mdx.py` as a stopgap, but it coupled the two repos and couldn't generalize beyond blog posts.

### Trigger Conditions Met

ADR-0005 listed re-evaluation triggers. Several have been met:
- Published 5+ pieces of content across blog, pages, LinkedIn
- Adding a new surface (website pages) that required different handling
- Manual steps became painful (reformatting frontmatter per surface, ad-hoc page workflows)

---

## Decision

### 1. Publisher-pr owns content creation; semops-sites owns surface delivery

| Concern | Owner | Examples |
|---------|-------|---------|
| Content creation & writing | semops-publisher | Drafting, style guides, edit capture, HITL editing |
| Content structure & metadata | semops-publisher | content_type, style_guide, audience_tier, hub/spoke |
| Surface-specific frontmatter | semops-sites | BlogFrontmatter (excerpt, category), PageFrontmatter (description) |
| MDX/JSX transforms | semops-sites | Mermaid → `<MermaidDiagram>`, field renames |
| Routing & navigation | semops-sites | URL structure, nav components, app assignment |
| Visual styling | semops-sites | Fonts, layout, design system |

### 2. Content manifest is the contract

Publisher-pr embeds YAML frontmatter in Markdown files following the [Content Manifest Specification](../CONTENT_MANIFEST.md) (ADR-0014). This frontmatter is semops-publisher's contract — it describes what the content is, not where or how it gets displayed.

Sites-pr's ingestion script  reads the manifest, strips semops-publisher fields, generates surface-specific frontmatter, applies transforms (Mermaid → JSX, relative links → site routes), and places the output in the correct app directory.

### 3. WordPress is no longer a target surface

WordPress was listed as a primary surface in ADR-0005 but has not been used. All blog publishing targets semops-sites (Next.js/MDX). WordPress-related outputs (`wordpress.md`, `rankmathseo.yaml`) and WordPress API integration plans are archived.

### 4. Resume is a separate bounded context

The resume composition system (ADR-0012) has grown beyond a "content type" into its own domain with schema, corpus, SQL generation, and component rendering. It should be extracted to its own repo (`resume-pr` or similar) as a standalone bounded context. See @publishing-pipeline P-5 .

### 5. Five content types with defined conventions

| Type | Directory | Delivery | Style Guide |
|------|-----------|----------|-------------|
| `page` | `content/pages/<hub-slug>/` | semops-sites ingestion → MDX | marketing-narrative |
| `blog` | `posts/<slug>/final.md` | semops-sites ingestion → MDX | blog |
| `whitepaper` | `content/whitepapers/<slug>/` | Pandoc → PDF | whitepaper |
| `github-readme` | `content/github/<repo>.md` | Manual copy | marketing-narrative |
| `linkedin` | `content/linkedin/<slug>.md` | Manual post | blog |

---

## Consequences

**Positive:**
- Clean ownership boundary — each repo can evolve independently
- New content types don't require changes in semops-sites's ingestion logic (just new frontmatter mappings)
- No more coupled imports (`generate_mdx.py` importing semops-sites types)
- Publisher-pr stays focused on writing quality; semops-sites stays focused on presentation
- Content manifest is portable — could target other delivery layers in the future

**Negative:**
- Two-step publishing (write in semops-publisher, ingest in semops-sites) vs. single-script publish
- semops-sites ingestion script needs to understand each content type's frontmatter mapping
- More documentation to maintain (manifest spec, ingestion contracts)

**Risks:**
- Manifest fields could drift from what semops-sites expects
- Hub/spoke relative links need reliable conversion to site URLs

**Mitigations:**
- Manifest spec (ADR-0014) is the single source of truth for field names
- defines the ingestion contract and field mapping rules
- Integration test: semops-sites ingestion script validates manifest fields on ingest

---

## Implementation

Tracked in **@publishing-pipeline** project (#23):

| Issue | Scope | Status |
|-------|-------|--------|
| (P-1) | Content manifest spec, directory conventions | Complete |
| (P-2) | This ADR, supersede ADR-0005, close #66 | Complete |
| (P-3) | Website page content workflow | Todo |
| (S-1) | Page/blog ingestion script + contracts | Todo |
| (P-4) | Blog workflow refactor (remove WordPress) | Todo |
| (P-5) | Extract resume to own repo | Todo |
| -84 (P-6-8) | GitHub README, whitepaper, LinkedIn types | Todo |
| (P-9) | Docs cleanup | Todo |
| (S-2) | Sites-pr content type documentation | Todo |

---

## What This Supersedes

**ADR-0005** (Publishing Architecture, Dec 2025) decided to defer pipeline complexity and stick with manual-first publishing. That decision was correct — it prevented premature abstraction and let real pain points drive the architecture. This ADR is the "re-evaluate" that ADR-0005 anticipated, informed by the experience of publishing across multiple content types.

**Issue #66** (Blog Publishing Pipeline spec) was closed as superseded. Its content-coupling approach (semops-publisher generating semops-sites-specific MDX) is replaced by the clean ownership split defined here.

---

## References

- [ADR-0005: Publishing Architecture](./ADR-0005-publishing-architecture.md) — Superseded predecessor
- [ADR-0014: Content Manifest Conventions](./ADR-0014-content-manifest-conventions.md) — Manifest format spec
- [Content Manifest Specification](../CONTENT_MANIFEST.md) — Normative field reference
- [Issue #66](https://github.com/semops-ai/semops-publisher/issues/66) — Superseded blog pipeline spec
- [Issue #77](https://github.com/semops-ai/semops-publisher/issues/77) — Page publishing that exposed the gap
- [](https://github.com/semops-ai/semops-sites/issues/52) — Ingestion script + content contracts
- [@publishing-pipeline project](https://github.com/users/timjmitchell/projects/23) — Tracking project

---

**End of Document**
