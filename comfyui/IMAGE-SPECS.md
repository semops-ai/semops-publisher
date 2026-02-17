# Image Specifications by Publishing Surface

## Quick Reference

| Surface | Image Type | Dimensions | Aspect Ratio | Format | Notes |
|---------|------------|------------|--------------|--------|-------|
| **WordPress** | Featured/Hero | 1200x630 | 1.91:1 | JPG/WebP | Social sharing optimized |
| **WordPress** | In-post | 1200xAuto | Flexible | JPG/WebP/PNG | Max width, height varies |
| **LinkedIn** | Post image | 1200x627 | 1.91:1 | JPG/PNG | Same as WordPress hero |
| **LinkedIn** | Article hero | 1280x720 | 16:9 | JPG/PNG | Larger for articles |
| **YouTube** | Thumbnail | 1280x720 | 16:9 | JPG/PNG | Max 2MB |
| **resumator** | Blog hero | 1200x630 | 1.91:1 | WebP | Optimized for Next.js |
| **resumator** | Inline | 800xAuto | Flexible | WebP | Smaller for perf |
| **Open Graph** | Social preview | 1200x630 | 1.91:1 | JPG | Facebook/Twitter/LinkedIn |

## ComfyUI Generation Settings

### Hero Images (1200x630)
```
Width: 1216  (closest SDXL-friendly to 1200)
Height: 640  (closest SDXL-friendly to 630)
```
SDXL prefers dimensions divisible by 64.

### 16:9 Images (1280x720)
```
Width: 1280
Height: 704  (closest SDXL-friendly to 720)
```

### Square (1:1)
```
Width: 1024
Height: 1024
```

## Post-Processing Pipeline

1. **Generate** at SDXL-friendly dimensions (divisible by 64)
2. **Resize** to exact target dimensions if needed
3. **Convert** to target format:
   - WebP for resumator (best compression)
   - JPG for social/WordPress (widest compatibility)
   - PNG only when transparency needed (diagrams)

## Format Guidelines

| Format | Use When | Quality Setting |
|--------|----------|-----------------|
| **WebP** | resumator, modern web | 85% quality |
| **JPG** | WordPress, social, email | 85% quality |
| **PNG** | Diagrams, transparency needed | N/A (lossless) |

## File Size Targets

| Surface | Max Size | Reason |
|---------|----------|--------|
| YouTube thumbnail | 2MB | Platform limit |
| WordPress | 500KB | Page speed |
| LinkedIn | 5MB | Platform limit |
| resumator | 200KB | Vercel/performance |

## Workflow

### Option 1: Generate at target size
Set ComfyUI dimensions to match target (using SDXL-friendly values).

### Option 2: Generate large, resize
1. Generate at 1024x1024 or larger
2. Use `convert` or Pillow to resize and format:
```bash
# Resize and convert to WebP
convert input.png -resize 1200x630 -quality 85 output.webp

# Resize and convert to JPG
convert input.png -resize 1200x630 -quality 85 output.jpg
```

### Option 3: Batch conversion script
```bash
# Convert all PNGs in outputs/ to WebP for resumator
for f in outputs/*.png; do
  convert "$f" -resize 1200x630 -quality 85 "${f%.png}.webp"
done
```

## Surface-Specific Notes

### WordPress (RankMath SEO)
- Featured image: Required for SEO
- Alt text: Include in frontmatter
- WebP with JPG fallback recommended

### LinkedIn
- Max 9 images per post
- First image most important (preview)
- Avoid text-heavy images (algorithm deprioritizes)

### YouTube
- Thumbnail is critical for CTR
- High contrast, readable text
- Face close-ups perform well

### resumator (Next.js)
- Use `<Image>` component (auto-optimization)
- Provide WebP, framework handles responsive
- Consider blur placeholder for hero images
