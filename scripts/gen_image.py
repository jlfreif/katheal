#!/usr/bin/env python3
"""
Generate images for storybook pages using various AI models.

Usage:
    uv run scripts/gen_image.py <model-backend> <page-path>

Model Backends:
    openai      - OpenAI DALL-E 3 (1792x1024, ~2:1 aspect ratio)
    replicate   - Replicate IPAdapter Style SDXL (1536x768, 2:1 aspect ratio)
                  Uses images/cu-01-openai.jpg as style reference
    ideogram    - Ideogram v3 (3:1 aspect ratio)
    prompt      - Display prompt without generating image (testing)

Examples:
    uv run scripts/gen_image.py openai pages/cu-01.yaml
    uv run scripts/gen_image.py replicate pages/em-05.yaml
    uv run scripts/gen_image.py ideogram pages/ha-12.yaml
    uv run scripts/gen_image.py prompt pages/cu-ha-02.yaml
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Model backend configurations
BACKENDS = {
    "openai": {
        "name": "OpenAI DALL-E 3",
        "env_vars": ["OPENAI_API_KEY"],
    },
    "replicate": {
        "name": "Replicate IPAdapter Style SDXL",
        "env_vars": ["REPLICATE_API_TOKEN"],
    },
    "ideogram": {
        "name": "Ideogram v3",
        "env_vars": ["IDEOGRAM_API_KEY", "IDEOGRAM_API_URL"],
    },
    "prompt": {
        "name": "Prompt Only (Testing)",
        "env_vars": [],
    },
}


def print_help():
    """Print help message."""
    print(__doc__)
    print("\nAvailable Model Backends:")
    for backend, config in BACKENDS.items():
        print(f"  {backend:12} - {config['name']}")
    print("\nRequired Environment Variables:")
    for backend, config in BACKENDS.items():
        print(f"  {backend:12} - {', '.join(config['env_vars'])}")
    print("\nNote: Copy .env.example to .env and fill in your API keys")


def validate_args(args):
    """Validate command line arguments."""
    if len(args) != 3:
        print("Error: Invalid number of arguments\n")
        print_help()
        sys.exit(1)

    backend = args[1]
    page_path = args[2]

    if backend not in BACKENDS:
        print(f"Error: Unknown model backend '{backend}'\n")
        print_help()
        sys.exit(1)

    return backend, page_path


def check_api_keys(backend: str):
    """Check if required API keys are present."""
    # Skip check for prompt backend
    if backend == "prompt":
        return

    missing_keys = []
    required_vars = BACKENDS[backend]["env_vars"]

    for var in required_vars:
        if not os.getenv(var):
            missing_keys.append(var)

    if missing_keys:
        print(f"Error: Missing required environment variables for {backend}:")
        for key in missing_keys:
            print(f"  - {key}")
        print("\nPlease set these in your .env file (see .env.example)")
        sys.exit(1)


def load_world_style() -> str:
    """Load the visual style from world.yaml."""
    world_path = Path("world.yaml")

    if not world_path.exists():
        print("Warning: world.yaml not found, skipping world style")
        return ""

    try:
        with open(world_path, "r") as f:
            world_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Warning: Failed to load world.yaml: {e}")
        return ""

    visual_style = world_data.get("visual_style", [])
    if visual_style:
        return "\n".join(f"- {item}" for item in visual_style)
    return ""


def load_page_data(page_path: str) -> dict:
    """Load the page data from a page YAML file."""
    page_path = Path(page_path)

    if not page_path.exists():
        print(f"Error: Page file not found: {page_path}")
        sys.exit(1)

    try:
        with open(page_path, "r") as f:
            page_data = yaml.safe_load(f)
    except Exception as e:
        print(f"Error: Failed to load page file: {e}")
        sys.exit(1)

    visual_prompt = page_data.get("visual", "")
    if not visual_prompt:
        print(f"Error: No 'visual' field found in {page_path}")
        sys.exit(1)

    return page_data


def build_full_prompt(page_data: dict, world_style: str) -> str:
    """Build the complete prompt with world style and visual content."""
    visual = page_data.get("visual", "")

    prompt_parts = [
        "Create a beautiful illustration for a children's storybook page.",
    ]

    # Add world visual style
    if world_style:
        prompt_parts.append("\n--- WORLD VISUAL STYLE ---")
        prompt_parts.append(world_style)

    # Add image content
    prompt_parts.append("\n--- SCENE TO ILLUSTRATE ---")
    prompt_parts.append(visual)

    return "\n".join(prompt_parts)


def generate_with_openai(prompt: str, page_id: str) -> str:
    """Generate image using OpenAI DALL-E 3."""
    try:
        from openai import OpenAI
    except ImportError:
        print("Error: openai package not installed. Run: uv pip install openai")
        sys.exit(1)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print(f"Generating image with OpenAI DALL-E 3...")
    print(f"Prompt length: {len(prompt)} characters")

    # Truncate prompt if too long (DALL-E has a limit)
    if len(prompt) > 4000:
        print(f"Warning: Prompt truncated from {len(prompt)} to 4000 characters")
        prompt = prompt[:4000]

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1792x1024",  # 2:1 wide aspect ratio (closest available)
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url

        # Download the image
        import requests

        image_data = requests.get(image_url).content

        # Save to images directory
        output_dir = Path("images")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{page_id}-openai.jpg"

        with open(output_path, "wb") as f:
            f.write(image_data)

        return str(output_path)

    except Exception as e:
        print(f"Error generating image with OpenAI: {e}")
        sys.exit(1)


def generate_with_replicate(prompt: str, page_id: str) -> str:
    """Generate image using Replicate IPAdapter Style SDXL."""
    try:
        import replicate
    except ImportError:
        print("Error: replicate package not installed. Run: uv pip install replicate")
        sys.exit(1)

    print(f"Generating image with Replicate IPAdapter Style SDXL...")
    print(f"Prompt length: {len(prompt)} characters")

    try:
        # Use hardcoded style reference image
        style_image_path = Path("images/cu-01-openai.jpg")
        print(f"Using style reference: {style_image_path}")

        # Open and use the style image (will fail if doesn't exist)
        with open(style_image_path, "rb") as f:
            output = replicate.run(
                "lucataco/ipadapter-style-sdxl:9a89134b4c84c264c817645f1703db1e73f66a43c3f0bf2697ec2edce95f7d39",
                input={
                    "prompt": prompt,
                    "style_image": f,
                    "width": 1536,
                    "height": 768,
                    "num_outputs": 1,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 50,
                    "style_strength": 0.5,  # How much to apply the style (0-1)
                },
            )

        # Download the image
        import requests

        image_url = output[0]
        image_data = requests.get(image_url).content

        # Save to images directory
        output_dir = Path("images")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{page_id}-replicate.jpg"

        with open(output_path, "wb") as f:
            f.write(image_data)

        return str(output_path)

    except Exception as e:
        print(f"Error generating image with Replicate: {e}")
        sys.exit(1)


def generate_with_ideogram(prompt: str, page_id: str) -> str:
    """Generate image using Ideogram v3."""
    import requests

    api_key = os.getenv("IDEOGRAM_API_KEY")
    api_url = os.getenv(
        "IDEOGRAM_API_URL", "https://api.ideogram.ai/v1/ideogram-v3/generate"
    )

    print(f"Generating image with Ideogram v3...")
    print(f"Prompt length: {len(prompt)} characters")

    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json",
    }

    # Use flat JSON structure (not nested under image_request)
    payload = {
        "prompt": prompt,
        "aspect_ratio": "3x1",  # Wide aspect ratio
        "magic_prompt": "OFF",
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()

        # Extract image URL from response
        if "data" in result and len(result["data"]) > 0:
            image_url = result["data"][0].get("url")
        else:
            print(f"Error: Unexpected API response structure: {result}")
            sys.exit(1)

        # Download the image
        image_data = requests.get(image_url).content

        # Save to images directory
        output_dir = Path("images")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_path = output_dir / f"{page_id}-ideogram.jpg"

        with open(output_path, "wb") as f:
            f.write(image_data)

        return str(output_path)

    except requests.exceptions.RequestException as e:
        print(f"Error generating image with Ideogram: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def generate_prompt(prompt: str, page_id: str) -> str:
    """Display the prompt without generating an image."""
    print(f"\n{'='*80}")
    print("GENERATED PROMPT")
    print(f"{'='*80}\n")
    print(prompt)
    print(f"\n{'='*80}")
    print(f"Prompt length: {len(prompt)} characters")
    print(f"Page ID: {page_id}")
    print(f"{'='*80}\n")
    return "N/A (prompt mode)"


def main():
    """Main entry point."""
    # Validate arguments
    if len(sys.argv) == 1 or sys.argv[1] in ["-h", "--help", "help"]:
        print_help()
        sys.exit(0)

    backend, page_path = validate_args(sys.argv)

    # Extract page ID from path for output filename (e.g., "pages/cu-ha-02.yaml" -> "cu-ha-02")
    page_id = Path(page_path).stem

    # Check API keys before doing anything
    print(f"Checking API keys for {backend}...")
    check_api_keys(backend)

    # Load world style and page data
    print(f"Loading world style...")
    world_style = load_world_style()

    print(f"Loading page: {page_path}")
    page_data = load_page_data(page_path)

    # Build complete prompt
    prompt = build_full_prompt(page_data, world_style)

    # Generate image with selected backend
    if backend == "openai":
        output_path = generate_with_openai(prompt, page_id)
    elif backend == "replicate":
        output_path = generate_with_replicate(prompt, page_id)
    elif backend == "ideogram":
        output_path = generate_with_ideogram(prompt, page_id)
    elif backend == "prompt":
        output_path = generate_prompt(prompt, page_id)

    if backend != "prompt":
        print(f"\n✓ Image generated successfully!")
        print(f"  Saved to: {output_path}")


if __name__ == "__main__":
    main()
