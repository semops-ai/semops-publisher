#!/bin/bash
# Download models for ComfyUI
# Run this once after first setup
#
# Requires: wget or curl, ~15GB disk space
# Models are downloaded to ./models/ subdirectories

set -e

MODELS_DIR="$(dirname "$0")/models"
mkdir -p "$MODELS_DIR"/{checkpoints,controlnet,loras,clip,vae,clip_vision,ipadapter}

echo "=== ComfyUI Model Downloader ==="
echo "Target: $MODELS_DIR"
echo ""

# Helper function
download {
 local url="$1"
 local dest="$2"
 if [ -f "$dest" ]; then
 echo " [skip] $(basename "$dest") already exists"
 else
 echo " [download] $(basename "$dest")"
 wget -q --show-progress -O "$dest" "$url"
 fi
}

# =============================================================================
# BASE MODELS (pick one to start)
# =============================================================================

echo ""
echo "--- Base Checkpoints ---"

# SDXL 1.0 Base - High quality, good ControlNet support (~6.5GB)
# Uncomment to download:
# download "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors" \
# "$MODELS_DIR/checkpoints/sd_xl_base_1.0.safetensors"

# DreamShaper XL - Good for both illustration and photorealistic (~6.5GB)
# Popular for versatility
download "https://civitai.com/api/download/models/351306?type=Model&format=SafeTensor&size=full&fp=fp16" \
 "$MODELS_DIR/checkpoints/dreamshaper_xl.safetensors"

# =============================================================================
# CONTROLNET MODELS (SDXL versions)
# =============================================================================

echo ""
echo "--- ControlNet Models ---"

# Canny - Edge detection for composition control (~2.5GB each)
download "https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.fp16.safetensors" \
 "$MODELS_DIR/controlnet/controlnet-canny-sdxl-1.0.safetensors"

# Depth - 3D structure preservation
download "https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.fp16.safetensors" \
 "$MODELS_DIR/controlnet/controlnet-depth-sdxl-1.0.safetensors"

# Lineart - For illustration workflows (sketch → render)
# Uses mistoline which works well for both detailed and simple lines
download "https://huggingface.co/TheMistoAI/MistoLine/resolve/main/mistoLine_fp16.safetensors" \
 "$MODELS_DIR/controlnet/mistoLine_fp16.safetensors"

# =============================================================================
# IP-ADAPTER (Style transfer from reference images)
# =============================================================================

echo ""
echo "--- IP-Adapter ---"

# IP-Adapter Plus for SDXL - Better style/composition transfer
download "https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors" \
 "$MODELS_DIR/ipadapter/ip-adapter-plus_sdxl_vit-h.safetensors"

# CLIP Vision model (required for IP-Adapter)
download "https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" \
 "$MODELS_DIR/clip_vision/CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"

# =============================================================================
# LORAS (Style modifiers)
# =============================================================================

echo ""
echo "--- LoRAs ---"

# Flat illustration style - good for diagrams/explainers
# Note: You'll want to find specific LoRAs that match your style
# These are placeholders - browse civitai.com for ones you like

echo " [info] LoRAs are style-specific. Browse civitai.com/models for:"
echo " - 'flat illustration sdxl'"
echo " - 'technical diagram'"
echo " - 'vector art sdxl'"
echo " Download .safetensors files to: $MODELS_DIR/loras/"

# =============================================================================
# VAE (improves color/detail)
# =============================================================================

echo ""
echo "--- VAE ---"

# SDXL VAE fix - better colors
download "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors" \
 "$MODELS_DIR/vae/sdxl_vae.safetensors"

# =============================================================================
# SUMMARY
# =============================================================================

echo ""
echo "=== Download Complete ==="
echo ""
echo "Models downloaded to: $MODELS_DIR"
echo ""
echo "Directory structure:"
find "$MODELS_DIR" -type f -name "*.safetensors" | while read f; do
 size=$(du -h "$f" | cut -f1)
 echo " $size $(basename "$f")"
done
echo ""
echo "Next steps:"
echo " 1. cd comfyui && docker compose up -d"
echo " 2. Open http://localhost:8188"
echo " 3. Install ComfyUI Manager (first run) for easy node installation"
echo ""
