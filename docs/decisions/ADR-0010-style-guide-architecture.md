# ADR-0010: Style Guide Architecture

> **Status:** Complete
> **Date:** 2026-01-19
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/52)

## Executive Summary

Establish semops-publisher as the owner of style guides for content generation, document all style guides in ARCHITECTURE.md, and register them across the Project Ike ecosystem via dx-hub domain-patterns.

## Context

### The Need

semops-publisher generates content for multiple formats:
- Technical documentation
- Blog posts and social content
- Whitepapers and thought leadership

Each format requires different voice and tone. Style guides existed (`BLOG_STYLE_GUIDE.md`, `GITHUB_DOCS_STYLE_GUIDE.md`) but were:
- Not documented in ARCHITECTURE.md
- Not referenced in README or CLAUDE.md
- Missing a whitepaper-specific guide

### Ownership Model

```
semops-publisher (Content Generation)
├── Owns: Style guides (voice, tone, formatting)
├── Owns: Edit corpus organized by style guide
└── Consumers: Draft Agent, Format Agent, human authors

semops-dx-orchestrator (Platform/DX)
├── Owns: domain-patterns (process documentation)
└── References: semops-publisher style guides in doc-style.md
```

## Decision

### Style Guide Hierarchy

| Guide | Purpose | Voice |
|-------|---------|-------|
| `style-guides/technical.md` | Technical documentation (voice + formatting) | Objective 3rd person, no contractions |
| `style-guides/blog.md` | Blog posts, social content | Conversational "you/we", contractions |
| `style-guides/whitepaper.md` | Whitepapers, thought leadership | Authoritative, evidence-based |

**Note:** Style guides moved to `style-guides/` directory with shorter names (2026-01-27). Original `GITHUB_DOCS_STYLE_GUIDE.md` and `GITHUB_DOCS_FORMAT.md` were merged into `technical.md`.

### Documentation Chain

```
README.md
└── Documentation section
 └── Style Guides table (quick reference)

CLAUDE.md
└── Key Concepts section
 └── Style Guides table → links to ARCHITECTURE.md

docs/ARCHITECTURE.md
└── Core Components section
 └── 4. Style Guides (full documentation)
 - Integration details
 - Agent usage
 - Cross-repo references

semops-dx-orchestrator/docs/domain-patterns/doc-style.md
└── Related Documentation section
 └── Style Guides (semops-publisher) table
```

## Consequences

### Positive

- Style guides discoverable through standard documentation paths
- Clear ownership (semops-publisher owns, dx-hub references)
- Agents can find appropriate style guide for content type
- New style guides follow established pattern

### Negative

- Cross-repo dependency (dx-hub references semops-publisher)
- Requires global_architecture sync when adding new guides

### Risks

- Style guides could drift from actual usage patterns
- Mitigated by: Edit capture workflow  for feedback loop

## Implementation

### Files Created

- `WHITEPAPER_STYLE_GUIDE.md` - New style guide based on guidelines

### Files Modified

- `docs/ARCHITECTURE.md` - Added "4. Style Guides" section
- `README.md` - Added Style Guides subsection
- `CLAUDE.md` - Added Style Guides section under Key Concepts
- `semops-dx-orchestrator/docs/domain-patterns/doc-style.md` - Updated style guide references

### Final Step

Run semops-dx-orchestrator global_architecture script to propagate changes across ecosystem.

## Related

- [](https://github.com/semops-ai/semops-docs/issues/77) - Whitepaper guidelines (source content)
- [](https://github.com/semops-ai/semops-publisher/issues/51) - Edit capture workflow (future iteration)
- [ADR-0001-narrative-style-system.md](ADR-0001-narrative-style-system.md) - Earlier style system research
