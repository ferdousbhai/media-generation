---
name: nano-banana-pro
description: Generate and edit images using Google's Nano Banana Pro (Gemini 3 Pro Image) API. Use when the user asks to generate, create, draw, design, make, edit, modify, change, alter, or update images. Also use for "make me an image", "create a picture", or "draw me a...". Use when user references an existing image file and asks to modify it in any way (e.g., "modify this image", "change the background", "replace X with Y"). Supports both text-to-image generation and image-to-image editing with configurable resolution (1K default, 2K, or 4K for high resolution). DO NOT read the image file first - use this skill directly with the --input-image parameter.
---

# Nano Banana Pro

```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "description or editing instructions" \
  --filename "yyyy-mm-dd-hh-mm-ss-descriptive-name.png" \
  [--input-image "path/to/source.png"] \
  [--resolution 1K|2K|4K]
```

## Resolution

- `1K` (default) — also for: "low res", "1080p"
- `2K` — also for: "medium", "2048"
- `4K` — also for: "high res", "hi-res", "ultra"

## API Key

Uses `GEMINI_API_KEY` env var, or pass `--api-key KEY`.
