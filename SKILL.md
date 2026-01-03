---
name: media-generation
description: Generate images, videos, and audio using Google's Gemini APIs. Use for image generation/editing (Gemini 3 Pro Image), video generation (Veo 3), and speech (TBD). Trigger words - images: generate, create, draw, design, make, edit, modify image/picture. Video: generate video, create video, animate, make a video. Supports text-to-image, image-to-image editing, text-to-video, and image-to-video.
---

# Media Generation

## Image Generation

```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_image.py \
  --prompt "description or editing instructions" \
  --filename "output.png" \
  [--input-image "source.png"] \
  [--resolution 1K|2K|4K]
```

### Resolution
- `1K` (default) — also for: "low res", "1080p"
- `2K` — also for: "medium", "2048"
- `4K` — also for: "high res", "hi-res", "ultra"

## Video Generation

```bash
uv run ~/.claude/skills/nano-banana-pro/scripts/generate_video.py \
  --prompt "video description" \
  --filename "output.mp4" \
  [--model veo-3.0-generate-preview] \
  [--negative "things to avoid"] \
  [--input-image "first-frame.png"]
```

### Models
- `veo-3.0-generate-preview` (default) — standard quality
- `veo-3.0-fast-generate-preview` — faster, lower cost
- `veo-3.1-generate-preview` — best for dialogue/speech in video
- `veo-3.1-fast-generate-preview` — fast with audio

### Prompting Tips
- Use quotes for dialogue: `'She says "Hello!"'`
- Describe sounds explicitly: `"thunder rumbling, rain pattering"`
- Specify camera movements: `"slow pan", "close-up", "wide shot"`

**Note:** Veo requires paid tier. ~$0.40/sec standard, ~$0.15/sec fast.

## Audio Generation

- **Music:** Use Suno (external service)
- **Speech:** Gemini 2.5 TTS (Flash or Pro) - TBD script

## API Key

Uses `GEMINI_API_KEY` env var, or pass `--api-key KEY`.
