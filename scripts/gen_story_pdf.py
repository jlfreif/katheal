#!/usr/bin/env python3
"""
Generate a PDF storybook for a character.

Usage:
    python3 scripts/gen_story_pdf.py <character-code>

Example:
    python3 scripts/gen_story_pdf.py no
    python3 scripts/gen_story_pdf.py el
"""

import sys
import yaml
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


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


def generate_pdf(char_code):
    """Generate a PDF storybook for the character."""
    # Load data
    char_data = load_character(char_code)
    world_data = load_world()

    char_name = char_data.get('attributes', {}).get('name', 'Unknown')
    world_name = world_data.get('name', 'Unknown World')
    pages = char_data.get('story', [])
    attributes = char_data.get('attributes', {})

    # Create PDF
    output_dir = Path('out-pdfs')
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{char_code}-{char_name.lower()}-story.pdf"

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=20,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Times-Italic',
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        spaceBefore=12,
    )

    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#555555'),
        spaceAfter=8,
        spaceBefore=8,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        spaceAfter=10,
    )

    story_text_style = ParagraphStyle(
        'StoryText',
        parent=styles['BodyText'],
        fontSize=12,
        leading=18,
        textColor=colors.HexColor('#2c3e50'),
        fontName='Times-Italic',
        leftIndent=20,
        rightIndent=20,
        spaceAfter=12,
    )

    visual_style = ParagraphStyle(
        'Visual',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#555555'),
        leftIndent=10,
        spaceAfter=10,
    )

    # Title page
    elements.append(Spacer(1, 2 * inch))
    elements.append(Paragraph(f"{char_name}'s Story", title_style))
    elements.append(Paragraph(f"A Tale from {world_name}", subtitle_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Character information
    elements.append(PageBreak())
    elements.append(Paragraph(f"About {char_name}", heading2_style))
    elements.append(Spacer(1, 0.2 * inch))

    char_info = []
    if 'age' in attributes:
        char_info.append(['Age:', str(attributes['age'])])
    if 'gender' in attributes:
        char_info.append(['Gender:', str(attributes['gender'])])

    if char_info:
        t = Table(char_info, colWidths=[1.5 * inch, 4 * inch])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.2 * inch))

    if 'core_values_motivations' in attributes and attributes['core_values_motivations']:
        elements.append(Paragraph("<b>Core Values:</b>", body_style))
        for value in attributes['core_values_motivations']:
            elements.append(Paragraph(f"• {value}", body_style))
        elements.append(Spacer(1, 0.1 * inch))

    if 'key_personality_traits' in attributes and attributes['key_personality_traits']:
        elements.append(Paragraph("<b>Personality Traits:</b>", body_style))
        for trait in attributes['key_personality_traits']:
            elements.append(Paragraph(f"• {trait}", body_style))
        elements.append(Spacer(1, 0.1 * inch))

    if 'hobbies_interests_skills' in attributes and attributes['hobbies_interests_skills']:
        elements.append(Paragraph("<b>Interests & Skills:</b>", body_style))
        for hobby in attributes['hobbies_interests_skills']:
            elements.append(Paragraph(f"• {hobby}", body_style))

    # Story pages
    for i, page_filename in enumerate(pages, 1):
        page_data = load_page(page_filename)
        if not page_data:
            continue

        page_id = page_filename.replace('.yaml', '')
        other_chars = get_other_characters(page_id, char_code)

        # New page for each spread
        elements.append(PageBreak())

        # Page header
        title = f"Spread {i}"
        if other_chars:
            title += f" ✨ Synchrony Node"
        elements.append(Paragraph(title, heading2_style))

        if other_chars:
            char_names = ', '.join([c.upper() for c in other_chars])
            elements.append(Paragraph(
                f"<i>Shared with {char_names}</i>",
                ParagraphStyle('italic', parent=body_style, textColor=colors.HexColor('#e67e22'))
            ))

        elements.append(Spacer(1, 0.1 * inch))

        # Story beat
        if 'beat' in page_data:
            elements.append(Paragraph(
                f'<b>Story Beat:</b> {page_data["beat"]}',
                body_style
            ))

        # Description
        if 'description' in page_data:
            elements.append(Paragraph("<b>Description</b>", heading3_style))
            desc_text = page_data['description']
            if isinstance(desc_text, str):
                desc_text = desc_text.strip()
            elements.append(Paragraph(desc_text, body_style))

        # Story text (highlighted)
        if 'text' in page_data:
            elements.append(Paragraph("<b>Story Text</b>", heading3_style))
            story = page_data['text']
            if isinstance(story, str):
                story = story.strip()
            # Add background color effect through indentation and style
            elements.append(Paragraph(f"<i>{story}</i>", story_text_style))

        # Visual description
        if 'visual' in page_data:
            elements.append(Paragraph("<b>Visual Scene</b>", heading3_style))
            visual = page_data['visual']
            if isinstance(visual, str):
                visual = visual.strip()
            elements.append(Paragraph(visual, visual_style))

    # Build PDF
    doc.build(elements)

    print(f"✓ PDF generated: {output_file}")
    return output_file


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 scripts/gen_story_pdf.py <character-code>")
        print("Example: python3 scripts/gen_story_pdf.py no")
        sys.exit(1)

    char_code = sys.argv[1]
    generate_pdf(char_code)


if __name__ == '__main__':
    main()
