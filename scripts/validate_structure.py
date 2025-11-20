#!/usr/bin/env python3
"""
Validation script to check structural integrity of the repository.

LAYOUT STRUCTURE:
- Each spread = 2 pages with 1 image spanning across both
- 12 spreads total per character = 12 images total
- File naming: {char}-{spread}.yaml (e.g., cu-01.yaml)
- For shared spreads: {char1}-{char2}-{spread}.yaml (alphabetical order)
- Node types: solo, meeting, mirrored, resonant

Checks:
- Spread files are well formatted
- All referenced spreads exist
- No overlaps on spreads 1, 11, and 12 (these must be character-specific)
- Spreads end in .yaml extension
- Spreads don't have the pages/ subdirectory prefix
- No missing/stray spreads in the pages directory
- At least one character exists
- All YAML files are valid
- Spread structure validation (node types, visual, text, etc.)
- Node type metadata validation

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
RESET = '\033[0m'

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


def test_spread_formatting(characters):
    """Test that all spread references are properly formatted."""
    errors_found = False

    for char_id, char_info in characters.items():
        spreads = char_info['data'].get('story', [])
        char_name = char_info['name']

        for spread in spreads:
            # Check for pages/ prefix
            if spread.startswith('pages/'):
                error(f"{char_name} ({char_id}): Spread '{spread}' includes 'pages/' prefix - should be just filename")
                errors_found = True

            # Check for .yaml extension
            if not spread.endswith('.yaml'):
                error(f"{char_name} ({char_id}): Spread '{spread}' missing '.yaml' extension")
                errors_found = True

            # Check for path separators
            if '/' in spread or '\\' in spread:
                error(f"{char_name} ({char_id}): Spread '{spread}' contains path separator - should be just filename")
                errors_found = True

    if not errors_found:
        success("All spread references are properly formatted")
    return not errors_found


def test_spreads_exist(characters):
    """Test that all referenced spreads exist."""
    errors_found = False
    pages_dir = Path('pages')

    if not pages_dir.exists():
        error("Pages directory not found")
        return False

    for char_id, char_info in characters.items():
        spreads = char_info['data'].get('story', [])
        char_name = char_info['name']

        for spread in spreads:
            spread_path = pages_dir / spread
            if not spread_path.exists():
                error(f"{char_name} ({char_id}): Referenced spread '{spread}' does not exist")
                errors_found = True

    if not errors_found:
        success("All referenced spreads exist")
    return not errors_found


def test_no_overlaps_on_required_solo_spreads(characters):
    """Test that spreads 1, 11, and 12 have no overlaps (are character-specific)."""
    errors_found = False
    required_solo_spreads = [1, 11, 12]

    for char_id, char_info in characters.items():
        spreads = char_info['data'].get('story', [])
        char_name = char_info['name']

        for spread in spreads:
            # Extract spread ID (filename without .yaml)
            spread_id = spread.replace('.yaml', '')

            # Parse format: {char}-{spread}.yaml or {char1}-{char2}-{spread}.yaml
            parts = spread_id.split('-')

            # Check if spread contains multiple character codes
            # Character codes are 2-letter alphabetic parts
            char_codes = [p for p in parts[:-1] if len(p) == 2 and p.isalpha()]

            # Extract spread number (should be last part)
            spread_num = None
            if len(parts) >= 2:
                try:
                    spread_num = int(parts[-1])
                except ValueError:
                    pass

            if spread_num in required_solo_spreads and len(char_codes) > 1:
                error(f"{char_name} ({char_id}): Spread {spread_num} ('{spread}') is a joint spread with {char_codes} - spreads 1, 11, 12 must be character-specific")
                errors_found = True

    if not errors_found:
        success("Spreads 1, 11, and 12 are all character-specific (no overlaps)")
    return not errors_found


def test_no_stray_spreads(characters):
    """Test that all spreads in the pages directory are referenced by at least one character."""
    pages_dir = Path('pages')

    if not pages_dir.exists():
        error("Pages directory not found")
        return False

    # Collect all referenced spreads
    referenced_spreads = set()
    for char_id, char_info in characters.items():
        spreads = char_info['data'].get('story', [])
        referenced_spreads.update(spreads)

    # Get all actual spread files
    all_spread_files = set(p.name for p in pages_dir.glob('*.yaml'))

    # Find stray spreads
    stray_spreads = all_spread_files - referenced_spreads

    if stray_spreads:
        error(f"Found {len(stray_spreads)} stray spread(s) not referenced by any character:")
        for spread in sorted(stray_spreads):
            info(f"  - {spread}")
        return False

    success("No stray spreads found - all spreads are referenced")
    return True


def test_missing_spreads(characters):
    """Test for any missing spreads in character stories (e.g., gaps in numbering)."""
    warnings_found = False

    for char_id, char_info in characters.items():
        spreads = char_info['data'].get('story', [])
        char_name = char_info['name']

        # Expected: 12 spreads
        if len(spreads) != 12:
            warning(f"{char_name} ({char_id}): Has {len(spreads)} spreads, expected 12")
            warnings_found = True

        # Check for sequential spread numbering
        # Expected pattern: spreads 1-12
        expected_spreads = list(range(1, 13))

        # Extract actual spread numbers
        actual_spreads = []
        for spread in spreads:
            spread_id = spread.replace('.yaml', '')
            parts = spread_id.split('-')

            # Try to extract spread number (should be last part)
            try:
                if len(parts) >= 2:
                    spread_num = int(parts[-1])
                    actual_spreads.append(spread_num)
            except ValueError:
                warning(f"{char_name} ({char_id}): Unable to parse spread format: {spread}")

        if actual_spreads and sorted(actual_spreads) != expected_spreads:
            info(f"{char_name} ({char_id}): Spread sequence differs from expected (1-12)")

    if not warnings_found:
        success("All characters have 12 spreads")

    return True  # Warnings don't fail the test


def test_spread_yaml_validity(characters):
    """Test that all spread YAML files are valid."""
    errors_found = False
    pages_dir = Path('pages')

    # Collect all referenced spreads
    all_spreads = set()
    for char_id, char_info in characters.items():
        spreads = char_info['data'].get('story', [])
        all_spreads.update(spreads)

    for spread in all_spreads:
        spread_path = pages_dir / spread
        if spread_path.exists():
            try:
                with open(spread_path, 'r') as f:
                    yaml.safe_load(f)
            except Exception as e:
                error(f"Spread '{spread}' is not valid YAML: {e}")
                errors_found = True

    if not errors_found:
        success("All spread YAML files are valid")
    return not errors_found


def test_spread_structure(characters):
    """Test that spreads have proper structure (node type, visual, text, etc.)."""
    errors_found = False
    warnings_found = False
    pages_dir = Path('pages')

    # Collect all referenced spreads
    all_spreads = set()
    for char_id, char_info in characters.items():
        spreads = char_info['data'].get('story', [])
        all_spreads.update(spreads)

    for spread in all_spreads:
        spread_path = pages_dir / spread
        if spread_path.exists():
            try:
                with open(spread_path, 'r') as f:
                    spread_data = yaml.safe_load(f)

                # Check for required fields
                if 'node_type' not in spread_data:
                    warning(f"Spread '{spread}' missing 'node_type' field")
                    warnings_found = True
                elif spread_data['node_type'] not in ['solo', 'meeting', 'mirrored', 'resonant']:
                    error(f"Spread '{spread}' has invalid node_type: {spread_data['node_type']}")
                    errors_found = True

                # Check for visual field
                if 'visual' not in spread_data:
                    warning(f"Spread '{spread}' missing 'visual' field (image description)")
                    warnings_found = True

                # Check for text field
                if 'text' not in spread_data:
                    warning(f"Spread '{spread}' missing 'text' field (story text)")
                    warnings_found = True

                # Validate node-specific metadata
                node_type = spread_data.get('node_type')
                if node_type == 'meeting' and 'meeting_data' not in spread_data:
                    warning(f"Spread '{spread}' is a meeting node but missing 'meeting_data'")
                    warnings_found = True
                if node_type == 'mirrored' and 'mirrored_data' not in spread_data:
                    warning(f"Spread '{spread}' is a mirrored node but missing 'mirrored_data'")
                    warnings_found = True
                if node_type == 'resonant' and 'resonant_data' not in spread_data:
                    warning(f"Spread '{spread}' is a resonant node but missing 'resonant_data'")
                    warnings_found = True

            except Exception as e:
                # Skip if already caught by YAML validity test
                pass

    if not errors_found and not warnings_found:
        success("All spreads have proper structure")
    elif not errors_found:
        success("Spread structure validation passed (with warnings)")

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
        ("Spread formatting is correct", lambda: test_spread_formatting(characters)),
        ("All referenced spreads exist", lambda: test_spreads_exist(characters)),
        ("Spreads 1, 11, 12 are character-specific", lambda: test_no_overlaps_on_required_solo_spreads(characters)),
        ("No stray spreads in pages directory", lambda: test_no_stray_spreads(characters)),
        ("Spread YAML files are valid", lambda: test_spread_yaml_validity(characters)),
        ("Spread structure validation", lambda: test_spread_structure(characters)),
        ("Check for missing spreads", lambda: test_missing_spreads(characters)),
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
