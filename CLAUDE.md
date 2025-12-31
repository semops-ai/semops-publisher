# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Role in Global Architecture

**Role:** Publishing (Content Production)

```
semops-publisher [PUBLISHING]
        │
        ├── Owns: Content production pipeline
        │   - Research/Outline/Draft/Format agents
        │   - Post directory structure
        │   - Platform formatting (WordPress, LinkedIn)
        │
        └── Depends on: semops-core [INFRASTRUCTURE]
            - Concepts and entities
            - Knowledge base for research
```

**Bounded Context:** Content production - owns the pipeline from notes to published content.

## Agent Workflow

The publishing pipeline uses specialized agents:

```
notes.md → Research → Outline → Draft → Format
```

| Agent | Input | Output |
|-------|-------|--------|
| Research | notes.md | research.md |
| Outline | research.md | outline.md |
| Draft | outline.md | draft.md |
| Format | final.md | wordpress.md, linkedin.md |

## Post Structure

```
posts/my-post-slug/
├── notes.md          # Initial notes
├── research.md       # Research output
├── outline.md        # Outline output
├── draft.md          # Draft output
├── final.md          # Edited final
├── metadata.yaml     # Post metadata
└── formats/
    ├── wordpress.md
    └── linkedin.md
```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/new-post` | Create new post with directory structure |
| `/research` | Run research agent |
| `/outline` | Generate outline |
| `/draft` | Generate draft |
| `/format` | Format for platforms |
| `/status` | Check post status |

## Key Files

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture
- [posts/](posts/) - Post directories
- [agents/](agents/) - Agent implementations
- [docs/decisions/](docs/decisions/) - Architecture Decision Records

## Integration with semops-core

The research agent queries semops-core for:
- Concept definitions and relationships
- Entity metadata
- Knowledge base entries

Ensure semops-core is running for full research capabilities.
