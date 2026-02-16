# Infrastructure

> **Repo:** `semops-publisher`
> **Owner:** This repo owns and operates these services
> **Status:** ACTIVE
> **Version:** 1.0.0
> **Last Updated:** 2026-02-06

## Overview

semops-publisher has minimal infrastructure - primarily local ComfyUI for image generation. Most infrastructure needs (database, vector DB) are consumed from semops-core.

## Services

| Service | Purpose | Status |
|---------|---------|--------|
| ComfyUI | Image generation (SDXL, LoRAs) | On-demand |

## ComfyUI

Local GPU-based image generation using ComfyUI.

**Location:** `comfyui/docker-compose.yml`

### Starting

```bash
cd comfyui
docker compose up -d
```

### Stopping

```bash
docker compose down
```

### Volumes

| Path | Purpose |
|------|---------|
| `models/` | Centralized model storage (checkpoints, LoRAs, VAE) |
| `./workflows/` | ComfyUI workflow JSON files |
| `./inputs/` | Input images (ControlNet, img2img) |
| `./outputs/` | Generated output images |
| `comfyui_custom_nodes` | Custom nodes (Docker volume) |

### Model Storage

Models are stored centrally per ADR-0006. ComfyUI expects:

```text
models/
├── checkpoints/      # Base models (SDXL, SD 1.5)
├── loras/            # LoRA models
├── controlnet/       # ControlNet models
├── vae/              # VAE models
├── clip/             # CLIP models
├── clip_vision/      # CLIP vision models
├── ipadapter/        # IP-Adapter models
└── upscale_models/   # Upscalers
```

### GPU Requirements

- NVIDIA GPU with CUDA support
- Docker with nvidia-container-toolkit
- Minimum 8GB VRAM for SDXL

## Consumed Services

semops-publisher consumes infrastructure from other repos:

| Service | Source Repo | Purpose |
|---------|-------------|---------|
| PostgreSQL | semops-core | Knowledge base entities |
| Qdrant | semops-core | Vector similarity search |
| MCP Server | semops-core | Agent KB access |

## Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...     # Claude API for agents
CLAUDE_MODEL=claude-sonnet-4-20250514

# Supabase (consumed from semops-core)
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...

# Hugging Face (for model downloads)
HF_TOKEN=...
```

## Health Checks

```bash
# ComfyUI
curl -s <comfyui-service>/system_stats

# Check GPU is visible
nvidia-smi
```

## Cloud GPU (RunPod)

For heavy compute jobs, semops-publisher can offload to RunPod:

- AnimateDiff video generation
- Advanced ControlNet pipelines
- Batch image generation

**Setup:** Configure RunPod API key and endpoint in environment.

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - This repo's architecture
- ADR-0004: ComfyUI for Image Generation
- ADR-0006: Model Storage Architecture
