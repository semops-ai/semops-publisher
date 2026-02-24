# ADR-0002: Experiment Framework for Content Generation

> **Status:** In Progress
> **Date:** 2025-12-03
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/12) - Start Build-out of Publishing pipeline
> **Builds On:** [semops-core experiment framework](https://github.com/semops-ai/semops-core/tree/main/experiments)

---

## Executive Summary

Established a Docker-based experiment framework for testing content generation workflows. The framework uses a Zettelkasten-inspired input format with concept declaration via backticks, enabling semantic linking to Project Ike's knowledge base during outline generation.

---

## Context

We needed a way to:
1. Quickly iterate on content generation prompts and RAG configurations
2. Test Project Ike integration for concept lookup and context retrieval
3. Isolate experiments in reproducible Docker environments
4. Track experiment results with clear inputs and outputs

The semops-core repo already had a working experiment framework pattern we could adapt.

---

## Decision

Implemented the experiment framework with:

1. **Single structured input file** (`input.md`) following Zettelkasten principles
2. **Concept declaration via backticks** - terms marked with `` `backticks` `` are looked up in Project Ike
3. **Docker isolation** with volume mounts for inputs and results
4. **Slash commands** (`/experiment`, `/experiment-cleanup`) for workflow automation
5. **Incremental stubbing** - features are scaffolded with placeholder implementations

---

## Feature Status

| Feature | Status | Notes |
|---------|--------|-------|
| Input parsing (`input.md`) | ✅ Implemented | Sections: Core Narrative, Key Points, Connections, References, Hints |
| Project Ike lookup (`` `backticks` ``) | ✅ Implemented | Queries `concept` table by ID and name |
| Repo file loading (`./path`) | ✅ Implemented | Volume mount at `/repo` |
| RAG keyword search | ✅ Implemented | Keyword extraction + concept matching |
| Outline generation (Claude) | ✅ Implemented | Preserves backtick notation in output |
| External URL fetch (`https://...`) | ⏸️ Stubbed | Logged but not fetched |
| External search (Search Hints) | ⏸️ Stubbed | Logged but not executed |
| Full content generation | ⏸️ Stubbed | Only outline phase implemented |

---

## Input Model

The `input.md` template follows Zettelkasten methodology with DDD alignment:

```markdown
## Core Narrative
Your POV with `concept-references` inline.

## Key Points
- Point linked to `supporting-concept`

## Connections to Explore
- How does `concept-a` relate to `concept-b`?

## Known References
- `concept-slug` (Project Ike lookup)
- ./path/to/doc.md (repo file)
- https://example.com (stubbed)

## Search Hints
- "external search query" (stubbed)
```

See: [content-input-pattern.md](https://github.com/semops-ai/semops-core/blob/main/docs/domain-patterns/content-input-pattern.md)

---

## Output Model

Two output files per experiment:

1. **`results/results.json`** - Machine-readable metrics
2. **`results/outline.md`** - Human-reviewable outline with:
 - Thesis (preserving `concept` references)
 - Sections with evidence sources
 - Flags for human attention

---

## Template Readiness

| Component | Location | Status |
|-----------|----------|--------|
| Dockerfile | `experiments/template/Dockerfile` | ✅ Ready |
| docker-compose.yml | `experiments/template/docker-compose.yml` | ✅ Ready |
| benchmark.py | `experiments/template/benchmark.py` | ✅ Ready (~700 lines) |
| input.md template | `experiments/template/input.md` | ✅ Ready |
| .env.example | `experiments/template/.env.example` | ✅ Ready |
| PLAN.md template | `experiments/template/PLAN.md` | ✅ Ready |
| /experiment command | `.claude/commands/experiment.md` | ✅ Ready |
| /experiment-cleanup | `.claude/commands/experiment-cleanup.md` | ✅ Ready |

---

## Consequences

**Positive:**
- Fast iteration on prompts without modifying main codebase
- Reproducible experiments via Docker
- Clear separation of input (author intent) from output (generated outline)
- Concept linking enables knowledge graph integration

**Negative:**
- Requires Docker environment
- Supabase connection needed for full functionality
- Stubbed features need implementation for complete pipeline

**Risks:**
- RAG retrieval quality depends on Project Ike concept coverage
- Outline quality needs HITL validation before drafting phase

---

## Implementation Plan

### Phase 1: Foundation (Complete)
- [x] Directory structure and templates
- [x] Docker configuration
- [x] Input parsing with concept extraction
- [x] Project Ike integration (Supabase)
- [x] Outline generation with Claude
- [x] Slash commands

### Phase 2: Enhancement (Future)
- [ ] External URL fetching (WebFetch)
- [ ] External search integration
- [ ] Full content generation (Claude + Gemini)
- [ ] Quality evaluation metrics

---

## Session Log

### 2025-12-03: Initial Framework Implementation
**Status:** Completed
**Tracking Issue:** N/A

**Completed:**
- Created full experiment framework adapted from semops-core
- Implemented Zettelkasten-inspired input format with backtick concept declaration
- Built benchmark.py with 7-step pipeline (parse → connect → refs → concepts → RAG → hints → outline)
- Created content-input-pattern.md in semops-core documenting the pattern
- Resolved git merge conflicts after rebase
- Switched remote to SSH for authentication

**Next Session Should Start With:**
1. Test framework with `/experiment test-basic`
2. Review outline quality with real input
3. Consider implementing stubbed features based on need

---

## References

- [experiments/README.md](../../experiments/README.md) - Framework documentation
- [experiments/template/](../../experiments/template/) - Template files
- [content-input-pattern.md](https://github.com/semops-ai/semops-core/blob/main/docs/domain-patterns/content-input-pattern.md) - Input pattern documentation
- [semops-core experiments](https://github.com/semops-ai/semops-core/tree/main/experiments) - Source framework

---

**End of Document**
