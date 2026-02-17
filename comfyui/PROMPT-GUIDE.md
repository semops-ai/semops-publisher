# ComfyUI Prompt Guide for Blog Images

Quick reference for generating blog images with DreamShaper XL Turbo.

## TL;DR - Copy-Paste Templates

### Hero Image (Abstract/Gradient)
```
abstract digital art representing [TOPIC],
flowing gradient shapes, particle effects,
modern tech aesthetic, purple to blue gradient background,
glowing accents, cinematic lighting
```

### Flat Vector Illustration
```
flat vector illustration of [TOPIC],
[SPECIFIC ELEMENTS],
minimalist design, clean lines, solid colors,
[COLOR] color palette, white background,
no gradients, simple shapes
```

### Isometric 3D Style
```
isometric 3D illustration of [TOPIC],
[SPECIFIC ELEMENTS],
tech illustration style, clean geometric shapes,
blue and purple color scheme, soft shadows
```

### Neural/AI Visualization
```
artistic visualization of [AI CONCEPT],
abstract brain made of interconnected nodes and pathways,
glowing synapses, data particles flowing through layers,
dark background with blue and purple bioluminescent glow
```

### Editorial Photo
```
editorial photograph of [SCENE],
[SPECIFIC DETAILS],
natural window lighting, shallow depth of field,
professional business photography, candid moment
```

---

## Style Keywords That Work

| Style | Key Phrases | Best For |
|-------|-------------|----------|
| **Flat Vector** | "flat vector illustration", "minimalist design", "clean lines", "solid colors", "no gradients" | Diagrams, simple concepts |
| **Isometric** | "isometric 3D illustration", "clean geometric shapes", "soft shadows" | Architecture, infrastructure |
| **Gradient Abstract** | "abstract digital art", "flowing gradient shapes", "particle effects", "glowing accents" | Hero images, AI topics |
| **Line Art** | "technical line art", "blueprint style", "white lines on dark background" | Technical diagrams |
| **Editorial Photo** | "editorial photograph", "natural lighting", "shallow depth of field", "candid" | Team/workplace scenes |

## Color Palettes

| Palette | Prompt Addition | Use Case |
|---------|-----------------|----------|
| **Tech Blue** | "blue and teal color palette" | Cloud, data, infrastructure |
| **AI Purple** | "purple to blue gradient, glowing cyan accents" | ML, AI, neural networks |
| **Warm Tech** | "teal and orange accents" | Data engineering, pipelines |
| **Clean White** | "white background, pastel colors" | Diagrams, simple illustrations |
| **Dark Mode** | "dark background with glowing elements" | Hero images, dramatic effect |

## Negative Prompt (Use This)

```
blurry, low quality, distorted, deformed, ugly, bad anatomy, text, watermark, signature
```

For illustrations add: `photorealistic, photograph, 3d render, grainy`

## Dimensions

| Use Case | Width | Height | Notes |
|----------|-------|--------|-------|
| **Blog Hero** | 1216 | 640 | 1.91:1 ratio for WordPress/LinkedIn |
| **YouTube Thumb** | 1280 | 704 | 16:9 ratio |
| **Square** | 1024 | 1024 | Instagram, general use |

SDXL works best with dimensions divisible by 64.

## Topic-Specific Templates

### Data Engineering
```
modern tech illustration of data engineering pipeline,
stylized database icons connected by flowing data streams,
ETL process visualization, clean vector style,
professional infographic aesthetic, teal and orange accents
```

### Machine Learning
```
artistic visualization of a neural network learning,
abstract brain made of interconnected nodes and pathways,
glowing synapses, data particles flowing through layers,
dark background with blue and purple bioluminescent glow
```

### Cloud Architecture
```
isometric illustration of cloud infrastructure,
stylized servers, containers, and microservices,
kubernetes pods floating in cloud environment,
modern flat design, pastel colors, clean white background
```

### Knowledge Graph
```
abstract visualization of a knowledge graph,
interconnected nodes representing concepts and relationships,
constellation-like network pattern,
dark space background, glowing cyan connections,
professional data visualization aesthetic
```

### AI Automation
```
conceptual illustration of AI automation in business,
robot arm and human hand working together on digital interface,
holographic displays showing charts and workflows,
futuristic but approachable, warm lighting
```

## What Doesn't Work Well

1. **Text in images** - SD generates gibberish text. Plan to add text in post-processing.
2. **Specific logos** - Won't render real company logos accurately.
3. **Complex diagrams with labels** - Use for visual impact, not information.
4. **Hands** - Still sometimes weird, especially in close-ups.

## Generation Settings

| Setting | Value | Notes |
|---------|-------|-------|
| **Steps** | 25 | Good balance of quality/speed |
| **CFG** | 7.0 | Standard, increase for more prompt adherence |
| **Sampler** | euler | Fast, good quality |
| **Scheduler** | normal | Default works well |

## Workflow

1. Pick a template above
2. Replace bracketed placeholders with your specifics
3. Generate at 1216x640 for hero images
4. Review, regenerate with different seed if needed
5. Post-process: crop, add text overlays, convert to WebP

## Quick Generator Script

Use `comfyui/generate.py` for quick generation:

```bash
# Generate a hero image
python comfyui/generate.py "data pipeline" --style gradient_abstract

# Generate flat illustration
python comfyui/generate.py "cloud computing" --style flat_vector

# Custom prompt
python comfyui/generate.py --prompt "your full prompt here"
```
