# Infrastructure

> **Repo:** `semops-publisher`
> **Owner:** This repo owns and operates these services
> **Status:** ACTIVE
> **Version:** 1.0.0
> **Last Updated:** 2026-02-06

## Overview

Publisher-pr has minimal infrastructure - primarily local ComfyUI for image generation. Most infrastructure needs (database, vector DB) are consumed from semops-core.

## Services

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| ComfyUI | 8188 | Image generation (SDXL, LoRAs) | On-demand |

## ComfyUI

Local GPU-based image generation using ComfyUI.

**Container:** `ike-comfyui`

**Location:** `comfyui/docker-compose.yml`

### Starting

```bash
cd 
docker compose up -d
```

### Stopping

```bash
docker compose down
```

### Volumes

| Path | Purpose |
|------|---------|
| `~/models/` | Centralized model storage (checkpoints, LoRAs, VAE) |
| `./workflows/` | ComfyUI workflow JSON files |
| `./inputs/` | Input images (ControlNet, img2img) |
| `./outputs/` | Generated output images |
| `comfyui_custom_nodes` | Custom nodes (Docker volume) |

### Model Storage

Models are stored centrally at `~/models/` per ADR-0006. ComfyUI expects:

```text
~/models/
├── checkpoints/ # Base models (SDXL, SD 1.5)
├── loras/ # LoRA models
├── controlnet/ # ControlNet models
├── vae/ # VAE models
├── clip/ # CLIP models
├── clip_vision/ # CLIP vision models
├── ipadapter/ # IP-Adapter models
└── upscale_models/ # Upscalers
```

### GPU Requirements

- NVIDIA GPU with CUDA support
- Docker with nvidia-container-toolkit
- Minimum 8GB VRAM for SDXL

## Consumed Services

Publisher-pr consumes infrastructure from other repos:

| Service | Source Repo | Port | Purpose |
|---------|-------------|------|---------|
| PostgreSQL | semops-core | 5432 | Knowledge base entities |
| Qdrant | semops-core | 6333 | Vector similarity search |
| MCP Server | semops-core | — | Agent KB access |

## Environment Variables

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-... # Claude API for agents
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
curl -s http://localhost:8188/system_stats

# Check GPU is visible
docker exec ike-comfyui nvidia-smi
```

## Cloud GPU (RunPod)

For heavy compute jobs, semops-publisher can offload to RunPod:

- AnimateDiff video generation
- Advanced ControlNet pipelines
- Batch image generation

**Setup:** Configure RunPod API key and endpoint in environment.

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - This repo's architecture
- [ADR-0004: ComfyUI for Image Generation](decisions/ADR-0004-COMFYUI-IMAGE-GENERATION.md)
- [ADR-0006: Model Storage Architecture](decisions/ADR-0006-model-storage-architecture.md)
- [GLOBAL_ARCHITECTURE.md](https://github.com/semops-ai/semops-dx-orchestrator/blob/main/docs/GLOBAL_ARCHITECTURE.md) - System landscape
