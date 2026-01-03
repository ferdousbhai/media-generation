#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
# ]
# ///
"""
Video generation using Google's Veo 3 API.

Supports:
- Text-to-video generation
- Image-to-video generation
- Multiple durations and resolutions
"""

import argparse
import os
import sys
import time
from pathlib import Path


def generate_video(
    prompt: str,
    output_path: str,
    model: str = "veo-3.0-generate-001",  # Stable production model
    negative_prompt: str | None = None,
    input_image_path: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    Generate a video using Veo 3 API.

    Args:
        prompt: Text description for video generation
        output_path: Where to save the generated video
        model: Veo model to use (veo-3.0-generate-preview, veo-3.1-generate-preview, etc.)
        negative_prompt: Things to avoid in the video
        input_image_path: Optional path to input image for image-to-video
        api_key: Optional API key (falls back to GEMINI_API_KEY env var)

    Returns:
        Full path to the saved video
    """
    from google import genai
    from google.genai import types

    # Resolve API key
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Set GEMINI_API_KEY environment variable or use --api-key argument.", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=resolved_api_key)

    # Build config
    config_kwargs = {}
    if negative_prompt:
        config_kwargs["negative_prompt"] = negative_prompt

    config = types.GenerateVideosConfig(**config_kwargs) if config_kwargs else None

    # Handle image-to-video
    image = None
    if input_image_path:
        path = Path(input_image_path)
        if not path.exists():
            print(f"Error: Input image not found: {input_image_path}", file=sys.stderr)
            sys.exit(1)

        # Load image as Image type for Veo
        print(f"Loading input image: {input_image_path}")
        import base64
        import mimetypes
        mime_type, _ = mimetypes.guess_type(input_image_path)
        mime_type = mime_type or "image/jpeg"
        with open(path, "rb") as f:
            image_data = f.read()
        image = types.Image(image_bytes=image_data, mime_type=mime_type)

    # Start video generation
    print(f"Starting video generation with model: {model}")
    print(f"Prompt: {prompt}")
    if negative_prompt:
        print(f"Negative prompt: {negative_prompt}")

    try:
        if image:
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt,
                image=image,
                config=config,
            )
        else:
            operation = client.models.generate_videos(
                model=model,
                prompt=prompt,
                config=config,
            )
    except Exception as e:
        print(f"Error starting video generation: {e}", file=sys.stderr)
        sys.exit(1)

    # Poll for completion
    print("Generating video (this may take a few minutes)...")
    poll_count = 0
    while not operation.done:
        poll_count += 1
        print(f"  Waiting... ({poll_count * 20}s elapsed)")
        time.sleep(20)
        try:
            operation = client.operations.get(operation)
        except Exception as e:
            print(f"Error checking operation status: {e}", file=sys.stderr)
            sys.exit(1)

    # Check for errors
    if operation.error:
        print(f"Error generating video: {operation.error}", file=sys.stderr)
        sys.exit(1)

    # Download and save the video
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        generated_video = operation.result.generated_videos[0]
        client.files.download(file=generated_video.video)
        generated_video.video.save(str(output_file))
        full_path = str(output_file.resolve())
        print(f"Video saved: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error saving video: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate videos using Google's Veo 3 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a video from text
  %(prog)s --prompt "A golden retriever playing in a field of sunflowers" --filename "dog.mp4"

  # Generate with negative prompt
  %(prog)s --prompt "Ocean waves at sunset" --filename "ocean.mp4" --negative "people, boats"

  # Image-to-video
  %(prog)s --prompt "The cat slowly wakes up and stretches" --filename "cat.mp4" --input-image "cat.jpg"

  # Use Veo 3.1 for dialogue/sound
  %(prog)s --prompt "A person says 'Hello world!'" --filename "hello.mp4" --model veo-3.1-generate-preview

Models:
  veo-3.0-generate-001       - Standard Veo 3 (default)
  veo-3.0-fast-generate-001  - Faster, lower cost
  veo-3.1-generate-preview   - Latest with improved audio
  veo-3.1-fast-generate-preview - Fast Veo 3.1

Note: Veo models require a paid tier Gemini API key.
Cost: ~$0.40/sec (standard) or ~$0.15/sec (fast)
        """,
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="Text description for video generation",
    )
    parser.add_argument(
        "--filename",
        required=True,
        help="Output filename (saved to current directory unless path specified)",
    )
    parser.add_argument(
        "--model",
        default="veo-3.0-generate-001",
        help="Veo model to use (default: veo-3.0-generate-001)",
    )
    parser.add_argument(
        "--negative",
        dest="negative_prompt",
        help="Things to avoid in the video",
    )
    parser.add_argument(
        "--input-image",
        help="Path to input image for image-to-video generation",
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY env var)",
    )

    args = parser.parse_args()

    generate_video(
        prompt=args.prompt,
        output_path=args.filename,
        model=args.model,
        negative_prompt=args.negative_prompt,
        input_image_path=args.input_image,
        api_key=args.api_key,
    )


if __name__ == "__main__":
    main()
