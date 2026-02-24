# ADR-0003: Narrative Style System

> **Status:** Complete (Phase 1)
> **Date:** 2025-12-06
> **Related Issue:** 

## Executive Summary

Design a style enforcement system that validates AI-generated content against two target styles (GitHub Documentation vs Blog/Informal) while ensuring consistent use of 1P concept terminology from the semops-core knowledge base.

## Context

### The Problem

ike-publisher generates content through AI agents (Research → Outline → Draft → Format). Currently, style control relies on:
1. Reference posts passed to Draft Agent (token-limited, underutilized)
2. Natural language instructions in agent prompts
3. Manual human editing (draft.md → final.md)

There's no validation layer, no explicit style guidelines, and no mechanism to enforce terminology consistency with the concept inventory.

### Why This Matters

1. **Brand Voice Consistency** - Posts should have recognizable style regardless of topic
2. **Concept Integrity** - 1P concepts (semantic-operations, source-problem, etc.) should appear with correct context
3. **Platform Optimization** - GitHub docs need hedging verbs; blog needs engagement verbs
4. **Quality Gates** - Catch style drift before manual editing phase

### Key Metrics from Issue #20

**Passive Voice Index (PVI)**
$$PVI = \left( \frac{\text{Passive Sentences}}{\text{Total Sentences}} \right) \times 100$$

| Style | Target PVI |
|-------|-----------|
| GitHub Docs | 0% |
| Blog | ≤5% |

**Concept Adherence Rate (CAR)**
$$CAR = \frac{\text{Sentences with (Concept ∈ C AND Context ∈ H or E)}}{\text{Total Sentences}}$$

| Style | Target CAR | Context Set |
|-------|-----------|-------------|
| GitHub Docs | ≥2% | Hedging verbs (suggests, implies, is consistent with) |
| Blog | ≥4% | Engagement verbs (we're thinking, check out, this cool thing) |

---

## Research Questions

### 1. Style Detection & Enforcement

**Q1.1: What NLP tools best detect passive voice in Python?**
- spaCy with dependency parsing
- NLTK with POS tagging
- textstat for readability metrics
- Custom regex patterns

**Q1.2: How do we detect concept context (hedging vs engagement)?**
- Window-based search (3-5 words around concept)
- Dependency parse to find governing verbs
- Pre-defined verb sets per style

**Q1.3: Where does validation fit in the workflow?**
Options:
- A) Pre-draft (inform agent with guidelines)
- B) Post-draft (validate before editing) ← Recommended
- C) Post-format (final QA check)
- D) Integrated in agent prompts (no validation, just guidance)

### 2. Concept Integration with semops-core

**Q2.1: How do we sync concept inventory?**
- Direct PostgreSQL query to orchestrator
- Export to JSON/YAML file in ike-publisher
- CLI command to refresh local cache

**Q2.2: Which concept fields matter for style checking?**
```
concept.preferred_label → Exact term to match
concept.alt_labels → Acceptable variants
concept.ownership → 1p/2p/3p determines enforcement priority
concept.maturity → canonical > established > emerging
```

**Q2.3: How strict should matching be?**
- Exact match only
- Fuzzy matching with threshold
- Embedding similarity (detect semantic drift)

### 3. Style Guide Definition

**Q3.1: Where do style rules live?**
Options:
- A) `STYLE_GUIDE.md` in repo root (human-readable)
- B) `config/styles/` with YAML per style (machine-readable)
- C) Database table in orchestrator (cross-repo consistency)

**Q3.2: How do we handle style inheritance?**
- Base rules (apply to all)
- Style-specific overrides
- Post-specific exceptions

**Q3.3: What rules are enforceable programmatically?**

| Rule | Enforceable | Method |
|------|-------------|--------|
| Active voice | Yes | POS/dependency parsing |
| Contractions (avoid/require) | Yes | Regex |
| Third-person (GitHub) | Yes | Pronoun detection |
| Serial comma | Yes | Regex |
| Paragraph length | Yes | Sentence count |
| Concept usage | Yes | Term matching + context |
| Tone (enthusiastic) | Partial | Sentiment analysis |
| Technical accuracy | No | Human review |

### 4. Architecture Patterns

**Q4.1: Should this be a new agent or utility module?**
- Agent: Can iterate, ask for revisions
- Utility: Simpler, just reports metrics

**Q4.2: How does it integrate with existing classifier pipeline?**
```
semops-core classifier pipeline:
 TIER 1: RuleBasedClassifier → Format validation
 TIER 2: EmbeddingClassifier → Semantic similarity
 TIER 3: GraphClassifier → Structure analysis
 TIER 4: LLMClassifier → Quality scoring
```
Style checking maps to TIER 1 (rules) + TIER 2 (concept drift)

**Q4.3: What's the output format?**
```yaml
# posts/my-slug/style_report.yaml
style: blog
metrics:
 pvi: 2.3%
 car: 4.5%
 readability: 8.2 # grade level
 avg_paragraph_length: 4.2
violations:
 - line: 14
 rule: passive_voice
 text: "The feature was implemented..."
 suggestion: "We implemented the feature..."
 - line: 28
 rule: concept_context
 concept: riverbend-hypothesis
 found_context: null
 expected_context: engagement_verb
```

---

## Decision

### Scope Decisions (2025-12-06)

| Question | Decision | Rationale |
|----------|----------|-----------|
| Style priority | GitHub Docs first | Authority/clarity style, easier to validate programmatically |
| Concept scope | 1P concepts only | Focus on proprietary terminology consistency |
| Tolerance | Advisory + targeted fixes | Report all, user decides which to address |
| Integration | Standalone in ike-publisher | Refinement layer, not classification concern |

### Conceptual Separation

**Ingestion (orchestrator):** What is this content? Where does it fit in the knowledge graph?
- Uses classifier pipeline (rules → embedding → graph → LLM)
- Concerned with categorization, relationships, provenance

**Egestion (publisher):** Is this content polished enough to publish?
- Uses style checker
- Concerned with voice, clarity, concept presentation
- Refinement pass before human editing

### Future Consideration: Consistency Audit

A separate, optional tool could audit target repo folders for terminology consistency and report back to orchestrator. This is **not** part of the style checking workflow - it's a different concern (ensuring docs across repos use concepts consistently vs. polishing a single piece for publication).

---

### Proposed Approach

**Phase 1: Core Writing Style**
1. Create `STYLE_GUIDE.md` with GitHub Docs rules
2. Implement style checker with Tier 1 + Tier 2 checks
3. Add `/style-check` slash command
4. Output `style_report.md` with violations and suggestions

Focus: passive voice, gerunds, contractions, pronouns, redundancy, clichés, noun stacks

**Phase 2: 1P Concept Adherence (CAR)**
1. Export 1P concepts from orchestrator
2. Implement concept mention + context window analysis
3. Add `--concepts` flag for premium mode
4. Track CAR metrics for flagship content

**Phase 3: Blog Style + Refinement**
1. Add blog/informal style rules (flip constraints)
2. Style-aware draft agent prompting
3. Iterative refinement based on learning

---

## Implementation Plan

### Phase 1 Deliverables

#### 1. Style Guide Document
**File:** `STYLE_GUIDE.md`

Complete rule inventory from issue #20:

| # | Rule | GitHub Docs | Blog | Detection |
|---|------|-------------|------|-----------|
| 1 | **Passive Voice** | Prohibited (PVI=0%) | Discouraged (PVI≤5%) | spaCy dependency |
| 2 | **Redundant Phrases** | Avoid ("in order to"→"to") | Avoid | Phrase list |
| 3 | **Complex Vocabulary** | Use simple words | Use simple words | TBD |
| 4 | **Person/Voice** | Third-person only | First/second-person OK | Pronoun regex |
| 5 | **Markdown Structure** | Consistent headings/lists | Consistent | Structure parse |
| 6 | **Paragraph Length** | 3-5 sentences max | 3-5 sentences max | Sentence count |
| 7 | **Serial Comma** | Always (Oxford) | Always (Oxford) | Regex |
| 8 | **AI Clichés** | Prohibited | Prohibited | Phrase blacklist |
| 9 | **Noun Stacks** | Break up chains | Break up chains | POS pattern |
| 10 | **Gerunds** (as nouns) | **Prohibited** | Allowed | POS detection |
| 11 | **Contractions** | **Prohibited** | **Required** | Regex |
| 12 | **Weasel Words** | Prohibited | Avoid (OK for humor) | Word list |
| 13 | **Exclamation Points** | **Prohibited** | Max 1 per sentence | Count |
| 14 | **Analogies** | Avoid | Encouraged | Manual review |
| 15 | **1P Concept Context** | Hedging verbs | Engagement verbs | Context window (CAR) |

**Phrase Blacklists:**

Redundancy:
- "at this point in time" → "now"
- "due to the fact that" → "because"
- "in order to" → "to"

AI Clichés:
- "In conclusion,"
- "It is important to note that..."
- "In today's fast-paced world..."
- "At the end of the day..."

Weasel Words:
- "somewhat", "arguably", "probably", "possibly"
- "it could be said that", "some people think"

Hedging Verbs (for 1P concepts in GitHub Docs):
- suggests, implies, describes, theorizes, is consistent with

Engagement Phrases (for 1P concepts in Blog):
- "we're thinking", "check out", "our idea is", "this cool thing"

#### 2. Style Checker Agent
**File:** `agents/style_checker.py`

Standard LLM agent pattern - no special NLP libraries needed. Claude handles all language analysis directly.

```python
class StyleCheckerAgent:
 """Analyze content against style guidelines and report violations."""

 def check(self, content: str, style: str = "github_docs") -> str:
 # Load style rules into prompt
 # Send content to Claude
 # Return structured report (violations + suggestions)
```

The agent prompt includes:
- Style rules (from STYLE_GUIDE.md)
- Expected output format (line numbers, violations, suggestions)
- Examples of each violation type

All detection is language-native - passive voice, gerunds, pronouns, clichés are things Claude understands without regex or dependency parsing.

#### 3. Slash Command
**File:** `.claude/commands/style-check.md`

```yaml
---
description: Validate draft against GitHub Docs style guidelines
---
```

Workflow:
1. Ask for post slug
2. Load `draft.md` or `final.md`
3. Run style checker (standard or premium mode)
4. Output report with line numbers and suggestions
5. Offer to fix specific violations

#### 4. Report Format
**File:** `posts/<slug>/style_report.md`

```markdown
# Style Report: my-post-slug
> Style: GitHub Docs
> Generated: 2025-12-06

## Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| PVI (Passive Voice) | 3.2% | 0% | ⚠️ |
| Contractions | 0 | 0 | ✅ |
| First-person pronouns | 2 | 0 | ⚠️ |
| Gerunds (as nouns) | 1 | 0 | ⚠️ |

## Violations (5 found)

### Passive Voice (2)
- **Line 14:** "The feature was implemented by the team"
 - Suggestion: "The team implemented the feature"
- **Line 28:** "The API is called by the client"
 - Suggestion: "The client calls the API"

### First-Person Pronouns (2)
- **Line 7:** "We recommend using..."
 - Suggestion: "The documentation recommends..." or "Users should..."
- **Line 35:** "Our approach focuses on..."
 - Suggestion: "This approach focuses on..."

### Gerunds (1)
- **Line 22:** "Configuring the system requires..."
 - Suggestion: "To configure the system..." or "System configuration requires..."
```

### Dependencies

No new dependencies - uses existing Anthropic API setup.

### Integration Points

| Trigger | Action |
|---------|--------|
| `/style-check <slug>` | Manual validation, outputs report |
| `python publish.py style-check <slug>` | CLI equivalent |
| Post-draft (optional) | Auto-run after draft generation |

### Not in Scope (Phase 1)

- Blog style rules (Phase 3)
- Automated fixes without approval
- Integration with orchestrator classifier
- Cross-repo consistency audit
- Embedding-based drift detection

---

## Session Log

### 2025-12-06 - Initial Research

**Explored:**
- ike-publisher architecture: 4-agent workflow, file-based, HITL review points
- semops-core: concept system, classifier pipeline, embedding infrastructure
- Issue #20: Detailed style rules, PVI/CAR metrics, hedging vs engagement verbs

**Key Findings:**
1. Style checking fits naturally post-draft, before human editing
2. Orchestrator already has tiered classifier infrastructure we can leverage
3. Concept inventory has 180 unique concepts with ownership/maturity metadata
4. spaCy dependency parsing can identify passive voice patterns
5. Both repos use Claude; prompts can be enhanced with explicit style context

### 2025-12-06 - Scope Alignment

**Decisions Made:**
1. GitHub Docs style first (active voice, third-person, hedging verbs)
2. 1P concepts only (focus on proprietary terminology)
3. Advisory reports with targeted fixes (not hard blocking)
4. Standalone in ike-publisher (refinement layer, not classification)

**Key Insight: Ingestion vs Egestion**
- Orchestrator classifier = **ingestion** (categorize for knowledge graph)
- Publisher style checker = **egestion** (polish for publication)

These are separate concerns. Style checking doesn't need classifier integration.

**1P Concept Checking = Premium Layer**
The 1P concept adherence (CAR metric) is an extra layer for critical assets, not default behavior:
- Standard run: PVI, pronouns, contractions, paragraph length
- Premium run: Add CAR for 1P concept presentation

This allows quick style checks on routine content while enabling deeper analysis for flagship posts.

**Future: Consistency Audit (Separate Tool)**
Could audit repo folders for terminology drift and report to orchestrator. Not part of publishing workflow - different concern entirely.

**Phase 1 Scope Refinement:**
CAR (Concept Adherence Rate) moved to Phase 2. Phase 1 focuses on core writing mechanics:
- Tier 1: Contractions, pronouns, exclamations, redundancy, clichés, weasel words
- Tier 2: Passive voice (PVI), gerunds, noun stacks

This keeps Phase 1 about writing style, Phase 2 about 1P concept integration.

**Next Steps:**
1. ~~Create `STYLE_GUIDE.md` with GitHub Docs rules~~ ✅
2. Implement Tier 1 + Tier 2 checks in `lib/style_checker.py`
3. Build `/style-check` slash command
4. Test on existing draft content
5. Document pattern in `semops-core/docs/domain-patterns/` for cross-repo reuse

### 2025-12-09 - Phase 1 Complete

**Completed:**
1. Created separate style guides in ike-publisher:
 - `BLOG_STYLE_GUIDE.md` - Writing voice for blog posts
 - `TECHNICAL_DOCS_STYLE_GUIDE.md` - Writing voice for technical documentation
 - `TECHNICAL_DOCS_STYLE_GUIDE.md (format section)` - Document structure, naming, markdown conventions

2. Integrated blog style guide into draft agent (`agents/draft.py`)

3. Updated cross-repo references:
 - semops-dx-orchestrator PROCESS.md - Added Writing Style section
 - semops-dx-orchestrator INFRASTRUCTURE.md - Added Diagramming section
 - project-ike-private STYLE_GUIDE.md - Redirects to ike-publisher
 - project-ike-private CLAUDE.md & README.md - Updated links
 - semops-core doc-style.md - Updated links

**Key Decision:** Separated format (structure/naming) from style (voice/tone) into distinct documents.

**Deferred to Phase 2:**
- Style checker agent with PVI/CAR metrics
- `/style-check` slash command
- 1P concept adherence checking

---

## References

### Internal
- 
- [ADR-0004: Concept as Aggregate Root](../../../semops-core/docs/decisions/ADR-0004-concept-aggregate-root.md)
- [Classifier Infrastructure](../../../semops-core/docs/domain-patterns/classifier-infrastructure.md)

### Style Rule Sources
- [Microsoft Writing Style Guide](https://learn.microsoft.com/en-us/style-guide/) - Primary source for gerunds, noun stacks, global content
- [Chicago Manual of Style](https://www.chicagomanualofstyle.org/) - Formal writing, serial comma
- [Strunk & White - Elements of Style](https://www.thewritersforhire.com/why-technical-writers-need-strunk-whites-the-elements-of-style/) - Active voice philosophy
- [Veeam Technical Writing Guidelines](https://helpcenter.veeam.com/docs/styleguide/tw/gerunds.html) - Gerund avoidance in docs
- [Google Technical Writing Resources](https://developers.google.com/tech-writing/resources)

### Metrics Notes
- **PVI (Passive Voice Index)**: Term coined in issue #20. Industry standard is simply "passive sentence percentage"
- **Threshold**: Microsoft Word readability suggests <2% passive; academic papers average 20-26%
- **CAR (Concept Adherence Rate)**: Novel metric from issue #20 for 1P terminology enforcement
- [Ubiquitous Language](../../../semops-core/schemas/UBIQUITOUS_LANGUAGE.md)
