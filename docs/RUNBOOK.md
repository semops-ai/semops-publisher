# Runbook

> **Repo:** `semops-publisher`
> **Status:** ACTIVE
> **Version:** 1.0.0
> **Last Updated:** 2025-12-17

## Quick Reference

| Task | Command |
|------|---------|
| New post | `python publish.py new <slug>` |
| Research | `python publish.py research <slug>` |
| Outline | `python publish.py outline <slug>` |
| Draft | `python publish.py draft <slug>` |
| Format | `python publish.py format <slug>` |
| Start ComfyUI | `cd comfyui && docker compose up -d` |

## Content Workflow

### Starting a New Post

```bash
# 1. Create post structure
python publish.py new my-post-slug

# 2. Edit notes
# Edit posts/my-post-slug/notes.md with topic, POV, references

# 3. Run research
python publish.py research my-post-slug

# 4. Generate outline (iterate as needed)
python publish.py outline my-post-slug
python publish.py outline my-post-slug --version 2

# 5. Copy best outline to outline_final.md

# 6. Generate draft
python publish.py draft my-post-slug

# 7. Edit draft.md, save as final.md

# 8. Format for publishing
python publish.py format my-post-slug

# 9. Copy-paste to platforms
```

### Post File Structure

```text
posts/my-post-slug/
├── notes.md              # Input: topic, POV, references
├── research.md           # Agent: findings, sources
├── outline_v1.md         # Agent: first outline
├── outline_final.md      # Human: approved outline
├── draft.md              # Agent: full draft
├── final.md              # Human: edited draft
├── linkedin.md           # Agent: LinkedIn format
├── frontmatter.yaml      # Agent: metadata
└── assets/               # Images, diagrams
```

## Image Generation (ComfyUI)

### Starting ComfyUI

```bash
cd comfyui
docker compose up -d

# Access at the ComfyUI web interface
```

### Stopping ComfyUI

```bash
cd comfyui
docker compose down
```

### Model Storage

Models are stored centrally in a dedicated `models/` directory (shared across tools):

```text
models/
├── checkpoints/     # Base models (SDXL, SD 1.5)
├── loras/           # LoRA models
├── controlnet/      # ControlNet models
├── vae/             # VAE models
└── upscale_models/  # Upscalers
```

## Common Issues

### Issue: Research agent returns empty results

**Symptoms:**
- `research.md` is mostly empty
- No sources found

**Cause:**
- `notes.md` missing repo references
- Referenced repos not accessible

**Fix:**
- Ensure notes.md includes explicit repo paths
- Verify repos exist at referenced paths

### Issue: Draft doesn't match style

**Symptoms:**
- Draft tone/style doesn't match existing posts

**Cause:**
- Missing or poor style references

**Fix:**
- Add representative posts to `posts/_references/`
- Include diverse examples (technical, narrative, etc.)

### Issue: ComfyUI out of memory

**Symptoms:**
- Generation fails with CUDA OOM
- Container crashes

**Cause:**
- Model too large for GPU VRAM
- Too many models loaded

**Fix:**
```bash
# Restart ComfyUI to clear VRAM
cd comfyui && docker compose restart

# Use smaller models or lower resolution
```

## External Service Notes

### Anthropic API (Claude)

**Auth:**
- `ANTHROPIC_API_KEY` in `.env`

**Gotchas:**
- Rate limits on heavy usage
- Model names change (update `CLAUDE_MODEL` in config)

### LinkedIn

**Publishing:**
- Manual copy-paste from `linkedin.md`
- Platform reformats automatically

## Environment Setup

### Required Environment Variables

| Variable | Purpose | Where to Get |
|----------|---------|--------------|
| `ANTHROPIC_API_KEY` | Claude API access | Anthropic console |
| `CLAUDE_MODEL` | Model to use | Default: claude-sonnet-4-20250514 |

### Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy env template
cp .env.example .env
# Edit .env with your API key
```

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DIAGRAM_STANDARDS.md](DIAGRAM_STANDARDS.md) - Diagram specs
