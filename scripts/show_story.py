#!/usr/bin/env python3
"""
Show the full story for a character given their two-letter code.

Supports both legacy format (single visual/text) and new format (scenes array).

Usage:
    python3 scripts/show_story.py <character-code>

Example:
    python3 scripts/show_story.py cu
"""

import sys
import yaml
from pathlib import Path

# Node type display names
NODE_TYPE_NAMES = {
    'solo': 'Solo',
    'meeting': 'Meeting Node',
    'mirrored': 'Mirrored Node',
    'resonant': 'Resonant Node',
}


def get_other_characters(page_id, main_char_code):
    """Extract other character codes from a page ID."""
    # Split by hyphens and filter out numbers and the main character code
    parts = page_id.split('-')
    chars = [p for p in parts if len(p) == 2 and p.isalpha() and p != main_char_code]
    return chars


def load_character(char_code):
    """Load character data from the YAML file."""
    char_file = Path('characters') / f'{char_code}-*.yaml'
    matches = list(Path('characters').glob(f'{char_code}-*.yaml'))

    if not matches:
        print(f"Error: No character file found for code '{char_code}'")
        sys.exit(1)

    with open(matches[0], 'r') as f:
        return yaml.safe_load(f)


def load_page(page_filename):
    """Load page data from the YAML file."""
    page_path = Path('pages') / page_filename

    if not page_path.exists():
        print(f"Warning: Page file not found: {page_filename}")
        return None

    with open(page_path, 'r') as f:
        return yaml.safe_load(f)


def show_page(page_filename, char_code, level=3):
    """Display a single page with the specified heading level."""
    page_data = load_page(page_filename)
    if not page_data:
        return None

    # Extract page ID (filename without .yaml)
    page_id = page_filename.replace('.yaml', '')

    # Check if this is a joint page
    other_chars = get_other_characters(page_id, char_code)
    joint_note = f" (joint with {', '.join(other_chars).upper()})" if other_chars else ""

    # Get node type
    node_type = page_data.get('node_type', 'solo' if not other_chars else 'meeting')
    node_type_name = NODE_TYPE_NAMES.get(node_type, node_type)

    # Determine heading symbols based on level
    page_heading = '#' * level
    content_heading = '#' * (level + 1)

    # Display page information
    spread = page_data.get('spread', '?')
    beat = page_data.get('beat', 'Unknown beat')
    print(f"{page_heading} Spread {spread}: {page_filename}{joint_note}")
    print(f"**Node Type:** {node_type_name} | **Beat:** {beat}\n")

    # Description
    description = page_data.get('description', 'No description available')
    print(f"{content_heading} Description\n")
    print(f"{description}\n")

    # Check for new scene-based format or legacy format
    scenes = page_data.get('scenes', [])

    if scenes:
        # New format with scenes
        for i, scene in enumerate(scenes):
            page_position = scene.get('page', 'left' if i == 0 else 'right')
            page_num = scene.get('page_number', '')
            focus = scene.get('focus', '')

            scene_title = f"Page {page_num} ({page_position.capitalize()})" if page_num else f"{page_position.capitalize()} Page"
            if focus:
                scene_title += f" - {focus}"

            print(f"{content_heading} {scene_title}\n")

            # Visual
            visual = scene.get('visual', 'No visual description')
            print(f"**Visual:**\n{visual.strip() if isinstance(visual, str) else visual}\n")

            # Text
            text = scene.get('text', 'No text')
            print(f"**Text:**\n{text.strip() if isinstance(text, str) else text}\n")

    else:
        # Legacy format with single visual/text
        print(f"{content_heading} Visual\n")
        visual = page_data.get('visual', 'No visual description available')
        if isinstance(visual, str):
            print(f"{visual.strip()}\n")
        else:
            print(f"{visual}\n")

        print(f"{content_heading} Text\n")
        text = page_data.get('text', 'No text available')
        if isinstance(text, str):
            print(f"{text.strip()}\n")
        else:
            print(f"{text}\n")

    # Show node-specific metadata if present
    if node_type == 'meeting':
        location = page_data.get('location')
        shared_action = page_data.get('shared_action')
        if location:
            print(f"**Meeting Location:** {location}\n")
        if shared_action:
            print(f"**Shared Action:** {shared_action}\n")

    return other_chars


def get_surrounding_pages(page_filename, other_char_code):
    """Get the preceding and succeeding pages from another character's story."""
    other_char_data = load_character(other_char_code)
    other_pages = other_char_data.get('story', [])

    try:
        idx = other_pages.index(page_filename)
        preceding = other_pages[idx - 1] if idx > 0 else None
        succeeding = other_pages[idx + 1] if idx < len(other_pages) - 1 else None
        return preceding, succeeding
    except ValueError:
        # Page not found in other character's story
        return None, None


def show_story(char_code):
    """Display the full story for a character."""
    # Load character data
    char_data = load_character(char_code)
    char_name = char_data['attributes']['name']
    pages = char_data.get('story', [])

    print(f"# {char_name}'s Story\n")

    # Show story summary
    print(f"**Character Code:** {char_code.upper()}")
    print(f"**Total Spreads:** {len(pages)}")
    print(f"**Layout:** 2 pages per spread, 1 image per page, 3-4 sentences per scene\n")

    print(f"## Story\n")

    # Track overlapping pages
    overlaps = []

    for page_filename in pages:
        other_chars = show_page(page_filename, char_code, level=3)
        if other_chars:
            overlaps.append((page_filename, other_chars))
        print("-" * 80 + "\n")

    # Show overlaps section
    if overlaps:
        print(f"## Narrative Node Analysis\n")
        print(f"This story connects with other characters at {len(overlaps)} point(s):\n")

        for page_filename, other_chars in overlaps:
            for other_char_code in other_chars:
                # Get surrounding pages from the other character's story
                preceding, succeeding = get_surrounding_pages(page_filename, other_char_code)

                other_char_data = load_character(other_char_code)
                other_char_name = other_char_data['attributes']['name']

                # Load page to get node type
                page_data = load_page(page_filename)
                node_type = page_data.get('node_type', 'meeting') if page_data else 'meeting'
                node_type_name = NODE_TYPE_NAMES.get(node_type, node_type)

                print(f"### {node_type_name} with {other_char_name} ({other_char_code.upper()})\n")

                # Show preceding page
                if preceding:
                    print(f"#### Before (from {other_char_name}'s story)\n")
                    show_page(preceding, other_char_code, level=5)

                # Show the overlap page
                print(f"#### Shared/Connected Page\n")
                show_page(page_filename, char_code, level=5)

                # Show succeeding page
                if succeeding:
                    print(f"#### After (from {other_char_name}'s story)\n")
                    show_page(succeeding, other_char_code, level=5)


def main():
    if len(sys.argv) != 2:
        print("Usage: python show_story.py <character-code>")
        print("Example: python show_story.py cu")
        sys.exit(1)

    char_code = sys.argv[1].lower()

    if len(char_code) != 2:
        print("Error: Character code must be exactly 2 characters")
        sys.exit(1)

    show_story(char_code)


if __name__ == '__main__':
    main()
