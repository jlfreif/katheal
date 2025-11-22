#!/usr/bin/env python3
"""
Validation script to check structural integrity of the repository.

Checks:
- Pages are well formatted
- All referenced pages exist
- No overlaps on spreads 1, 11, and 12 (these must be character-specific)
- Pages end in .yaml extension
- Pages don't have the pages/ subdirectory prefix
- No missing/stray pages in the pages directory
- At least one character exists
- All YAML files are valid
- Node types are valid (solo, meeting, mirrored, resonant)
- Scene structure is present for new-format pages

Exit codes:
- 0: All tests passed
- 1: One or more tests failed
"""

import sys
import yaml
from pathlib import Path
from collections import defaultdict

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

# Valid node types
VALID_NODE_TYPES = ['solo', 'meeting', 'mirrored', 'resonant']

# Spreads that must be character-specific (no nodes allowed)
REQUIRED_SOLO_SPREADS = [1, 11, 12]


def error(message):
    """Print error message in red."""
    print(f"{RED}✗ ERROR: {message}{RESET}")


def warning(message):
    """Print warning message in yellow."""
    print(f"{YELLOW}⚠ WARNING: {message}{RESET}")


def success(message):
    """Print success message in green."""
    print(f"{GREEN}✓ {message}{RESET}")


def info(message):
    """Print info message."""
    print(f"  {message}")


def note(message):
    """Print note message in blue."""
    print(f"{BLUE}ℹ {message}{RESET}")


def load_all_characters():
    """Load all character files."""
    characters_dir = Path('characters')
    if not characters_dir.exists():
        error("Characters directory not found")
        sys.exit(1)

    char_files = list(characters_dir.glob('*.yaml'))
    # Filter out template files
    char_files = [f for f in char_files if 'template' not in f.name and 'example' not in f.name]

    if not char_files:
        error("No character files found in characters directory")
        sys.exit(1)

    characters = {}
    for char_file in char_files:
        try:
            with open(char_file, 'r') as f:
                char_data = yaml.safe_load(f)
                char_id = char_data.get('id')
                if char_id:
                    characters[char_id] = {
                        'file': char_file,
                        'data': char_data,
                        'name': char_data.get('attributes', {}).get('name', 'Unknown')
                    }
        except Exception as e:
            error(f"Failed to load character file {char_file}: {e}")
            sys.exit(1)

    return characters


def test_at_least_one_character(characters):
    """Test that at least one character exists."""
    if len(characters) == 0:
        error("No characters found")
        return False
    success(f"Found {len(characters)} character(s)")
    return True


def test_page_formatting(characters):
    """Test that all page references are properly formatted."""
    errors_found = False

    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        char_name = char_info['name']

        for page in pages:
            # Check for pages/ prefix
            if page.startswith('pages/'):
                error(f"{char_name} ({char_id}): Page '{page}' includes 'pages/' prefix - should be just filename")
                errors_found = True

            # Check for .yaml extension
            if not page.endswith('.yaml'):
                error(f"{char_name} ({char_id}): Page '{page}' missing '.yaml' extension")
                errors_found = True

            # Check for path separators
            if '/' in page or '\\' in page:
                error(f"{char_name} ({char_id}): Page '{page}' contains path separator - should be just filename")
                errors_found = True

    if not errors_found:
        success("All page references are properly formatted")
    return not errors_found


def test_pages_exist(characters):
    """Test that all referenced pages exist."""
    errors_found = False
    pages_dir = Path('pages')

    if not pages_dir.exists():
        error("Pages directory not found")
        return False

    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        char_name = char_info['name']

        for page in pages:
            page_path = pages_dir / page
            if not page_path.exists():
                error(f"{char_name} ({char_id}): Referenced page '{page}' does not exist")
                errors_found = True

    if not errors_found:
        success("All referenced pages exist")
    return not errors_found


def test_no_overlaps_on_required_solo_spreads(characters):
    """Test that spreads 1, 11, and 12 have no overlaps (are character-specific)."""
    errors_found = False

    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        char_name = char_info['name']

        for pos in REQUIRED_SOLO_SPREADS:
            if pos - 1 < len(pages):  # Check if this position exists
                page = pages[pos - 1]
                # Extract page ID (filename without .yaml)
                page_id = page.replace('.yaml', '')

                # Check if page contains multiple character codes
                parts = page_id.split('-')
                char_codes = [p for p in parts if len(p) == 2 and p.isalpha()]

                if len(char_codes) > 1:
                    error(f"{char_name} ({char_id}): Spread {pos} ('{page}') is a joint page with {char_codes} - spreads 1, 11, 12 must be character-specific")
                    errors_found = True

    if not errors_found:
        success("Spreads 1, 11, and 12 are all character-specific (no overlaps)")
    return not errors_found


def test_no_stray_pages(characters):
    """Test that all pages in the pages directory are referenced by at least one character."""
    pages_dir = Path('pages')

    if not pages_dir.exists():
        error("Pages directory not found")
        return False

    # Collect all referenced pages
    referenced_pages = set()
    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        referenced_pages.update(pages)

    # Get all actual page files
    all_page_files = set(p.name for p in pages_dir.glob('*.yaml'))

    # Find stray pages
    stray_pages = all_page_files - referenced_pages

    if stray_pages:
        error(f"Found {len(stray_pages)} stray page(s) not referenced by any character:")
        for page in sorted(stray_pages):
            info(f"  - {page}")
        return False

    success("No stray pages found - all pages are referenced")
    return True


def test_missing_pages(characters):
    """Test for any missing pages in character stories (e.g., gaps in numbering)."""
    warnings_found = False

    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        char_name = char_info['name']

        # Expected: 12 pages
        if len(pages) != 12:
            warning(f"{char_name} ({char_id}): Has {len(pages)} pages, expected 12")
            warnings_found = True

        # Check for sequential numbering (this is a soft check)
        # Extract page numbers
        page_numbers = []
        for page in pages:
            page_id = page.replace('.yaml', '')
            parts = page_id.split('-')
            # Look for the numeric part
            for part in parts:
                if part.isdigit():
                    page_numbers.append(int(part))
                    break

        if page_numbers:
            expected = list(range(1, 13))
            if page_numbers != expected:
                info(f"{char_name} ({char_id}): Page numbering is {page_numbers}")

    if not warnings_found:
        success("All characters have 12 pages")

    return True  # Warnings don't fail the test


def test_page_yaml_validity(characters):
    """Test that all page YAML files are valid."""
    errors_found = False
    pages_dir = Path('pages')

    # Collect all referenced pages
    all_pages = set()
    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        all_pages.update(pages)

    for page in all_pages:
        page_path = pages_dir / page
        if page_path.exists():
            try:
                with open(page_path, 'r') as f:
                    yaml.safe_load(f)
            except Exception as e:
                error(f"Page '{page}' is not valid YAML: {e}")
                errors_found = True

    if not errors_found:
        success("All page YAML files are valid")
    return not errors_found


def test_node_types(characters):
    """Test that all pages have valid node types."""
    errors_found = False
    warnings_found = False
    pages_dir = Path('pages')

    # Collect all referenced pages
    all_pages = set()
    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        all_pages.update(pages)

    pages_with_node_type = 0
    pages_without_node_type = 0

    for page in all_pages:
        page_path = pages_dir / page
        if page_path.exists():
            try:
                with open(page_path, 'r') as f:
                    page_data = yaml.safe_load(f)

                node_type = page_data.get('node_type')

                if node_type:
                    pages_with_node_type += 1
                    if node_type not in VALID_NODE_TYPES:
                        error(f"Page '{page}' has invalid node_type '{node_type}'. Valid types: {VALID_NODE_TYPES}")
                        errors_found = True

                    # Check that meeting nodes have multiple character codes
                    page_id = page.replace('.yaml', '')
                    parts = page_id.split('-')
                    char_codes = [p for p in parts if len(p) == 2 and p.isalpha()]

                    if node_type == 'meeting' and len(char_codes) < 2:
                        error(f"Page '{page}' is marked as meeting node but has only one character code")
                        errors_found = True

                    if node_type == 'solo' and len(char_codes) > 1:
                        warning(f"Page '{page}' is marked as solo but has multiple character codes")
                        warnings_found = True
                else:
                    pages_without_node_type += 1
                    # Infer node type from filename
                    page_id = page.replace('.yaml', '')
                    parts = page_id.split('-')
                    char_codes = [p for p in parts if len(p) == 2 and p.isalpha()]
                    inferred_type = 'meeting' if len(char_codes) > 1 else 'solo'
                    # This is just informational - not an error

            except Exception as e:
                error(f"Failed to check node_type for '{page}': {e}")
                errors_found = True

    if pages_without_node_type > 0:
        note(f"{pages_without_node_type} page(s) don't have explicit node_type (using legacy format)")

    if not errors_found:
        success(f"All page node types are valid ({pages_with_node_type} explicit, {pages_without_node_type} inferred)")

    return not errors_found


def test_scene_structure(characters):
    """Test that pages have proper scene structure (new format) or legacy fields."""
    errors_found = False
    pages_dir = Path('pages')

    # Collect all referenced pages
    all_pages = set()
    for char_id, char_info in characters.items():
        pages = char_info['data'].get('story', [])
        all_pages.update(pages)

    pages_with_scenes = 0
    pages_with_legacy = 0

    for page in all_pages:
        page_path = pages_dir / page
        if page_path.exists():
            try:
                with open(page_path, 'r') as f:
                    page_data = yaml.safe_load(f)

                has_scenes = 'scenes' in page_data and page_data['scenes']
                has_legacy_visual = 'visual' in page_data
                has_legacy_text = 'text' in page_data

                if has_scenes:
                    pages_with_scenes += 1
                    # Validate scene structure
                    scenes = page_data['scenes']
                    if len(scenes) != 2:
                        warning(f"Page '{page}' has {len(scenes)} scenes, expected 2 (left and right)")

                    for i, scene in enumerate(scenes):
                        if 'visual' not in scene:
                            error(f"Page '{page}' scene {i+1} missing 'visual' field")
                            errors_found = True
                        if 'text' not in scene:
                            error(f"Page '{page}' scene {i+1} missing 'text' field")
                            errors_found = True
                        if 'page' not in scene:
                            warning(f"Page '{page}' scene {i+1} missing 'page' field (left/right)")

                elif has_legacy_visual and has_legacy_text:
                    pages_with_legacy += 1
                else:
                    error(f"Page '{page}' has neither scenes structure nor legacy visual/text fields")
                    errors_found = True

            except Exception as e:
                error(f"Failed to check scene structure for '{page}': {e}")
                errors_found = True

    note(f"Page formats: {pages_with_scenes} new (scenes), {pages_with_legacy} legacy (visual/text)")

    if not errors_found:
        success("All pages have valid content structure")

    return not errors_found


def test_world_interactions(characters):
    """Test that world.yaml interactions reference valid pages and characters."""
    world_path = Path('world.yaml')
    pages_dir = Path('pages')

    if not world_path.exists():
        warning("world.yaml not found - skipping interaction validation")
        return True

    try:
        with open(world_path, 'r') as f:
            world_data = yaml.safe_load(f)
    except Exception as e:
        error(f"Failed to load world.yaml: {e}")
        return False

    interactions = world_data.get('interactions', [])
    if not interactions:
        note("No interactions defined in world.yaml")
        return True

    errors_found = False

    for interaction in interactions:
        if not isinstance(interaction, dict):
            continue

        chars = interaction.get('characters', [])
        nodes = interaction.get('nodes', [])

        # Validate characters exist
        if isinstance(chars, list):
            for char_code in chars:
                if char_code and char_code not in characters:
                    error(f"Interaction references unknown character '{char_code}'")
                    errors_found = True

        # Validate nodes
        if isinstance(nodes, list):
            for node in nodes:
                if not isinstance(node, dict):
                    continue

                spread = node.get('spread')
                node_type = node.get('type')
                page_file = node.get('page_file')

                if spread in REQUIRED_SOLO_SPREADS:
                    error(f"Node at spread {spread} violates constraint - spreads 1, 11, 12 must be character-specific")
                    errors_found = True

                if node_type and node_type not in VALID_NODE_TYPES:
                    error(f"Node has invalid type '{node_type}'")
                    errors_found = True

                if page_file:
                    page_path = pages_dir / page_file
                    if not page_path.exists():
                        error(f"Node references non-existent page '{page_file}'")
                        errors_found = True

    if not errors_found:
        success("World interactions are valid")

    return not errors_found


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("REPOSITORY STRUCTURE VALIDATION")
    print("="*80 + "\n")

    # Load all characters
    try:
        characters = load_all_characters()
    except SystemExit:
        return 1

    # Run all tests
    tests = [
        ("At least one character exists", lambda: test_at_least_one_character(characters)),
        ("Page formatting is correct", lambda: test_page_formatting(characters)),
        ("All referenced pages exist", lambda: test_pages_exist(characters)),
        ("Spreads 1, 11, 12 are character-specific", lambda: test_no_overlaps_on_required_solo_spreads(characters)),
        ("No stray pages in pages directory", lambda: test_no_stray_pages(characters)),
        ("Page YAML files are valid", lambda: test_page_yaml_validity(characters)),
        ("Check for missing pages", lambda: test_missing_pages(characters)),
        ("Node types are valid", lambda: test_node_types(characters)),
        ("Scene structure is valid", lambda: test_scene_structure(characters)),
        ("World interactions are valid", lambda: test_world_interactions(characters)),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        print("-" * 80)
        result = test_func()
        results.append(result)

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(results)
    total = len(results)

    if all(results):
        success(f"All {total} tests passed!")
        print()
        return 0
    else:
        error(f"{total - passed} out of {total} tests failed")
        print()
        return 1


if __name__ == '__main__':
    sys.exit(main())
