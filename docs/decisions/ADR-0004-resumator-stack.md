# ADR-0002: Resumator Frontend Stack

> **Status:** Complete
> **Date:** 2025-12-05
> **Related Issue:** 

---

## Executive Summary

Selected and deployed a modern web stack for timjmitchell.com (semops-sites) using Next.js, Tailwind CSS, Supabase, and Vercel. Successfully deployed test site and documented the full stack for future development.

---

## Context

Need a personal portfolio/blog site that:
- Serves as public-facing presence (timjmitchell.com)
- Supports interactive data visualizations from Python/Jupyter workflows
- Integrates with ike-publisher for content pipeline
- Will eventually host AI chatbot features with LinkedIn OAuth
- Keeps data/backend as IP with thin, interchangeable frontend

Previous experience was ~15 years ago (XML/XSLT era), so needed a modern stack that's well-supported and maintainable.

---

## Decision

### Stack Selected

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Framework** | Next.js 16 (App Router) | React framework with SSR, file-based routing |
| **Language** | TypeScript | Type safety, better tooling |
| **Styling** | Tailwind CSS v4 | Utility-first CSS |
| **Components** | ShadCN UI + Radix | Accessible, customizable UI primitives |
| **Database** | Supabase (PostgreSQL) | Backend-as-a-Service with auto-generated API |
| **Content** | MDX | Markdown + React components for blog |
| **Visualization** | Plotly.js | Interactive charts, Python export support |
| **Hosting** | Vercel | Auto-deploy from GitHub, global CDN |
| **DNS/Security** | Cloudflare | DDoS protection, WAF, SSL |

### Why This Stack

1. **Mainstream & well-supported** - Large community, extensive documentation, not going anywhere
2. **Python integration** - Plotly exports directly from Jupyter to web
3. **Supabase as BaaS** - No need to build/maintain backend API; database is the IP
4. **Vercel + Next.js** - Same company, optimized integration
5. **File-based content** - Blog posts are MDX files in git, no CMS dependency

---

## Consequences

**Positive:**
- Rapid deployment (test site live same day)
- Comprehensive documentation created for future reference
- Design tools (Lovable, v0.dev) generate compatible code
- Clear separation: data/backend = IP, frontend = interchangeable

**Negative:**
- Learning curve for modern React patterns (Server Components, App Router)
- Plotly requires `unsafe-eval` in CSP (security tradeoff)

**Risks:**
- Vercel pricing at scale (mitigated: can self-host Next.js if needed)
- Supabase vendor lock-in (mitigated: standard PostgreSQL, can migrate)

---

## Implementation Completed

### Infrastructure
- [x] Next.js project initialized with TypeScript, Tailwind, ShadCN
- [x] Supabase project created with local dev setup
- [x] Vercel deployment connected to GitHub (auto-deploy on push)
- [x] Test deployment successful

### Documentation Created
- [x] `docs/STACK-OVERVIEW.md` - Comprehensive stack documentation
 - Architecture diagrams
 - Technology layer explanations
 - Data flow patterns
 - Security configuration (Cloudflare + Vercel + Supabase)
 - Development commands

### Components Added
- [x] `src/components/charts/` - Plotly integration
 - `PlotlyChart` - Direct Python export rendering
 - `InteractiveChart` - Dimension switching UI
- [x] `src/components/layouts/` - Page layout primitives
 - `PageLayout` - Container with width variants
 - `PageHeader` - Consistent h1 + subtitle
 - `Section` - Content sections with spacing

### SEO & Discoverability
- [x] `next-sitemap` configured (auto-generates sitemap.xml)
- [x] `public/llms.txt` - AI assistant discoverability
- [x] Postbuild script for sitemap generation

### GitHub Issues Created (semops-sites repo)
- [#3 Domain cutover checklist](https://github.com/semops-ai/semops-sites/issues/3)
- [#4 Security hardening checklist](https://github.com/semops-ai/semops-sites/issues/4)
- [#5 SEO, Analytics & Social Integration](https://github.com/semops-ai/semops-sites/issues/5)

---

## Publishing Pipeline (Next Steps)

Content flow from ike-publisher to semops-sites:

```
ike-publisher (content creation)
 │
 ▼
 MDX file with frontmatter
 (title, date, description)
 │
 ▼
 Push to semops-sites repo
 src/content/blog/*.mdx
 │
 ▼
 Vercel auto-deploys
 │
 ▼
 Live at timjmitchell.com/blog/*
```

See for pipeline implementation details.

---

## Session Log

### 2025-12-05: Initial Stack Setup & Documentation
**Status:** Complete

**Completed:**
- Deployed Next.js site to Vercel (resolved 404 issue - Root Directory config)
- Created comprehensive STACK-OVERVIEW.md documentation
- Added Plotly components for data visualization
- Configured next-sitemap and llms.txt
- Added security section to docs (Cloudflare/Vercel/Supabase layers)
- Created layout primitives (PageLayout, PageHeader, Section)
- Created GitHub issues for pre-launch checklists (#3, #4, #5)
- Discussed Lovable integration for design workflow
- Paused Vercel deployment (test complete, will redeploy when ready)

**Key Decisions Made:**
- Will use Lovable's layouts rather than custom primitives (less friction)
- LinkedIn OAuth required for visitor-facing chatbot (not anonymous)
- RAG strategy: hybrid retrieval with confidence-based routing

**Next Session Should Start With:**
1. Design work in Lovable connected to Supabase
2. Career timeline data model and initial content
3. Blog publishing pipeline implementation (#15)

---

## References

- [semops-sites repo](https://github.com/semops-ai/semops-sites)
- [STACK-OVERVIEW.md](https://github.com/semops-ai/semops-sites/blob/main/docs/STACK-OVERVIEW.md)
- [semops-core #74 - RAG Architecture](https://github.com/semops-ai/semops-core/issues/74)

---

**End of Document**
