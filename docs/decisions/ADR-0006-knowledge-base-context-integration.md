# ADR-0006: Knowledge Base Context + Concept Validation

> **Status:** Draft
> **Date:** 2025-12-06
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/22) - Phase 1.5: Knowledge base context + concept validation
> **Builds On:** [PHASE1-MANUAL-FIRST.md](./PHASE1-MANUAL-FIRST.md)

---

## Executive Summary

Introduce a "Phase 1.5" enhancement that connects ike-publisher agents to the semops-core knowledge base for read-only concept context. Key feature: validate `{{concept-name}}` tags against the 1p concept table to bifurcate handling of 1p vs 3p references, enabling different backlink, attribution, and citation paths.

---

## Context

### Current Phase 1 Limitations

1. **No knowledge base connection**: Agents have no access to existing concepts, definitions, or relationships
2. **Blind concept tagging**: `{{concept-name}}` tags are arbitrary strings with no validation
3. **No 1p/3p distinction at tagging time**: All concepts treated equally until manual review
4. **Missing context**: Research agent can't leverage existing 1p knowledge for consistency

### The Schema Evolution

The new semops-core schema (phase2-schema.sql) establishes:
- **Concept as aggregate root** with provenance field (`1p`, `2p`, `3p`)
- **1p concepts** represent "operates in my system" - core IP, methodology, owned ideas
- **3p concepts** represent external references requiring citation

This creates a clear data source for validating concept tags.

### The Opportunity

With 1p concepts structured in PostgreSQL, we can:
1. Validate concept slugs against the authoritative list
2. Provide agents with concept definitions for consistent usage
3. Bifurcate output handling based on provenance
4. Suggest relevant 1p concepts the author may have missed

---

## Decision

### 1. Connect Publisher to Knowledge Base (Read-Only)

Add Supabase client to ike-publisher for querying the concept table:

```python
# utils/knowledge_client.py
class KnowledgeClient:
 def get_1p_concepts(self) -> list[Concept]:
 """Fetch all 1p concepts with definitions"""
 return self.client.table('concept') \
 .select('id, preferred_label, definition, broader, narrower, related') \
 .eq('provenance', '1p') \
 .execute

 def validate_concept(self, slug: str) -> ConceptMatch | None:
 """Check if slug exists as 1p concept"""
 result = self.client.table('concept') \
 .select('*') \
 .eq('id', slug) \
 .single \
 .execute
 return result.data if result.data else None
```

### 2. Concept Validation in Agents

Research and Draft agents validate `{{concept-name}}` tags:

```
Input: {{semantic-coherence}}
 │
 ▼
 Query concept table
 WHERE id = 'semantic-coherence'
 │
 ┌──────┴──────┐
 │ │
 ▼ ▼
FOUND NOT FOUND
provenance=1p (unknown concept)
 │ │
 ▼ ▼
✓ Valid 1p Check if 3p reference
 concept or typo/new concept
```

### 3. Bifurcated Output Handling

Based on concept provenance:

| Aspect | 1p Concept | 3p Concept |
|--------|-----------|-----------|
| **Backlink** | Internal link to concept page | External citation link |
| **Attribution** | Auto-attributed (owned IP) | Requires explicit citation |
| **Frontmatter** | `concepts: [slug]` | `citations: [{source, url}]` |
| **Edge Creation** | `entity -> concept` edge | `entity -> external_ref` edge |
| **Validation** | Must exist in concept table | Flagged for review |

### 4. Agent Context Enhancement

Research agent receives 1p concept catalog as context:

```markdown
## Available 1P Concepts

The following concepts are part of your knowledge system.
Use these exact slugs when referencing owned ideas:

- **semantic-coherence**: A state of stable, shared semantic alignment...
- **semantic-operations**: The methodology for maintaining coherence...
- **aggregate-root**: The DDD pattern where concept is the root...

When referencing external ideas (3p), use citation format instead.
```

### 5. Concept Suggestion

Draft agent can suggest 1p concepts based on content:

```python
def suggest_concepts(self, content: str, available_concepts: list[Concept]) -> list[str]:
 """Use embeddings or keyword matching to suggest relevant 1p concepts"""
 # Phase 1.5: Simple keyword matching against preferred_label and definition
 # Phase 2: Vector similarity search
```

---

## Consequences

**Positive:**
- Concept tags are validated against authoritative source
- Clear 1p/3p bifurcation enables correct attribution paths
- Agents have consistent definitions to work from
- Reduces manual review burden (typos caught automatically)
- Enables automatic internal linking for 1p concepts
- Concept suggestions help authors use established vocabulary

**Negative:**
- Adds database dependency to publisher (was file-only in Phase 1)
- Requires concept table to be populated before use
- New failure mode if Supabase is unavailable

**Risks:**
- Concept table may be incomplete initially (mitigation: graceful handling of unknown concepts)
- Over-reliance on validation might limit introducing new concepts (mitigation: clear "new concept" workflow)

---

## Implementation Plan

### Prerequisites: Validate Orchestrator Readiness

Before implementing, semops-core must complete its content overhaul:

#### Blocking Dependencies (semops-core)
- [ ] `feature/concept-aggregate-root` branch merged to main
- [ ] Phase 2 schema deployed to Supabase
- [ ] 1p concepts ingested into concept table (via `ingest_concepts.py`)
- [ ] Concepts have `definition` field populated
- [ ] At least core concepts approved (`approval_status = 'approved'`)

#### Validation Checklist
```bash
# Run from semops-core to verify readiness:

# 1. Check branch status
git branch --show-current # Should be 'main' after merge

# 2. Query concept count
psql $DATABASE_URL -c "SELECT provenance, COUNT(*) FROM concept GROUP BY provenance;"
# Expected: meaningful count of 1p concepts

# 3. Check definition coverage
psql $DATABASE_URL -c "SELECT COUNT(*) FROM concept WHERE definition IS NULL OR definition = '';"
# Expected: 0 (all concepts have definitions)

# 4. Check approved concepts
psql $DATABASE_URL -c "SELECT COUNT(*) FROM concept WHERE approval_status = 'approved' AND provenance = '1p';"
# Expected: > 0 (some approved 1p concepts ready for use)
```

---

### Phase 1.5a: Basic Connection
**Depends on:** Prerequisites complete

- [ ] Add `supabase` to requirements.txt
- [ ] Create `utils/knowledge_client.py` with concept queries
- [ ] Add connection config to `.env` (use same Supabase as semops-core)
- [ ] Test connection with existing concept data
- [ ] Handle connection failures gracefully (fallback to manual mode)

### Phase 1.5b: Concept Validation
**Depends on:** Phase 1.5a

- [ ] Add validation to research agent output processing
- [ ] Flag unknown concepts in research.md output
- [ ] Add validation to draft agent
- [ ] Generate validation report in frontmatter
- [ ] Add canonical source URI to concept lookups

### Phase 1.5c: Context Injection
**Depends on:** Phase 1.5b

- [ ] Fetch 1p concepts at research phase start
- [ ] Include concept catalog in agent system prompts
- [ ] Add concept definitions to research context
- [ ] Include source_uri for canonical doc linking

### Phase 1.5d: Bifurcated Output
**Depends on:** Phase 1.5c

- [ ] Update formatter agent to separate 1p/3p in frontmatter
- [ ] Generate internal links for 1p concepts (to canonical source)
- [ ] Generate citation format for 3p concepts
- [ ] Auto-attribution for 1p references
- [ ] Update linkedin.md handling for citations

### Phase 2 (Future)
- [ ] Vector similarity for concept suggestions (uses concept.embedding)
- [ ] Automatic edge creation on publish
- [ ] Two-way sync with knowledge base
- [ ] Concept proposal workflow (publisher → semops-core)

---

## Technical Details

### Database Schema (from semops-core)

```sql
CREATE TABLE concept (
 id TEXT PRIMARY KEY, -- kebab-case slug: 'semantic-coherence'
 provenance TEXT NOT NULL, -- '1p' | '2p' | '3p'
 approval_status TEXT, -- 'pending' | 'approved' | 'rejected'
 preferred_label TEXT, -- Display name
 definition TEXT, -- Full definition
 broader TEXT[], -- Parent concepts (SKOS)
 narrower TEXT[], -- Child concepts (SKOS)
 related TEXT[], -- Related concepts (SKOS)
 created_at TIMESTAMPTZ,
 updated_at TIMESTAMPTZ
);
```

### Validation Output Format

```yaml
# In frontmatter.yaml
concepts:
 validated:
 - id: semantic-coherence
 provenance: 1p
 label: Semantic Coherence
 - id: aggregate-root
 provenance: 1p
 label: Aggregate Root
 unvalidated:
 - id: new-concept-idea
 suggested_action: "Add to concept table or convert to 3p citation"

citations:
 - source: "Eric Evans"
 concept: "bounded-context"
 provenance: 3p
 url: "https://..."
```

### Agent Prompt Addition

```markdown
## Concept Validation Rules

When tagging concepts:

1. **Use exact slugs** for 1p concepts (provided in context)
2. **Mark as citation** if referencing external/3p ideas
3. **Flag for review** if uncertain whether concept exists

Available 1P concepts: {{concept_catalog}}
```

---

## Open Questions

1. **How to handle new 1p concepts?** Should the publisher be able to propose new concepts, or must they be added to semops-core first?
 - *Proposed*: Publisher flags as "proposed 1p" → manual review → add to concept table

2. **Caching strategy?** Should concept catalog be cached locally or fetched each run?
 - *Proposed*: Fetch at session start, cache for duration

3. **Partial matches?** What if author writes `{{semantic coherence}}` (space) vs `{{semantic-coherence}}` (slug)?
 - *Proposed*: Fuzzy match + suggest correction

---

## References

- [SYSTEM_CONTEXT.md] - 1p/3p provenance definitions
- [phase2-schema.sql] - Concept table schema
- [UBIQUITOUS_LANGUAGE.md] - Domain definitions
- [PHASE1-MANUAL-FIRST.md](./PHASE1-MANUAL-FIRST.md) - Current phase constraints

---

**End of Document**
