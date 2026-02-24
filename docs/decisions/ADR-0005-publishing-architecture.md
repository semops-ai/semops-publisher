# ADR-0005: Publishing Architecture

> **Status:** Superseded by [ADR-0015](./ADR-0015-publishing-pipeline-architecture.md)
> **Date:** 2025-12-05
> **Related Issues:**
> - [semops-core #49 - Multi-Surface Publishing Architecture](https://github.com/semops-ai/semops-core/issues/49)
> - 
> **Builds On:** [PHASE1-MANUAL-FIRST](./PHASE1-MANUAL-FIRST.md)

---

## Executive Summary

Evaluating architectural options for the publishing pipeline. Two GitHub issues proposed elaborate multi-surface architectures with central hubs, surface registries, and transformation pipelines. This ADR captures the decision to defer most of that complexity and stick with the manual-first approach until real pain points emerge.

---

## Context

Two issues were created with ambitious publishing architectures:

**Issue #49 (semops-core)** proposed:
- semops-core as central hub for all content operations
- Surface registry (ingest → transform → publish)
- Entity catalog with approval workflows
- Delivery tracking with lineage edges
- Multi-phase implementation across 4+ phases

**Issue #12 (ike-publisher)** proposed:
- Two competing designs (tools-focused vs. metadata-focused)
- Transformation pipeline with ComfyUI, Pillow, SEO tools
- WordPress/LinkedIn API integrations
- Surface adapters for each platform

**Problem:** These plans were created before validating the workflow through actual publishing. They represent "big design up front" that contradicts the Phase 1 philosophy.

---

## Decision

**Defer the elaborate architecture. Stick with manual-first.**

### What We're NOT Doing (Yet)

| Proposed Feature | Status | Rationale |
|------------------|--------|-----------|
| Central hub (semops-core) | ❌ Deferred | Adds coordination overhead before we know what's needed |
| Surface registry (DB/YAML) | ❌ Deferred | Only have 2-3 surfaces; hardcode is fine |
| Entity catalog for content | ❌ Deferred | File-based state is simpler to debug |
| Transformation pipeline | ❌ Deferred | Manual image creation works for now |
| WordPress/LinkedIn APIs | ❌ Deferred | Copy-paste is fast enough for 3-5 posts |
| Delivery tracking edges | ❌ Deferred | Mental tracking sufficient at current volume |

### What We ARE Doing

| Feature | Status | Implementation |
|---------|--------|----------------|
| Content creation | ✅ Active | Experiment framework with `input.md` |
| Outline generation | ✅ Active | Claude via benchmark.py |
| Draft editing | ✅ Active | HITL in editor |
| Publishing | ✅ Active | Manual copy-paste |
| Tracking | ✅ Active | Git history + frontmatter |

### Publishing Surfaces (Current)

| Surface | Method | Notes |
|---------|--------|-------|
| WordPress (blog) | Copy-paste | Use Gutenberg editor |
| LinkedIn | Copy-paste | Reformat for platform |
| semops-sites (timjmitchell.com) | Git push | MDX to `src/content/blog/` |

---

## Consequences

**Positive:**
- No premature abstraction
- Learn what actually hurts through real publishing
- Keep focus on content quality, not infrastructure
- Avoid coordination overhead between repos

**Negative:**
- No automated multi-surface syndication
- Manual reformatting per platform
- No lineage tracking (yet)

**Risks:**
- May need to retrofit tracking later
- Manual steps might scale poorly

**Mitigations:**
- Document pain points as they emerge
- Keep issues #49 and #12 as reference for future automation
- Re-evaluate after 5+ published posts

---

## Trigger for Revisiting

Re-open this decision when ANY of:
- [ ] Published 5+ posts and manual steps are painful
- [ ] Need to track what's published where (losing track)
- [ ] Need to automate image generation at scale
- [ ] Adding a new surface that requires API integration
- [ ] Content volume exceeds what one person can manually manage

---

## What to Keep from the Issues

Some ideas worth preserving for future reference:

### From Issue #49
- Surface concept (ingest/transform/publish directions)
- `derived_from` and `version_of` edge predicates for lineage
- Delivery status tracking (`planned` → `queued` → `published`)

### From Issue #12
- Tool list: ComfyUI, Pillow, SEO optimizer
- Surface adapter pattern for platform APIs
- YAML-based surface configuration

These can be pulled in incrementally when needed.

---

## Session Log

### 2025-12-05: Initial Assessment
**Status:** In Discussion

**Completed:**
- Reviewed issues #49 and #12 against current ADRs
- Identified gap between elaborate plans and Phase 1 philosophy
- Decided to defer complexity, stick with manual-first
- Created this ADR to document the decision

**Key Insight:**
The issues represent "bloated plans" created before learning what the workflow actually needs. Better to publish manually and let pain points drive automation.

---

## References

- [PHASE1-MANUAL-FIRST](./PHASE1-MANUAL-FIRST.md) - Core philosophy
- [semops-core #49](https://github.com/semops-ai/semops-core/issues/49) - Original architecture proposal
- - Pipeline build-out proposal
- [ADR-0002-RESUMATOR-STACK](./ADR-0002-RESUMATOR-STACK.md) - Decided stack for timjmitchell.com

---

**End of Document**
