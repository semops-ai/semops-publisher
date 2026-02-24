# ADR-0016: Bounded Context Extraction — Resumator Application

> **Status:** Draft
> **Date:** 2026-02-11
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/89)
> **General Pattern:** [semops-dx-orchestrator ADR-0008](https://github.com/semops-ai/semops-dx-orchestrator/blob/main/docs/decisions/ADR-0008-bounded-context-extraction.md) (authoritative source for the general extraction pattern)
> **Builds On:** [semops-core ADR-0009](https://github.com/semops-ai/semops-core/blob/main/docs/decisions/ADR-0009-strategic-tactical-ddd-refactor.md) (Strategic/Tactical DDD Refactor)

---

## Executive Summary

This ADR documents the resumator-specific extraction from semops-publisher — the first application of the bounded context extraction pattern defined in [semops-dx-orchestrator ADR-0008](https://github.com/semops-ai/semops-dx-orchestrator/blob/main/docs/decisions/ADR-0008-bounded-context-extraction.md). For the general pattern (architecture vs. infrastructure lens, maturity model, integration contracts, provenance/adoption lineage), see ADR-0008. This document retains the resume-specific decisions: what moves, what stays, integration patterns, and ownership.

---

## Context

SemOps currently operates as **one bounded context** with a single ubiquitous language (UBIQUITOUS_LANGUAGE.md v8.0.0). Repos are **agent role boundaries** — they scope what an AI agent needs in context — not DDD subdomain boundaries. This is codified in STRATEGIC_DDD.md (Principle #6) and GLOBAL_ARCHITECTURE.md.

However, two signals indicate this model is incomplete:

1. **semops-backoffice already uses an Anti-Corruption Layer** because finance (beancount, transactions, vendors) is a different domain that uses SemOps infrastructure but not the SemOps domain model.

2. **STRATEGIC_DDD.md identifies a bounded context candidate**: "Agentic composition applied to domain-specific outputs (e.g., resume composition, motorsport-consulting proposals) may warrant a second bounded context. These use SemOps infrastructure but serve a different domain with its own ubiquitous language."

3. **The resume-builder in semops-publisher** has its own object model (Bullet, Variant, Job, Skill Taxonomy — see ADR-0011, ADR-0012), its own dimensional schema (16 tables), and zero code dependencies on the blog publishing agents. It is architecturally distinct but embedded in a repo whose domain is content creation.

The question is not just "should we extract the resume-builder?" but "what is the general pattern for extracting functionality that has matured beyond the core's bounded context?"

---

## Decision

### 1. Architecture vs. Infrastructure Are Independent Dimensions

An extraction decision evaluates two dimensions independently:

| Dimension | Question | Implication |
|-----------|----------|-------------|
| **Architecture** | Does it have its own domain model, aggregate root, and language? | Determines whether it's a new bounded context or just a new repo within the existing context |
| **Infrastructure** | Does it consume shared services (Supabase, Qdrant, tooling patterns)? | Determines the integration pattern, not the extraction decision |

**Architecture drives the decision.** Infrastructure is a deployment concern.

A new repo within the same bounded context (like splitting semops-publisher into two repos) would still share UBIQUITOUS_LANGUAGE.md and the Pattern/Entity/Edge model. A bounded context extraction creates a context with its own domain language that consumes core services through a defined interface.

### 2. Extraction Maturity Model

Functionality progresses through four levels of separation:

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| 0 | **Embedded** | Code lives inside a repo, no separation | Early resume scripts in semops-publisher |
| 1 | **Modular** | Distinct directory/module, shares the host repo's domain model | `docs/resumes/` directory with its own corpus |
| 2 | **Extractable** | Own domain model, own language, ready to be its own context | Resume-builder today — own object model (Bullet/Variant/Job), own schema, no code deps on host |
| 3 | **Extracted** | Own repo, own bounded context, consumes core via integration pattern | Target state for resume-builder |

**The test for Level 2** (ready to extract):

1. **Own aggregate root** — not Pattern. The domain organizes around a different central concept.
2. **Own language** — terms that don't belong in UBIQUITOUS_LANGUAGE.md (e.g., "role targeting", "bullet format", "skill taxonomy").
3. **Standalone coherence** — you could explain the domain to someone who has never heard of SemOps.
4. **No code dependencies** on the host repo's domain logic.

Reaching Level 2 is a signal, not a mandate. Some functionality is fine staying modular forever.

### 3. Integration Contract for Extracted Contexts

An extracted bounded context relates to the SemOps core through explicitly typed DDD integration patterns:

| Integration | What Flows | Direction |
|-------------|-----------|-----------|
| **Shared Kernel** | Meta-patterns (DDD, SKOS, PROV-O) and **architectural patterns** — e.g., composition-from-atoms (concept atoms → composed documents in core; bullet atoms → composed variants in resume-builder). The pattern is shared; the domain-specific atoms and edges are not. | Bidirectional — both contexts depend on the same foundation |
| **Customer-Supplier** | Core provides services (Supabase, Qdrant, knowledge graph queries), satellite consumes | Core → Satellite |
| **Anti-Corruption Layer** | Satellite translates core concepts into its own domain language where the models diverge | At the satellite boundary |
| **Published Language** | Core publishes its schema and API contracts; satellite adopts what it needs | Core → Satellite |

**What is NOT shared:**

- The satellite does NOT conform to UBIQUITOUS_LANGUAGE.md for its own domain terms
- The satellite does NOT use Pattern as its aggregate root
- The satellite does NOT need the full SemOps context to be useful

**What IS shared:**

- Infrastructure services (connection configs, not code coupling)
- Tooling conventions (uv, ruff, pytest, project structure)
- Process patterns (ADRs, session notes, GitHub workflow)
- Meta-patterns from the Pattern layer where they genuinely apply
- **Architectural patterns as shared patterns** — composition-from-atoms is a core SemOps pattern (concept atoms → composed documents via edge relationships and context). A satellite may implement the same *pattern* with its own *domain atoms*. Resume-builder composes Bullets into Variants the same way core composes concept atoms into documents — the composition pattern is shared, the atoms and edges are domain-specific. This is the Shared Kernel at the pattern level: the satellite adopts the architectural pattern, not the domain model.

### 4. Provenance and Adoption Lineage Between Contexts

An extracted bounded context has **known provenance** back to core. The relationship isn't static — it evolves, and that evolution is tracked. This applies the same adoption lineage thinking from the Pattern layer (`adopts`, `extends`, `modifies`) to the bounded context level.

**Origin lineage:** The satellite knows what core patterns, services, and architectural decisions it derives from. Resumator derives from the composition-from-atoms pattern, consumes Supabase infrastructure, and adopted the dimensional modeling approach from the Pattern layer's SKOS taxonomy design.

**Adoption tracking:** When core updates a shared component (pattern, service, schema, tooling), the satellite can:

| Response | Meaning | Example |
| -------- | ------- | ------- |
| **Adopt** | Update to match core | Core improves the composition pattern → resumator adopts the improvement |
| **Extend** | Adopt with domain-specific adaptations (tracked deviation) | Core adds provenance tracking to composition → resumator extends with bullet-specific lineage |
| **Decline** | Consciously choose not to adopt, with rationale | Core changes SKOS taxonomy structure → resumator declines because its skill taxonomy serves a different purpose |
| **Defer** | Acknowledge the change, plan to evaluate later | Core upgrades Supabase → resumator defers until next maintenance window |

**Decision provenance:** Each adoption decision is an episode — what changed in core, what the satellite decided, and why. This is tracked through the same mechanisms the system already uses: session notes for the decision, ADRs for significant choices, commit messages for the implementation.

The satellite is **autonomous but aligned** — it can evolve its own domain independently while maintaining known, tracked provenance back to core. The relationship is visible: we always know what core components a satellite depends on, whether those components have changed, and whether the satellite has adopted or diverged.

**Update propagation mechanics:**

- **Schema changes** in core → satellite consumes via API/views, not direct table access
- **Architectural pattern changes** → satellite evaluates and records adopt/extend/decline
- **Tooling updates** (uv, ruff versions) → satellite adopts independently via its own pyproject.toml
- **Process updates** (ADR template, session notes format) → satellite adopts via semops-dx-orchestrator Published Language
- **Infrastructure updates** (Supabase version, Qdrant config) → satellite updates connection config

---

## First Application: Resume-Builder

### Architecture Assessment

| Criterion | Assessment |
|-----------|------------|
| Own aggregate root | **Yes** — Bullet is the composable unit; Variant is the composed output. Not Pattern. |
| Own language | **Yes** — role targeting, skill taxonomy, dimensional model, bullet formats (CAR/STAR/PAR/XYZ/APR), metric types. None of these belong in UBIQUITOUS_LANGUAGE.md. |
| Standalone coherence | **Yes** — "AI-assisted resume composition from a structured bullet corpus" is self-contained. |
| No code deps on host | **Yes** — Zero imports from semops-publisher's blog agents (research.py, outline.py, draft.py, formatter.py). |
| Maturity level | **Level 2 → 3** — Ready to extract. |

### What Moves

| Component | Current Location | Destination |
|-----------|-----------------|-------------|
| Corpus (source of truth) | `docs/resumes/corpus/` | resumator repo root |
| Variants (composed output) | `docs/resumes/variants/` | resumator repo |
| Frameworks | `docs/resumes/frameworks/` | resumator repo |
| Archive | `docs/resumes/archive/` | resumator repo |
| Database schema | `supabase/migrations/002_resume_schema.sql` | resumator repo |
| ETL script | `scripts/corpus_to_sql.py` | resumator repo |
| ADRs 0011, 0012 | `docs/decisions/` | Copied to resume-builder with cross-references; originals marked Superseded with pointer |
| Session notes (55, 56, 59, 63, 64, 69) | `docs/session-notes/` | Referenced from resume-builder, not moved (they document semops-publisher history) |

### What Stays in semops-publisher

- Blog publishing agents and workflow
- Style guides (resume-builder may eventually have its own)
- Content manifest spec (ADR-0014) — resume-builder can adopt this as Published Language if it publishes content
- Edit capture system
- All non-resume content

### Ownership After Extraction

The extraction forces clarity about who owns what. Three categories apply:

| Category | Principle | What Moves to resumator |
| -------- | --------- | ---------------------- |
| **Domain artifacts** | The satellite owns its domain model | Corpus, schema (002_resume_schema.sql), ETL script, ADRs |
| **Infrastructure** | Stays shared, consumed via config | Supabase instance stays in semops-core |
| **Consumer contracts** | Published Language to downstream | Views (`v_resume_job`, `v_duration_by_role`, `v_company_tenure`) and seed.sql format |

**Key decision: the schema IS the domain model, not infrastructure.** The dimensional model (jobs, bullets, skills, bridges) defines what a Job is, what a Bullet is, how Skills relate to Jobs — that's resumator's domain. The fact that it runs in Supabase (shared infrastructure) is a deployment concern. Sites-pr currently owns `002_resume_schema.sql` in its migrations because that's where the data is consumed, but this conflates architecture (domain model) with infrastructure (where it runs). After extraction, resumator owns the schema; semops-sites consumes via views.

### Integration Pattern

```
resumator (new bounded context)
│
├── Customer-Supplier ← semops-core
│ Consumes: Supabase instance (infrastructure)
│ Owns: resume schema within that instance (domain model)
│ Does NOT consume: Pattern/Entity/Edge domain model
│
├── Anti-Corruption Layer → semops-core
│ Translates: If resumator ever queries the knowledge base,
│ it maps results into its own domain (Bullet, Skill, Job)
│
├── Published Language ← semops-publisher
│ Adopts: Content manifest frontmatter spec (if publishing resume content)
│ Adopts: PDF export tooling patterns (Pandoc)
│
├── Published Language → semops-sites
│ Publishes: SQL views as the consumer contract
│ Provides: seed.sql for Career DataViz UI
│ semops-sites consumes views, does NOT own resume schema
│
└── Current handoff (to be improved):
 corpus_to_sql.py → seed.sql → manual merge into semops-sites
 Known gap: real-time-comms product domain missing from output
```

### Repo Naming and Lifecycle

**Decision:** `resumator` under `timjmitchell` — this is a personal operational tool now.

The planned lifecycle itself demonstrates how bounded contexts work:

1. **Personal tool** (now) — `timjmitchell/resumator-pr`. Operationally serves timjmitchell.com. Own domain, own schema, consumes SemOps infrastructure.
2. **Reference application** (future) — Open-sourced as a demonstration of SemOps composition patterns. Shows how the composition-from-atoms pattern works in a concrete, relatable domain (everyone understands resumes). May move to `semops-ai/resumator` or remain under `timjmitchell` with SemOps documentation pointing to it.

This arc — embedded tool → extracted bounded context → open-source reference application — is the same trajectory any SemOps satellite context could follow. The extraction formalizes the boundaries; the open-sourcing demonstrates them. A future motorsport-consulting or proposal-builder would follow the same path.

---

## Consequences

**Positive:**
- Formalizes a pattern that's already emerging (semops-backoffice ACL, STRATEGIC_DDD.md candidate)
- Resume-builder gets its own focused agent context — an AI agent working on resumes doesn't need blog style guides
- Clean separation makes it possible to share the resume system independently
- General pattern is reusable for future extractions (proposals, consulting, voice agent)

**Negative:**
- Cross-repo coordination overhead for the seed.sql pipeline to semops-sites
- ADR and session note references become cross-repo links (manageable, already done for other repos)
- One more repo to maintain

**Risks:**
- Over-extraction: not everything that *could* be separated *should* be. The maturity model (Level 0-3) and the four-criterion test mitigate this.
- Under-specifying the integration contract leads to invisible coupling. The typed integration patterns mitigate this.

---

## Implementation Plan

### Phase 1: Document and Decide
- [x] Define general extraction pattern (this ADR)
- [ ] Decide repo name and org placement
- [ ] Update STRATEGIC_DDD.md to reference this pattern
- [ ] Update GLOBAL_ARCHITECTURE.md repo map

### Phase 2: Extract
- [ ] Create new repo with standard structure (CLAUDE.md, pyproject.toml, docs/)
- [ ] Move corpus, variants, frameworks, archive
- [ ] Move schema and ETL script
- [ ] Copy ADRs 0011, 0012 with cross-references
- [ ] Set up Supabase connection to semops-core instance

### Phase 3: Clean Up
- [ ] Remove extracted content from semops-publisher
- [ ] Add cross-references where content was removed
- [ ] Mark ADRs 0011, 0012 as Superseded in semops-publisher
- [ ] Update semops-publisher CLAUDE.md and ARCHITECTURE.md
- [ ] Update semops-dx-orchestrator ADR_INDEX.md

---

## Session Log

### 2026-02-11: Pattern Definition
**Status:** In Progress
**Tracking Issue:** [](https://github.com/semops-ai/semops-publisher/issues/89)

**Completed:**
- Reviewed GLOBAL_ARCHITECTURE.md, STRATEGIC_DDD.md, UBIQUITOUS_LANGUAGE.md v8.0.0
- Confirmed SemOps operates as one bounded context with repos as agent role boundaries
- Identified resume-builder as Level 2 (Extractable) on the maturity model
- Defined general extraction pattern: architecture vs. infrastructure lens, maturity model, integration contracts
- Drafted this ADR

**Next Session Should Start With:**
1. Decide repo name and org placement
2. Validate integration patterns with semops-sites seed.sql pipeline
3. Begin Phase 2 extraction

---

## References

- [GLOBAL_ARCHITECTURE.md](https://github.com/semops-ai/semops-dx-orchestrator/blob/main/docs/GLOBAL_ARCHITECTURE.md) — System architecture, DDD alignment
- [STRATEGIC_DDD.md](https://github.com/semops-ai/semops-core/blob/main/docs/STRATEGIC_DDD.md) — Strategic DDD layer, bounded context candidate
- [UBIQUITOUS_LANGUAGE.md](https://github.com/semops-ai/semops-core/blob/main/schemas/UBIQUITOUS_LANGUAGE.md) — Shared domain vocabulary (v8.0.0)
- [ADR-0011: Resume Schema Design](./ADR-0011-resume-schema-design.md) — Dimensional model for resume data
- [ADR-0012: Resume Composition Object Model](./ADR-0012-resume-composition-model.md) — Bullet/Variant/Job object model
- [](https://github.com/semops-ai/semops-dx-orchestrator/issues/102) — Parent issue for resume extraction

---

**End of Document**
