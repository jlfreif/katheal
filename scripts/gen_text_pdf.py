#!/usr/bin/env python3
"""
Generate a text-only PDF for a character's story.
Usage: python scripts/gen_text_pdf.py <character-code>
Example: python scripts/gen_text_pdf.py no
"""

import sys
import yaml
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER

def load_character(char_code):
    """Load character data from YAML file."""
    char_file = Path(f"characters/{char_code}-*.yaml")
    matches = list(Path("characters").glob(f"{char_code}-*.yaml"))

    if not matches:
        print(f"Error: No character file found for code '{char_code}'")
        sys.exit(1)

    with open(matches[0], 'r') as f:
        return yaml.safe_load(f)

def load_page(page_filename):
    """Load page data from YAML file."""
    page_path = Path("pages") / page_filename

    if not page_path.exists():
        print(f"Warning: Page file not found: {page_filename}")
        return None

    with open(page_path, 'r') as f:
        return yaml.safe_load(f)

def get_node_type_name(node_type):
    """Convert node type to display name with emoji."""
    node_types = {
        'solo': '👤 Solo',
        'meeting': '🤝 Meeting',
        'mirrored': '🪞 Mirrored',
        'resonant': '✨ Resonant'
    }
    return node_types.get(node_type, node_type.title())

def create_pdf(char_code, output_path):
    """Create a PDF with the character's story text."""
    # Load character data
    char_data = load_character(char_code)
    char_name = char_data.get('attributes', {}).get('name', char_code.upper())
    story_pages = char_data.get('story', [])

    # Create PDF document
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    # Define styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2C3E50',
        spaceAfter=30,
        alignment=TA_CENTER
    )

    spread_style = ParagraphStyle(
        'SpreadHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor='#34495E',
        spaceAfter=12,
        spaceBefore=20
    )

    page_style = ParagraphStyle(
        'PageHeading',
        parent=styles['Heading3'],
        fontSize=14,
        textColor='#555555',
        spaceAfter=10,
        spaceBefore=15
    )

    node_style = ParagraphStyle(
        'NodeType',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#7F8C8D',
        spaceAfter=8
    )

    image_heading_style = ParagraphStyle(
        'ImageHeading',
        parent=styles['Heading4'],
        fontSize=12,
        textColor='#666666',
        spaceAfter=6,
        spaceBefore=10
    )

    text_style = ParagraphStyle(
        'StoryText',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        spaceAfter=12,
        leftIndent=10
    )

    description_style = ParagraphStyle(
        'Description',
        parent=styles['Italic'],
        fontSize=10,
        textColor='#555555',
        spaceAfter=10,
        leftIndent=10
    )

    # Build content
    content = []

    # Title page
    content.append(Paragraph(f"{char_name}'s Story", title_style))
    content.append(Spacer(1, 0.3*inch))
    content.append(Paragraph(f"Character Code: {char_code}", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    content.append(Paragraph(f"Total Pages: {len(story_pages)}", styles['Normal']))
    content.append(PageBreak())

    # Process each page
    current_spread = None

    for page_filename in story_pages:
        page_data = load_page(page_filename)

        if not page_data:
            continue

        page_id = page_data.get('id', 'unknown')
        spread = page_data.get('spread', 0)
        page_num = page_data.get('page', 0)
        node_type = page_data.get('node_type', 'unknown')
        description = page_data.get('description', '')

        # Add spread heading if new spread
        if spread != current_spread:
            if current_spread is not None:
                content.append(Spacer(1, 0.2*inch))
            content.append(Paragraph(f"Spread {spread} (Pages {spread*2-1}-{spread*2})", spread_style))
            current_spread = spread

        # Page heading
        content.append(Paragraph(f"Page {page_id}", page_style))
        content.append(Paragraph(f"Node Type: {get_node_type_name(node_type)}", node_style))

        # Description
        if description:
            content.append(Paragraph(f"<i>{description}</i>", description_style))

        content.append(Spacer(1, 0.1*inch))

        # Process images
        images = page_data.get('images', [])

        for img in images:
            img_num = img.get('image_number', 0)
            text = img.get('text', '').strip()

            # Image heading
            content.append(Paragraph(f"Image {img_num}", image_heading_style))

            # Story text
            if text:
                # Clean up text for PDF
                text_clean = text.replace('\n', ' ').replace('  ', ' ')
                content.append(Paragraph(text_clean, text_style))

            content.append(Spacer(1, 0.1*inch))

        # Add space between pages
        content.append(Spacer(1, 0.15*inch))

    # Build PDF
    doc.build(content)
    print(f"PDF created: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/gen_text_pdf.py <character-code>")
        print("Example: python scripts/gen_text_pdf.py no")
        sys.exit(1)

    char_code = sys.argv[1]
    output_path = f"{char_code}-story-text.pdf"

    create_pdf(char_code, output_path)

if __name__ == "__main__":
    main()
