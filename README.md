# katha-base

Modular storybook system for creating a set of interlocking storybooks for multiple children.

## Overview

Create interconnected children's stories where each character has their own book, and characters can connect at synchronized points through **Narrative Nodes**.

### Key Concepts

- Each character is defined in a YAML file with attributes and storylines
- Characters can connect through three types of Narrative Nodes:
  - **Meeting Node**: Characters physically converge at the same place/time
  - **Mirrored Node**: Characters face parallel challenges in different places; themes rhyme
  - **Resonant Node**: Emotional ripple connects characters across distance
- Story structure follows a 12-spread arc (see `templates/story-template.yaml`)
- All content is stored as YAML files with markdown text and image prompts

### Layout System

Each story contains:
- **12 spreads** (a spread is both facing pages when you open a book)
- **2 pages per spread** (left page + right page)
- **1 image per page** (24 total images per story)
- **3-4 sentences per scene** (each page is one scene)
- Each story beat is expressed over two scenes

## Architecture

```
world.yaml (master: world lore + character links + node definitions)
    ↓
characters/cc-name.yaml (each character = one storybook)
    ↓
pages/cc-pp.yaml (individual spreads, can be shared at nodes)
    ↓
templates/meeting-node-example.yaml (node type templates)
templates/mirrored-node-example.yaml
templates/resonant-node-example.yaml
```

### Key Concept: Narrative Nodes

Characters connect through three types of Narrative Nodes:

1. **Meeting Node** - Same file shared across characters
   - Maya's book spread 7 → `le-ma-07.yaml`
   - Leo's book spread 7 → `le-ma-07.yaml` (same file!)

2. **Mirrored Node** - Separate files with linked themes
   - Maya's book spread 5 → `ma-05.yaml`
   - Leo's book spread 5 → `le-05.yaml`
   - Definition file → `mirrored-05.yaml`

3. **Resonant Node** - Emotional connection across distance
   - Similar structure to Mirrored Node
   - Must follow a character growth moment

## Getting Started

For each of these steps, just ask Claude to do it for you, and it will prompt you to get all of the relevant information. (See `.claude/claude.md` for detailed instructions.)

1. Create all your characters (suggested to do this one at a time).
2. Create the world.
3. Bind characters together by creating Narrative Nodes.
4. Create all pages for each character (one character at a time).
5. Show and critique each character's story to refine and improve it.

## Viewing Stories and Testing Consistency

### View a Character's Complete Story

To view a character's complete story with node analysis:

```bash
python3 scripts/show_story.py <character-code>
```

Examples:
- `python3 scripts/show_story.py el` - Shows Elise's story
- `python3 scripts/show_story.py no` - Shows Noah's story

The script displays all pages in order, including description, visual, and text fields, plus analysis of Narrative Nodes showing connections with other characters.

### Validate Repository Structure

To verify repository structure and that all pages are properly formatted:

```bash
python3 scripts/validate_structure.py
```

This validates:
- Page formatting (correct extensions, no path prefixes)
- All referenced pages exist
- Spreads 1, 11, and 12 are character-specific (no nodes)
- No stray pages in the pages directory
- YAML validity
- Node types are valid (solo, meeting, mirrored, resonant)
- Scene structure is present

The script exits with code 0 on success, 1 on failure, with color-coded error messages.

## Image Generation

Generate AI illustrations for story pages using the `gen_image.py` script. See [`docs/image-generation.md`](docs/image-generation.md) for complete documentation.

### New Layout Support

The image generator supports the new 1-image-per-page layout:

```bash
# Generate both pages of a spread
uv run scripts/gen_image.py openai pages/el-01.yaml

# Generate only the left page
uv run scripts/gen_image.py openai pages/el-01.yaml --scene left

# Generate only the right page
uv run scripts/gen_image.py openai pages/el-01.yaml --scene right

# Generate as a single spread (legacy mode)
uv run scripts/gen_image.py openai pages/el-01.yaml --scene spread
```

## Structure

- `world.yaml` - Master document: world lore, settings, character index, node definitions
- `characters/` - Character files (each is a storybook with attributes + page list)
- `pages/` - Individual story spreads (YAML with scene content + image prompts)
- `templates/` - Example files that serve as both templates and schemas
  - `story-template.yaml` - **SOURCE OF TRUTH** for story structure
  - `page-example.yaml` - Individual spread structure with scenes
  - `meeting-node-example.yaml` - Meeting Node template
  - `mirrored-node-example.yaml` - Mirrored Node template
  - `resonant-node-example.yaml` - Resonant Node template
- `scripts/` - Utility scripts for repository management
  - `gen_image.py` - Generate illustrations with scene selection
  - `gen_all_images.py` - Generate illustrations for all pages in parallel
  - `show_story.py` - Display a character's complete story with node analysis
  - `validate_structure.py` - Validate repository structure and formatting
- `docs/` - Additional documentation
  - `image-generation.md` - Complete guide to generating AI illustrations
- `ref-images/` - Reference images for style consistency (git-ignored except README)
- `.claude/` - Claude integration documentation

## File Naming

All lowercase with dashes:

- Characters: `ma-maya.yaml`, `le-leo.yaml`, `el-elise.yaml` (two-letter code + name)
- Solo pages: `ma-01.yaml`, `le-05.yaml`, `el-01.yaml` (character code + spread number 01-12)
- Meeting Node pages: `el-no-07.yaml`, `le-ma-07.yaml` (character codes alphabetically + spread number)
- Mirrored/Resonant definitions: `mirrored-05.yaml`, `resonant-09.yaml`

Templates serve as both examples and schemas:
- **World**: `templates/world-example.yaml` - World structure
- **Story Arc**: `templates/story-template.yaml` - **SOURCE OF TRUTH** for story structure
- **Character**: `templates/character-example.yaml` - Character structure
- **Page**: `templates/page-example.yaml` - Individual spread structure with scenes
- **Meeting Node**: `templates/meeting-node-example.yaml` - Shared scene template
- **Mirrored Node**: `templates/mirrored-node-example.yaml` - Parallel theme template
- **Resonant Node**: `templates/resonant-node-example.yaml` - Emotional connection template

## Narrative Node Types

### Meeting Node
Characters physically converge at the same place and time:
- Single shared page file
- Cross-book image alignment with POV variants
- Dialogue packets for multi-POV syncing

### Mirrored Node
Characters face parallel challenges in different places:
- Separate page files per character
- Shared theme key connects the scenes
- Symbolic motif appears in all stories
- Strict spread alignment across books

### Resonant Node
Emotional ripple connects characters across distance:
- Separate page files per character
- Emotional state packets per character
- Ripple effect describing cross-character impact
- Symbolic resonance phenomenon (sky shimmer, lantern glow, etc.)
- Must follow a moment of character growth
