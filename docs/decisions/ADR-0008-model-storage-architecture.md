# ADR-0008: Model Storage Architecture

> **Status:** Complete
> **Date:** 2025-12-07
> **Related Issue:** 

## Executive Summary

Store all ComfyUI models at `~/models` using ComfyUI's native flat structure. Mount directly into containers. Track model family via filename convention.

## Context

### The Problem We Hit

When setting up ComfyUI, we encountered a Docker volume mounting issue:

1. **What we did:** Mounted `./models:/root/ComfyUI/models`
2. **What happened:** The container image (`zhangp365/comfyui`) internally uses symlinks pointing to `/data/*`
3. **Result:** ComfyUI couldn't find models because symlinks pointed to non-existent paths

**The fix:**
```yaml
volumes:
 - ~/models:/data # Mount to where ComfyUI's symlinks point
```

### Why `~/models`

- `/media` is a dedicated data drive (not removable media)
- Keeps large model files off the OS drive
- Single location for all ML models (ComfyUI, Ollama, embeddings)

## Decision

Use ComfyUI's native flat directory structure directly:

```
~/models/
├── checkpoints/ # ComfyUI - Base models (SDXL, SD 1.5, etc.)
├── loras/ # ComfyUI - LoRA models
├── controlnet/ # ComfyUI - ControlNet models
├── vae/ # ComfyUI - VAE models
├── clip/ # ComfyUI - CLIP models
├── clip_vision/ # ComfyUI - CLIP vision models
├── ipadapter/ # ComfyUI - IP-Adapter models
├── upscale_models/ # ComfyUI - Upscalers (Real-ESRGAN, etc.)
├── configs/ # ComfyUI - Model configs
├── ollama/ # Ollama - LLM models (symlinked from ~/.ollama/models)
├── embeddings/ # Shared - Text embeddings (BGE, etc.)
└── gguf/ # Local LLMs - GGUF format models
```

### Naming Convention

Track model family in filename to prevent compatibility mistakes:

```
checkpoints/
├── dreamshaper_xl_v2.1.safetensors # SDXL (xl = SDXL)
├── realistic_vision_sd15_v5.safetensors # SD 1.5 (sd15 = SD 1.5)
└── animatediff_sdxl_beta.safetensors # AnimateDiff SDXL

loras/
├── detail_slider_sdxl.safetensors # SDXL LoRA
└── film_grain_sd15.safetensors # SD 1.5 LoRA
```

**Why this matters:** SDXL LoRAs don't work with SD 1.5 checkpoints (tensor shape mismatch). The filename makes it obvious which family each model belongs to.

### Docker Compose

```yaml
services:
 comfyui:
 image: zhangp365/comfyui:latest
 volumes:
 - ~/models:/data # Models
 - ./workflows:/app/user/default/workflows
 - ./inputs:/app/input
 - ./outputs:/app/output
 deploy:
 resources:
 reservations:
 devices:
 - driver: nvidia
 count: 1
 capabilities: [gpu]
```

## Implementation

```bash
# Create directory structure
sudo mkdir -p ~/models
sudo chown $USER:$USER ~/models

# Move existing ComfyUI models from project directory
mv ~/models/

# Fix any root-owned directories
sudo chown -R $USER:$USER ~/models

# Symlink Ollama models to centralized storage
# (Ollama stores models at ~/.ollama/models by default)
mkdir -p ~/models/ollama
mv ~/.ollama/models/* ~/models/ollama/ 2>/dev/null || true
rm -rf ~/.ollama/models
ln -s ~/models/ollama ~/.ollama/models
```

## Future Considerations

If/when we need more sophisticated model management:

- **RunPod:** Use persistent volume with same structure, `startup.sh` to provision
- **Model manifest:** `models.yaml` listing required models per environment
- **HuggingFace:** Registry for custom-trained LoRAs/embeddings
- **Training:** Add `datasets/` and `trained/` directories as needed

For now, keep it simple. A handful of local models doesn't need enterprise MLOps.

## Consequences

### Positive

- **Simple:** Just move files to `~/models`, done
- **ComfyUI-native:** No symlinks, no translation layers
- **Single backup target:** Just backup `~/models`
- **Filename convention:** Prevents family compatibility mistakes

### Negative

- **Manual tracking:** No automated provenance or version control
- **No manifest:** Must manually remember which models are needed

### Risks

| Risk | Mitigation |
|------|------------|
| Disk space | `/media` is dedicated data drive |
| Family mismatch | Use naming convention with family suffix |
| Model loss | Backup `~/models`, re-download from HuggingFace/CivitAI |

## Docker Volume Rules (Reference)

1. **Know the container's internal paths** - Read Dockerfile or check with `docker exec`
2. **Mount to where the app expects models** - Not where you think they should go
3. **Watch for UID/GID mismatches** - Container user vs host file ownership

## Session Log

### 2025-12-07

- Initial draft documenting ComfyUI volume issue
- Simplified from over-engineered family-first architecture to pragmatic flat structure
- Decision: Use ComfyUI's native structure, track family via filename
