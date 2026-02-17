# ComfyUI Image Generation

Local ComfyUI setup for blog image generation using your RTX 4000 Ada (20GB VRAM).

## Quick Start

```bash
# 1. Download models (~15GB, one-time)
./download-models.sh

# 2. Start ComfyUI
docker compose up -d

# 3. Open browser
open http://localhost:8188

# 4. Stop when done
docker compose down
```

## Directory Structure

```
comfyui/
  docker-compose.yml    # Container config with GPU passthrough
  download-models.sh    # Model downloader script
  workflows/            # Saved workflow JSONs (version controlled)
  inputs/               # Reference images for ControlNet/IP-Adapter
  outputs/              # Generated images

~/models/               # Centralized model storage (per ADR-0006)
  checkpoints/          # Base models (SDXL, etc.)
  controlnet/           # ControlNet models
  loras/                # Style LoRAs
  vae/                  # VAE models
  clip_vision/          # CLIP for IP-Adapter
  ipadapter/            # IP-Adapter models
```

**Note:** Models are stored at `~/models/` and mounted into the container at `/data`. See [ADR-0006](../docs/decisions/ADR-0006-model-storage-architecture.md) for details.

## Installed Models

### Base Model
- **DreamShaper XL** - Versatile, good for both illustration and photorealistic

### ControlNet (Determinism)
| Model | Use Case |
|-------|----------|
| **Canny** | Edge detection - maintain composition from sketch |
| **Depth** | 3D structure - consistent spatial layout |
| **MistoLine** | Lineart - sketch → rendered illustration |

### IP-Adapter (Style Transfer)
- **IP-Adapter Plus SDXL** - Transfer style from reference images

### VAE
- **SDXL VAE** - Improved colors and details

## Two Workflows

### 1. Illustration Mode (80% of use)
For explaining AI/data concepts with diagram-style visuals.

**Typical pipeline:**
1. Sketch concept in Excalidraw or on paper
2. Use **Canny** or **MistoLine** ControlNet to maintain composition
3. Apply illustration-style LoRA
4. Generate with DreamShaper XL

**Recommended LoRAs to add:**
- Flat illustration style
- Vector art style
- Technical diagram style

Browse [civitai.com](https://civitai.com/models) and filter by SDXL + your style keywords.

### 2. Photorealistic Mode (20% of use)
For situational/goofy scenarios (e.g., "giving a TED talk in pajamas").

**Typical pipeline:**
1. Use **OpenPose** ControlNet for body positioning (optional)
2. Use **Depth** ControlNet for scene structure
3. Generate with DreamShaper XL (it handles photorealistic well)
4. Optionally use **IP-Adapter** to transfer style from a reference photo

## First Run Setup

After `docker compose up -d`:

1. Open http://localhost:8188
2. Install **ComfyUI Manager** for easy custom node installation:
   - Click "Manager" in the menu
   - Or manually: the container may auto-install it
3. Install required custom nodes via Manager:
   - ComfyUI-ControlNet-Preprocessors
   - ComfyUI_IPAdapter_plus

## Adding New LoRAs

1. Download `.safetensors` from civitai.com
2. Save to `~/models/loras/` (use naming convention: `style_name_sdxl.safetensors`)
3. Restart ComfyUI or use "Refresh" in the UI
4. Use "Load LoRA" node in your workflow

## Saving Workflows

1. Create your workflow in ComfyUI
2. Save via UI: Workflow → Save
3. Default saves to `workflows/` (mounted volume)
4. Commit useful workflows to git for reuse

## GPU Memory Tips

Your RTX 4000 Ada (20GB) can handle:
- SDXL base + 1-2 ControlNets comfortably
- Add `--lowvram` to CLI_ARGS in docker-compose.yml if issues

## Image Specifications

See [IMAGE-SPECS.md](./IMAGE-SPECS.md) for dimensions, formats, and sizing per publishing surface.

Quick reference:
| Surface | Dimensions | Format |
|---------|------------|--------|
| WordPress/LinkedIn hero | 1200x630 | JPG/WebP |
| YouTube thumbnail | 1280x720 | JPG |
| resumator | 1200x630 | WebP |

## Outputs

Generated images land in `outputs/`. When ready for a blog post:

```bash
# Copy to post assets
cp outputs/my-image.png ../posts/my-post-slug/assets/
```

## Troubleshooting

### Docker Desktop vs System Docker

If using Docker Desktop alongside system Docker, you may need to specify the system socket:

```bash
# Use system Docker (has NVIDIA runtime configured)
DOCKER_HOST=unix:///var/run/docker.sock docker compose up -d

# Or add to ~/.bashrc for this directory:
export DOCKER_HOST=unix:///var/run/docker.sock
```

The NVIDIA Container Toolkit only integrates with system Docker, not Docker Desktop.

### Container won't start
```bash
# Check GPU access
nvidia-smi

# Check Docker GPU support
DOCKER_HOST=unix:///var/run/docker.sock docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Out of memory
Edit `docker-compose.yml`:
```yaml
environment:
  - CLI_ARGS=--listen 0.0.0.0 --lowvram
```

### Models not showing
- Check files are in correct subdirectory under `~/models/`
- Click "Refresh" in ComfyUI UI
- Restart container: `docker compose restart`

### Port 8188 already in use (sticky ports)

Docker can leave orphan `docker-proxy` processes holding ports after containers are removed:

```bash
# Find what's using the port
sudo lsof -i :8188

# Kill stale docker-proxy processes
sudo pkill -f "docker-proxy.*8188"

# Or kill by PID from lsof output
sudo kill <PID>
```

### NVIDIA GPU not available in container

If you see `could not select device driver "nvidia"`:

```bash
# Configure NVIDIA runtime for Docker
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker daemon (required after runtime config)
sudo systemctl restart docker

# Verify
docker info | grep -i nvidia
```

**Important:** After any Docker issues, restart the full daemon, not just the container:

```bash
sudo systemctl restart docker
```
