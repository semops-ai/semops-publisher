# semops-publisher

[![GitHub](https://img.shields.io/badge/org-semops--ai-blue)](https://github.com/semops-ai)
[![Website](https://img.shields.io/badge/web-semops.ai-green)](https://semops.ai)

**AI-assisted content publishing workflow** - research, outlining, drafting, and multi-platform formatting.

## What is This?

`semops-publisher` provides an AI-assisted pipeline for creating and publishing content. It implements a multi-agent workflow that takes notes through research, outlining, drafting, and formatting for multiple platforms.

## Agent Workflow

```
notes.md → Research → Outline → Draft → Format → publish
                                              │
                                              ├── WordPress
                                              ├── LinkedIn
                                              └── Knowledge Base
```

### Agents

| Agent | Purpose |
|-------|---------|
| **Research** | Gather 1P sources, validate concepts, compile research notes |
| **Outline** | Structure content, define sections, create skeleton |
| **Draft** | Generate full prose from outline |
| **Format** | Adapt for WordPress, LinkedIn, knowledge system |

## Quick Start

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add ANTHROPIC_API_KEY

# Create and publish a post
/new-post my-post-slug     # Create post structure
# Edit posts/my-post-slug/notes.md
/research                  # Run research agent
/outline                   # Generate outline
/draft                     # Generate draft
# Edit draft.md → final.md
/format                    # Format for publishing
```

## Slash Commands

| Command | Description |
|---------|-------------|
| `/new-post` | Create new post with directory structure |
| `/research` | Run research phase |
| `/outline` | Generate outline from research |
| `/draft` | Generate draft from outline |
| `/format` | Format for WordPress, LinkedIn |
| `/status` | Check post status |

## Role in Architecture

```
semops-dx-orchestrator [PLATFORM/DX]
        │
        ▼
semops-core [SCHEMA/INFRASTRUCTURE]
        │
        │  Provides: Concepts, entities, knowledge base
        │
        ▼
semops-publisher [PUBLISHING]  ← This repo
        │
        │  Owns: Content production, agent pipeline
        │
        ▼
semops-sites [FRONTEND]
        │
        └── Final publishing destination
```

## Post Structure

Each post lives in its own directory:

```
posts/my-post-slug/
├── notes.md          # Initial notes and ideas
├── research.md       # Research agent output
├── outline.md        # Outline agent output
├── draft.md          # Draft agent output
├── final.md          # Edited final version
├── metadata.yaml     # Post metadata
└── formats/
    ├── wordpress.md  # WordPress-formatted
    └── linkedin.md   # LinkedIn-formatted
```

## Documentation

- [CLAUDE.md](CLAUDE.md) - AI agent instructions
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Technical architecture
- [docs/decisions/](docs/decisions/) - Architecture Decision Records

## Related Repositories

| Repository | Role | Description |
|------------|------|-------------|
| [semops-dx-orchestrator](https://github.com/semops-ai/semops-dx-orchestrator) | Platform/DX | Process, global architecture |
| [semops-core](https://github.com/semops-ai/semops-core) | Schema/Infrastructure | Knowledge base |
| [semops-docs](https://github.com/semops-ai/semops-docs) | Documents | Source documents for research |
| [semops-data](https://github.com/semops-ai/semops-data) | Product | Data utilities |
| [semops-sites](https://github.com/semops-ai/semops-sites) | Frontend | Publishing destination |

## Contributing

This is currently a personal project by Tim Mitchell. Contributions are welcome once the public release is complete.

## License

[TBD - License to be determined for public release]
