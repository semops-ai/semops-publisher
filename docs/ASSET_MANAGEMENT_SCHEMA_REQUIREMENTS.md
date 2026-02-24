# Asset Management Requirements for Project Ike Schema Integration

## Overview

As we develop the asset management features in blog-geratror, we need to capture requirements that will inform the Surface/Delivery schema design in Project Ike. This document tracks the specific patterns and requirements we discover.

## Current Asset Management Patterns

### Multi-Format Generation
- **Input**: Single source image (e.g., `post-slug_header.jpg`)
- **Output**: Platform-optimized variants
 - WordPress: 1200x630, webp format, responsive breakpoints
 - LinkedIn: 1200x627, jpg format, high compression 
 - GitHub: 800x400, png format, markdown-friendly

### Naming Convention
```
post-slug_purpose.ext
├── ai-adoption-challenges_header.jpg
├── enterprise-automation_diagram.png 
└── data-strategy_screenshot.png
```

## Schema Requirements to Capture

### 1. Asset Transformation Tracking
- [ ] Original asset → Generated variants lineage
- [ ] Transformation metadata (resize, format conversion, optimization)
- [ ] Success/failure status for each transformation

### 2. Platform Constraints 
- [ ] File size limits per platform
- [ ] Supported formats per platform
- [ ] Dimension requirements/recommendations
- [ ] CDN integration needs

### 3. Delivery Status Management
- [ ] Queued → Processing → Published → Failed states
- [ ] Retry logic for failed deliveries
- [ ] Batch processing coordination

### 4. Approval Workflows
- [ ] Which asset types need human review
- [ ] GitHub issue integration for asset approval
- [ ] Version control for asset iterations

### 5. Metadata Schema Examples

**Original Asset Item:**
```json
{
 "type": "source_image_v1",
 "version": 1,
 "original_filename": "header.jpg",
 "dimensions": "1920x1080", 
 "file_size_bytes": 245760,
 "color_profile": "sRGB",
 "creation_tool": "canva"
}
```

**Delivery Metadata:**
```json
{
 "type": "image_delivery_v1", 
 "version": 1,
 "target_format": "webp",
 "target_dimensions": "1200x630",
 "compression_quality": 85,
 "cdn_url": "https://cdn.example.com/optimized/...",
 "processing_time_ms": 1240,
 "file_size_reduction_pct": 67
}
```

## Action Items

- [ ] **Phase 1**: Implement basic asset processing with metadata capture
- [ ] **Phase 2**: Test schema patterns against real workflow data 
- [ ] **Phase 3**: Refine Surface/Delivery schema based on learnings
- [ ] **Phase 4**: Integrate with Project Ike schema implementation

## Success Criteria

1. All asset transformations are tracked with full lineage
2. Platform-specific delivery requirements are captured as constraints
3. Asset approval workflows integrate cleanly with GitHub issues
4. Schema patterns are proven with real multi-format publishing

## Related

- Project Ike DDD Schema: `../project-ike/examples/DDD_arch.md`
- Current Image Processor: `utils/image_processor.py`
- Asset Workflow: `orchestrator.py` (Phase 4)