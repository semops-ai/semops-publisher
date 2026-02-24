# ADR-0009: Pandoc PDF Export with Font Integration

> **Status:** Complete
> **Date:** 2026-01-14
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/48)

## Executive Summary

Add markdown-to-PDF export using Pandoc with XeLaTeX, integrating fonts from semops-sites for consistent branding across templates.

## Context

### The Need

semops-publisher handles content creation (blog posts, proposals, documentation) but lacks export capability. Currently, final outputs go to:
- WordPress (via manual copy)
- LinkedIn (via manual copy)
- No PDF option

PDFs are needed for:
- Consulting proposals (semops brand)
- Professional documents (personal brand)
- Technical documentation (code-focused)

### Cross-Repo Font Infrastructure

semops-sites has a comprehensive font package:
```
semops-sites/packages/fonts/
├── ttf/ # 30+ fonts in TTF format
├── woff2/ # Web-optimized versions
└── fonts.json # Machine-readable manifest
```

Key fonts for PDF export:
- **DM Sans** - Clean sans-serif for body text
- **JetBrains Mono** - Monospace for code and technical headings
- **Inter** - Modern sans-serif alternative
- **Lora** - Serif for elegant headings

### Technology Choice: Why Pandoc + XeLaTeX

| Option | Pros | Cons |
|--------|------|------|
| **Pandoc + XeLaTeX** | Full typography control, code highlighting, real fonts | Requires texlive install |
| weasyprint | Pure Python, CSS styling | Limited typography, no ligatures |
| markdown-pdf (JS) | Simple | Node dependency, basic output |
| Prince XML | Professional quality | Commercial license |

**Decision:** Pandoc + XeLaTeX for professional typography and font support.

## Decision

### Architecture

```
semops-publisher/
├── scripts/
│ └── export_pdf.py # CLI entry point
├── templates/
│ ├── semops.latex # Consulting brand
│ ├── timjmitchell.latex # Personal brand
│ └── technical.latex # Documentation
└── pyproject.toml # uv dependencies
```

### Font Installation

Install fonts locally for XeLaTeX using fontconfig:
```bash
# One-time setup (documented in README)
mkdir -p ~/.local/share/fonts
cp ~/.local/share/fonts/
fc-cache -fv
```

This makes fonts available to XeLaTeX without modifying system fonts.

### Template Design

Each template specifies:
- Font family mappings (main, sans, mono)
- Color scheme (links, code, emphasis)
- Layout (margins, spacing, headers)
- Code block styling

#### semops.latex (Primary)
- **Body:** DM Sans
- **Headings:** JetBrains Mono (technical/modern feel)
- **Code:** JetBrains Mono
- **Colors:** Forest green accents (`#3a6b54`)

#### timjmitchell.latex (Personal)
- **Body:** Inter
- **Headings:** Lora (serif elegance)
- **Code:** JetBrains Mono
- **Colors:** Warm, professional palette

#### technical.latex (Documentation)
- **Body:** Inter
- **Headings:** JetBrains Mono
- **Code:** JetBrains Mono with line numbers
- **Style:** Tighter spacing, code-first

### CLI Interface

```bash
# Basic usage (semops template default)
uv run scripts/export_pdf.py input.md -o output.pdf

# Explicit template
uv run scripts/export_pdf.py proposal.md -o proposal.pdf --template semops

# Batch export
uv run scripts/export_pdf.py docs/*.md --outdir pdfs/
```

### Dependencies

**System (apt):**
```bash
sudo apt install pandoc texlive-xetex texlive-fonts-recommended
```

**Python (uv):**
- pypandoc - Pandoc wrapper
- pyyaml - Template configuration
- click - CLI framework

## Implementation Plan

1. [x] Set up uv project structure (`pyproject.toml`)
2. [x] Create font installation script/documentation
3. [x] Build `semops.latex` template first
4. [x] Implement `scripts/export_pdf.py` with basic CLI
5. [x] Add `timjmitchell.latex` and `technical.latex` templates
6. [x] Add batch export support
7. [x] Document in README

## Consequences

### Positive

- **Professional output:** XeLaTeX produces publication-quality PDFs
- **Brand consistency:** Templates enforce visual standards
- **Font integration:** Reuses existing semops-sites font investment
- **Extensible:** Easy to add new templates

### Negative

- **System dependency:** Requires pandoc + texlive-xetex (~500MB)
- **Cross-repo coupling:** Depends on semops-sites font paths
- **Learning curve:** LaTeX templates require LaTeX knowledge to modify

### Risks

| Risk | Mitigation |
|------|------------|
| Font not found | Installation script with verification |
| Template errors | Test with sample documents before release |
| Cross-repo path changes | Document expected font location, fail with helpful error |

## Session Log

### 2026-01-14

- Created ADR documenting PDF export architecture
- Chose Pandoc + XeLaTeX for professional typography
- Defined four templates: semops, timjmitchell, technical, resume
- Downloaded Google Fonts to semops-sites font manifest 
- Installed fonts locally for XeLaTeX access
- Created all three LaTeX templates
- Implemented export_pdf.py CLI with single/batch modes
- Updated README with documentation
- ADR marked complete
