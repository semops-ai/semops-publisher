# ADR-0007: ComfyUI for Image Generation

> **Status:** Complete
> **Date:** 2025-12-05
> **Resolved:** 2025-12-06
> **Related Issue:** [](https://github.com/semops-ai/semops-publisher/issues/21) - Get comfy working
> **Builds On:** [PHASE1-MANUAL-FIRST](./PHASE1-MANUAL-FIRST.md)

---

## Executive Summary

Set up local ComfyUI with ControlNet for deterministic blog image generation. Uses RTX 4000 Ada (20GB VRAM) for SDXL-based workflows. Two modes: illustration style (80%) for concept explanation, photorealistic (20%) for situational imagery.

---

## Context

Blog posts need images for:
1. **Concept explanation** - Diagrams, illustrations showing AI/data concepts
2. **Situational/engaging** - Occasional photorealistic scenarios (goofy, attention-grabbing)

Requirements:
- **Determinism** - ControlNet for consistent composition from sketches/references
- **Local GPU** - RTX 4000 Ada available, avoid cloud costs
- **Reproducible** - Docker container, version-controlled workflows
- **Manual-first** - UI-based workflow, no automation yet

---

## Decision

### Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Runtime** | ComfyUI (Docker) | Node-based, flexible, good ControlNet support |
| **Base Model** | DreamShaper XL | Versatile (illustration + photorealistic), SDXL-based |
| **ControlNet** | Canny, Depth, MistoLine | Composition control from sketches |
| **Style Transfer** | IP-Adapter Plus | Reference image style matching |
| **GPU** | RTX 4000 Ada (20GB) | Local, sufficient VRAM for SDXL + ControlNets |

### Two Workflow Modes

**Mode 1: Illustration (Primary)**
- Input: Sketch (Excalidraw, paper, etc.)
- ControlNet: Canny or MistoLine
- LoRA: Flat illustration / vector style
- Output: Diagram-style image explaining concept

**Mode 2: Photorealistic (Secondary)**
- Input: Scene description, optional pose reference
- ControlNet: Depth, OpenPose (optional)
- IP-Adapter: Style from reference photo (optional)
- Output: Situational image (e.g., TED talk in pajamas)

---

## Implementation

### Directory Structure

```
comfyui/
 docker-compose.yml # GPU-enabled container
 download-models.sh # Model fetcher (~15GB)
 models/ # .safetensors (git-ignored)
 workflows/ # JSON workflows (version controlled)
 inputs/ # Reference images
 outputs/ # Generated images
```

### Models Included

| Category | Model | Size |
|----------|-------|------|
| Checkpoint | DreamShaper XL | ~6.5GB |
| ControlNet | Canny SDXL | ~2.5GB |
| ControlNet | Depth SDXL | ~2.5GB |
| ControlNet | MistoLine | ~2.5GB |
| IP-Adapter | Plus SDXL | ~1GB |
| CLIP Vision | ViT-H-14 | ~2GB |
| VAE | SDXL VAE | ~300MB |

### LoRAs (To Add)

Browse [civitai.com](https://civitai.com/models) for:
- Flat illustration SDXL
- Technical diagram style
- Vector art SDXL

Save to `models/loras/` as needed.

---

## Consequences

**Positive:**
- Local generation - no cloud API costs
- Deterministic output via ControlNet
- Reproducible via Docker + version-controlled workflows
- Flexible node-based editing

**Negative:**
- Manual workflow (no API automation yet)
- Requires GPU workstation
- Learning curve for ComfyUI node system

**Risks:**
- Model downloads are large (~15GB)
- VRAM limits if adding many ControlNets simultaneously

---

## Usage

```bash
# One-time setup
cd comfyui
./download-models.sh

# Start
docker compose up -d
open http://localhost:8188

# Stop
docker compose down
```

Output images → copy to `posts/<slug>/assets/` when ready.

---

## Future Considerations

- [ ] Save reusable workflows for common patterns
- [ ] Add OpenPose ControlNet for body positioning
- [ ] Explore Flux.1 when ControlNet support matures
- [ ] Consider API mode for batch generation (Phase 2+)

---

## Session Log

### 2025-12-05: Initial Setup
**Status:** In Progress

**Completed:**
- Created Docker Compose config with GPU passthrough
- Created model download script with starter models
- Created README with usage instructions
- Set up directory structure with .gitignore for large files
- Downloaded models: DreamShaper XL (6.5GB), ControlNets, IP-Adapter, VAE
- Added 7 LoRAs (Flat style, Minimalist icons, CollagePainting, C64XL, chatuxuan, Beautify-Supermodel, MoviePoster)
- Created IMAGE-SPECS.md with dimensions per publishing surface
- Created GitHub issue #18 for video generation (RunPod direction)
- Tried multiple Docker images (ai-dock, yanwk, zhangp365/comfyui)

### 2025-12-06: RESOLVED - Docker Desktop vs System Docker

**Root cause identified:** Docker Desktop was configured as default Docker socket, but NVIDIA Container Toolkit only integrates with system Docker.

**Fix:** Use system Docker socket explicitly:
```bash
DOCKER_HOST=unix:///var/run/docker.sock docker compose up -d
```

**Result:** ComfyUI container running with GPU access at http://localhost:8188

**Updated:** README.md with troubleshooting section for Docker Desktop users

---

## References

- [comfyui/README.md](../../comfyui/README.md) - Usage documentation
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)
- [CivitAI Models](https://civitai.com/models) - LoRA source

---

**End of Document**
