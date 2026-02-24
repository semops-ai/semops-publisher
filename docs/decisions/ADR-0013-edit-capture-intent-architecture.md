# ADR-0013: Edit Capture Intent Architecture

> **Status:** Draft
> **Date:** 2026-01-28
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/65)
> **Builds On:** [ADR-0008: Style Guide Architecture](./ADR-0008-style-guide-architecture.md)

---

## Executive Summary

Extend the edit capture system from structural diffs to a **style learning pipeline** that captures editorial intent ("why"), supports both human and agent editors, and feeds a normalization loop that hardens style guide rules over time. The corpus serves multiple destinations: local review, Postgres, vector DB, and training data export.

---

## Context

### Current State

The existing edit capture system (Issue #53, `scripts/capture_edits.py`) diffs `[ai-draft]` commits against current state and outputs YAML with before/after text and sentence-level context. It captures **what** changed but not **why**.

### The Gap

1. **No intent capture** — No `reason`, `rule_applied`, or rationale field in the schema
2. **Human edits only** — Agent edits are not captured at all
3. **No feedback loop** — Captured edits don't flow back into agent behavior or style guide updates
4. **No normalization** — Raw edits accumulate without deduplication, ranking, or rule extraction

### Why This Matters

The "why" behind an edit is the most valuable signal for:
- **Style guide hardening** — Repeated corrections become explicit rules
- **Training data** — Intent-labeled pairs (original, edited, reason) for SFT/RLHF
- **Agent improvement** — Loading distilled rules as context makes agents apply learned patterns
- **Audit** — Understanding whether human and agent edits agree on style rules

Key insight: the most valuable captures happen early — when actively shaping agent behavior. Early edits become foundational "big rules." Per-edit logging during interactive sessions is essential for this real-time evaluation, not just post-hoc training data.

---

## Decision

### Two Capture Paths, One Corpus

#### 1. Agent Edits → Sidecar Append Log

Agents write to `edits/.pending/<file>.yaml` as they edit, per-edit granularity.

```yaml
# edits/.pending/semops-whitepaper-v2.yaml
- original: "Our methodology focuses on..."
 edited: "The methodology focuses on..."
 reason: "Removing first person per whitepaper style guide"
 rule_applied: "whitepaper.md#voice"
 style: whitepaper
 flagged: false
 timestamp: 2026-01-28T14:30:00Z
 file: posts/whitepaper-semops/semops-marketing-whitepaper-v2.md
 line: 42
```

- Agent knows "why" in the moment — capturing later loses fidelity
- Human-readable during editing — doubles as real-time feedback monitor
- Per-edit append: ordering preserved, early entries carry most weight
- `flagged: true` for entries the user or agent marks as important

#### 2. Human Edits → Inline Annotation via `/capture-edits`

Extends the existing diff-based capture with rationale prompting:

- Commit message = default session-level reason for all edits
- `/capture-edits` shows edits interactively, user selectively annotates significant ones
- Trivial edits (typos, whitespace) auto-skipped or `reason: null`

#### 3. Merge Step

`/capture-edits` reads sidecar (if exists) + git diff → unified corpus in `edits/`.

Both paths produce the same schema with `editor_type` distinguishing source.

### Toggle Mechanism

Explicit `/capture on` and `/capture off` slash commands.

| Mode | Trigger | Capture | Review |
| --- | --- | --- | --- |
| Interactive (HITL) | `/capture on` in VSCode | Sidecar append, real-time | During session |
| Autonomous | `/capture on` in automation manifest | Same sidecar append | Post-session |
| Human-only | `/capture-edits` after manual editing | Git diff + rationale prompt | Post-edit |

- Near-term: all interactive/active sessions
- Future: automation manifests reuse the same slash command interface
- `/capture on` also loads the distilled rule set as agent context (style-aware editing mode)

### Unified Corpus Schema

```yaml
source_file: posts/example/content.md
baseline_commit: abc1234
captured_at: 2026-01-28T14:30:00Z
editor_type: human | agent
style: blog | whitepaper | technical
session_reason: "Tightened tone for conversational blog style"
edits:
 - id: edit-001
 original: "..."
 edited: "..."
 sentence_before: "..."
 line_number: 42
 reason: "Active voice per style guide"
 rule_applied: "blog.md#voice-active"
 flagged: false
 timestamp: 2026-01-28T14:30:00Z
```

### Style Scoping

Every edit inherits a `style` from its source document. During normalization:

- Rules appearing across multiple styles → `scope: global`
- Rules appearing in one style only → `scope: <style>`
- Enables per-style rule sets and a global baseline

### Agentic Normalization (`/corpus review`)

A separate agent step that reads accumulated corpus and produces a **distilled rule set**:

```yaml
rules:
 - id: rule-001
 statement: "Use third person in whitepapers, never first person"
 style: whitepaper
 scope: style-specific
 frequency: 12
 confidence: high
 source_edits: [edit-003, edit-017, edit-022]
 flagged: true
 - id: rule-002
 statement: "Prefer active voice over passive constructions"
 style: null
 scope: global
 frequency: 28
 confidence: high
 source_edits: [edit-001, edit-005, ...]
 flagged: true
```

Functions:
- **Deduplicates** — "removed first person" appears 12 times → one rule with frequency
- **Ranks** — by frequency, flagged status, recency
- **Normalizes** — varying phrasings → canonical rule statement
- **Scopes** — global vs style-specific based on cross-style analysis
- **Promotes** — candidates for style guide updates (manual approval)

### Feedback Loop

```
Edits (sidecar + diff)
 → Raw corpus (YAML, git-versioned)
 → Agentic normalization (/corpus review)
 → Distilled rule set (per-style + global)
 → Agent context on /capture on (loop closes)
 → Style guide updates (manual promotion)
 → Training data export (JSONL for SFT/RLHF)
 → Postgres/vector for query and analysis
```

### Multi-Destination Data

The local YAML corpus is the source of truth. Export scripts push to other destinations:

| Destination | Format | Use |
| --- | --- | --- |
| Local files | YAML/MD | Human review, git-versioned, session notes |
| Postgres | Structured rows | Query, aggregate, frequency analysis |
| Vector DB | Embeddings of rule statements | Semantic search ("edits like this one") |
| Training export | JSONL pairs | SFT/RLHF fine-tuning data |

Follows existing pattern: corpus files → SQL via export scripts (cf. `corpus_to_sql.py`).

---

## Consequences

### Positive

- Captures the most valuable signal (intent) that is currently lost
- Both human and agent edits flow into unified corpus — enables comparison
- Distilled rules feed back into agent context — self-improving loop
- Style scoping separates global patterns from format-specific rules
- Format-agnostic corpus supports multiple downstream consumers
- Real-time sidecar enables interactive evaluation of agent behavior

### Negative

- Agent edit logging adds overhead per edit (Bash call to `log_edit.py`)
- Relies on agent compliance with CLAUDE.md convention when capture is on
- Normalization agent adds a manual step before rules are usable
- Multiple data destinations increase maintenance surface

### Risks

- **Corpus noise** — Low-quality edits dilute signal. Mitigated by: flagging, normalization, frequency thresholds.
- **Agent compliance** — Agent may forget to log. Mitigated by: `scripts/log_edit.py` helper, slash command instructions, CLAUDE.md convention.
- **Schema drift** — Multiple destinations could diverge. Mitigated by: YAML as single source of truth, export scripts validate schema.
- **Over-engineering** — Building the full pipeline before validating the capture step works. Mitigated by: phased implementation.

---

## Implementation Plan

### Phase 1: Capture Infrastructure

- [ ] `scripts/log_edit.py` — Append helper for sidecar YAML
- [ ] `/capture on` / `/capture off` slash commands
- [ ] Extend `/capture-edits` with human rationale prompting
- [ ] Update corpus schema with intent fields
- [ ] CLAUDE.md convention: "When capture is on, log edits via `log_edit.py`"
- [ ] `edits/.pending/` directory structure

### Phase 2: Merge and Review

- [ ] Merge step in `/capture-edits`: sidecar + diff → unified corpus
- [ ] Sidecar review UI in `/capture-edits` (confirm/edit/flag before merge)
- [ ] Auto-archive `.pending/` after merge

### Phase 3: Normalization and Feedback

- [ ] `/corpus review` agent — deduplicate, rank, normalize, scope
- [ ] Distilled rule set format and storage
- [ ] `/capture on` loads distilled rules as agent context
- [ ] Style guide promotion workflow (rule → style guide update, manual approval)

### Phase 4: Multi-Destination Export

- [ ] Postgres export script (extends `corpus_to_sql.py` pattern)
- [ ] Vector DB export (rule statement embeddings)
- [ ] JSONL training data export (SFT/RLHF pairs)

---

## Session Log

### 2026-01-28: Design Session

**Status:** Draft
**Tracking Issue:** [](https://github.com/semops-ai/semops-publisher/issues/65)

**Completed:**
- Identified gap: no intent capture, no agent edit capture
- Designed two-path architecture (sidecar for agents, inline for humans)
- Decided explicit toggle (`/capture on/off`) over always-on
- Designed schema with style scoping and flagging
- Designed normalization agent and feedback loop
- Identified multi-destination data requirements

**Next Session Should Start With:**
1. Review this ADR for completeness
2. Begin Phase 1: `scripts/log_edit.py` and `/capture` slash command
3. Test with a real editing session on an active post

---

## References

- [ADR-0008: Style Guide Architecture](./ADR-0008-style-guide-architecture.md) — Style guide ownership and organization
- [ADR-0001: Narrative Style System](./ADR-0001-narrative-style-system.md) — Earlier style system research
- [Issue #51](https://github.com/semops-ai/semops-publisher/issues/51) — Edit capture workflow (parent)
- [Issue #53](https://github.com/semops-ai/semops-publisher/issues/53) — `/capture-edits` Phase 1 implementation
- [Issue #65](https://github.com/semops-ai/semops-publisher/issues/65) — This feature (intent + agent capture)
- `scripts/capture_edits.py` — Existing diff-based capture script
- `style-guides/` — Current style guides (blog, technical, whitepaper)

---

**End of Document**
