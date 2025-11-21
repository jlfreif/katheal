#!/usr/bin/env python3
"""
Generate an HTML storybook for a character (can be printed to PDF from browser).

Usage:
    python3 scripts/gen_story_html.py <character-code>

Example:
    python3 scripts/gen_story_html.py no
    python3 scripts/gen_story_html.py el
"""

import sys
import yaml
from pathlib import Path


def load_character(char_code):
    """Load character data from the YAML file."""
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


def load_world():
    """Load world data."""
    world_path = Path('world.yaml')
    if world_path.exists():
        with open(world_path, 'r') as f:
            return yaml.safe_load(f)
    return {'name': 'Unknown World'}


def get_other_characters(page_id, main_char_code):
    """Extract other character codes from a page ID."""
    parts = page_id.split('-')
    chars = [p for p in parts if len(p) == 2 and p.isalpha() and p != main_char_code]
    return chars


def escape_html(text):
    """Escape HTML special characters."""
    if not isinstance(text, str):
        text = str(text)
    return (text.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


def text_to_paragraphs(text):
    """Convert text with line breaks to HTML paragraphs."""
    if not isinstance(text, str):
        text = str(text)
    paragraphs = [p.strip() for p in text.strip().split('\n') if p.strip()]
    return ''.join([f'<p>{escape_html(p)}</p>\n' for p in paragraphs])


def generate_html(char_code):
    """Generate an HTML storybook for the character."""
    # Load data
    char_data = load_character(char_code)
    world_data = load_world()

    char_name = char_data.get('attributes', {}).get('name', 'Unknown')
    world_name = world_data.get('name', 'Unknown World')
    pages = char_data.get('story', [])
    attributes = char_data.get('attributes', {})

    # Build HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape_html(char_name)}'s Story - {escape_html(world_name)}</title>
    <style>
        @page {{
            margin: 1in;
        }}
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
            max-width: 8.5in;
            margin: 0 auto;
            padding: 20px;
            background: #fafafa;
        }}
        .page {{
            background: white;
            padding: 40px;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            page-break-after: always;
        }}
        .title-page {{
            text-align: center;
            padding-top: 200px;
            min-height: 600px;
        }}
        h1 {{
            font-size: 2.5em;
            margin: 20px 0;
            color: #2c3e50;
        }}
        h2 {{
            font-size: 1.8em;
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
        }}
        h3 {{
            font-size: 1.3em;
            color: #555;
            margin-top: 20px;
        }}
        .subtitle {{
            font-size: 1.3em;
            color: #7f8c8d;
            font-style: italic;
            margin: 10px 0;
        }}
        .character-info {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            margin: 30px 0;
        }}
        .character-info h3 {{
            margin-top: 0;
            color: #2c3e50;
        }}
        .character-info p {{
            margin: 8px 0;
        }}
        .story-text {{
            background: #fff9e6;
            border-left: 4px solid #f39c12;
            padding: 15px 20px;
            margin: 20px 0;
            font-style: italic;
            font-size: 1.1em;
            color: #444;
        }}
        .visual-description {{
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 15px 20px;
            margin: 20px 0;
            font-size: 0.95em;
            color: #555;
        }}
        .description {{
            margin: 15px 0;
            padding: 10px 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .beat {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 10px 0;
        }}
        .synchrony-note {{
            background: #ffeaa7;
            border: 2px solid #fdcb6e;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: bold;
            color: #e67e22;
        }}
        .spread-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        .spread-number {{
            color: #95a5a6;
            font-size: 1.2em;
        }}
        @media print {{
            body {{
                background: white;
            }}
            .page {{
                box-shadow: none;
                margin: 0;
            }}
        }}
    </style>
</head>
<body>
    <!-- Title Page -->
    <div class="page title-page">
        <h1>{escape_html(char_name)}'s Story</h1>
        <div class="subtitle">A Tale from {escape_html(world_name)}</div>
    </div>

    <!-- Character Information Page -->
    <div class="page">
        <h2>About {escape_html(char_name)}</h2>
        <div class="character-info">
"""

    # Add character attributes
    if 'age' in attributes:
        html += f"            <p><strong>Age:</strong> {attributes['age']}</p>\n"

    if 'gender' in attributes:
        html += f"            <p><strong>Gender:</strong> {escape_html(str(attributes['gender']))}</p>\n"

    if 'core_values_motivations' in attributes:
        values = attributes['core_values_motivations']
        if values:
            html += "            <p><strong>Core Values:</strong></p>\n"
            html += "            <ul>\n"
            for value in values:
                html += f"                <li>{escape_html(str(value))}</li>\n"
            html += "            </ul>\n"

    if 'key_personality_traits' in attributes:
        traits = attributes['key_personality_traits']
        if traits:
            html += "            <p><strong>Personality Traits:</strong></p>\n"
            html += "            <ul>\n"
            for trait in traits:
                html += f"                <li>{escape_html(str(trait))}</li>\n"
            html += "            </ul>\n"

    if 'hobbies_interests_skills' in attributes:
        hobbies = attributes['hobbies_interests_skills']
        if hobbies:
            html += "            <p><strong>Interests &amp; Skills:</strong></p>\n"
            html += "            <ul>\n"
            for hobby in hobbies:
                html += f"                <li>{escape_html(str(hobby))}</li>\n"
            html += "            </ul>\n"

    html += """        </div>
    </div>

    <!-- Story Pages -->
"""

    # Add each page
    for i, page_filename in enumerate(pages, 1):
        page_data = load_page(page_filename)
        if not page_data:
            continue

        page_id = page_filename.replace('.yaml', '')
        other_chars = get_other_characters(page_id, char_code)

        html += f"""    <div class="page">
        <div class="spread-header">
            <h2>Spread {i}</h2>
            <span class="spread-number">{escape_html(page_filename)}</span>
        </div>
"""

        # Synchrony Node note
        if other_chars:
            char_names = ', '.join([c.upper() for c in other_chars])
            html += f'        <div class="synchrony-note">✨ Synchrony Node with {char_names}</div>\n'

        # Story beat
        if 'beat' in page_data:
            html += f'        <div class="beat">{escape_html(str(page_data["beat"]))}</div>\n'

        # Description
        if 'description' in page_data:
            html += '        <div class="description">\n'
            html += text_to_paragraphs(page_data['description'])
            html += '        </div>\n'

        # Story text (highlighted)
        if 'text' in page_data:
            html += '        <div class="story-text">\n'
            html += text_to_paragraphs(page_data['text'])
            html += '        </div>\n'

        # Visual description
        if 'visual' in page_data:
            html += '        <h3>Visual Scene</h3>\n'
            html += '        <div class="visual-description">\n'
            html += text_to_paragraphs(page_data['visual'])
            html += '        </div>\n'

        html += '    </div>\n\n'

    # Close HTML
    html += """</body>
</html>
"""

    # Save HTML
    output_dir = Path('out-pdfs')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{char_code}-{char_name.lower()}-story.html"

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ HTML generated: {output_file}")
    print(f"  To create PDF: Open {output_file} in a browser and use Print → Save as PDF")
    return output_file


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/gen_story_html.py <character-code>")
        print("Example: python3 scripts/gen_story_html.py no")
        sys.exit(1)

    char_code = sys.argv[1]
    generate_html(char_code)


if __name__ == '__main__':
    main()
