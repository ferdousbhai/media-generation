#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
#     "pillow>=10.0.0",
# ]
# ///
"""
Nano Banana Pro - Image generation and editing using Google's Gemini 3 Pro Image API.

Supports:
- Text-to-image generation
- Image-to-image editing
- Resolution options: 1K, 2K, 4K
"""

import argparse
import base64
import mimetypes
import os
import sys
from pathlib import Path


def get_mime_type(file_path: str) -> str:
    """Determine MIME type from file extension."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # Default to PNG for unknown types
        return "image/png"
    return mime_type


def load_image_as_base64(file_path: str) -> tuple[str, str]:
    """Load an image file and return (base64_data, mime_type)."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Input image not found: {file_path}")

    with open(path, "rb") as f:
        image_data = f.read()

    base64_data = base64.standard_b64encode(image_data).decode("utf-8")
    mime_type = get_mime_type(file_path)

    return base64_data, mime_type


def generate_image(
    prompt: str,
    output_path: str,
    resolution: str = "1K",
    input_image_path: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    Generate or edit an image using Gemini 3 Pro Image API.

    Args:
        prompt: Text description or editing instructions
        output_path: Where to save the generated image
        resolution: Image resolution (1K, 2K, or 4K)
        input_image_path: Optional path to input image for editing
        api_key: Optional API key (falls back to GEMINI_API_KEY env var)

    Returns:
        Full path to the saved image
    """
    # Import here to allow script metadata parsing without dependencies
    from google import genai
    from google.genai import types

    # Resolve API key
    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not resolved_api_key:
        print("Error: No API key provided.", file=sys.stderr)
        print("Set GEMINI_API_KEY environment variable or use --api-key argument.", file=sys.stderr)
        sys.exit(1)

    # Validate resolution
    valid_resolutions = {"1K", "2K", "4K"}
    if resolution not in valid_resolutions:
        print(f"Error: Invalid resolution '{resolution}'. Must be one of: {valid_resolutions}", file=sys.stderr)
        sys.exit(1)

    # Initialize client
    client = genai.Client(api_key=resolved_api_key)

    # Build content parts
    contents = []

    # If editing an existing image, include it first
    if input_image_path:
        base64_data, mime_type = load_image_as_base64(input_image_path)
        contents.append(
            types.Part.from_bytes(
                data=base64.standard_b64decode(base64_data),
                mime_type=mime_type,
            )
        )

    # Add the text prompt
    contents.append(prompt)

    # Configure generation
    config = types.GenerateContentConfig(
        response_modalities=["IMAGE"],
        image_config=types.ImageConfig(
            image_size=resolution,
        ),
    )

    # Generate
    model = "gemini-3-pro-image-preview"

    try:
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract and save the image
    output_file = Path(output_path)

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data is not None:
            image_data = part.inline_data.data
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_bytes(image_data)
            full_path = str(output_file.resolve())
            print(f"Image saved: {full_path}")
            return full_path

    # No image in response
    print("Error: No image was generated in the response.", file=sys.stderr)
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                print(f"Model response: {part.text}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit images using Gemini 3 Pro Image API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a new image
  %(prog)s --prompt "A serene Japanese garden" --filename "garden.png"

  # Edit an existing image
  %(prog)s --prompt "Add storm clouds to the sky" --filename "edited.png" --input-image "photo.jpg"

  # Generate at 4K resolution
  %(prog)s --prompt "Mountain landscape" --filename "mountains.png" --resolution 4K
        """,
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="Text description for generation or editing instructions",
    )
    parser.add_argument(
        "--filename",
        required=True,
        help="Output filename (saved to current directory unless path specified)",
    )
    parser.add_argument(
        "--resolution",
        choices=["1K", "2K", "4K"],
        default="1K",
        help="Image resolution (default: 1K)",
    )
    parser.add_argument(
        "--input-image",
        help="Path to input image for editing (optional)",
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY env var)",
    )

    args = parser.parse_args()

    generate_image(
        prompt=args.prompt,
        output_path=args.filename,
        resolution=args.resolution,
        input_image_path=args.input_image,
        api_key=args.api_key,
    )


if __name__ == "__main__":
    main()
