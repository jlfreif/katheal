# Image Generation

Generate AI illustrations for storybook pages using the `gen_image.py` script.

## Layout System

The new layout system generates **1 image per page** (not per spread):

- **12 spreads** per story
- **2 pages per spread** (left + right)
- **1 image per page** = 24 images per story
- **3-4 sentences per scene**

## Usage

### Generate a Single Spread (Both Pages)

```bash
uv run scripts/gen_image.py <model-backend> <page-path>
```

### Generate Individual Pages

```bash
# Generate only the left page
uv run scripts/gen_image.py <model-backend> <page-path> --scene left

# Generate only the right page
uv run scripts/gen_image.py <model-backend> <page-path> --scene right

# Generate both pages (default)
uv run scripts/gen_image.py <model-backend> <page-path> --scene both

# Generate as single spread image (legacy mode)
uv run scripts/gen_image.py <model-backend> <page-path> --scene spread
```

### Generate All Pages in Parallel

```bash
uv run scripts/gen_all_images.py [--workers N] [--backend MODEL]
```

## Naming Convention

Generated images follow the format: `{page-id}-{scene}-openai.jpg`

Examples:
- `el-01-left-openai.jpg` - Elise's first page, left side
- `el-01-right-openai.jpg` - Elise's first page, right side
- `no-05-left-openai.jpg` - Noah's fifth page, left side
- `el-no-07-left-openai.jpg` - Shared Meeting Node page, left side

For legacy spread mode (single image per spread):
- `el-01-openai.jpg` - Elise's first spread (both pages)

## Image Specifications

### Per-Page Images (New Layout)
- **Size**: 1024x1536 (portrait orientation)
- **Upscaled to**: 1789x2406 (with bleed)
- **Format**: JPEG (.jpg)

### Per-Spread Images (Legacy Layout)
- **Size**: 1536x1024 (landscape orientation)
- **Upscaled to**: 3579x2406 (with bleed)
- **Format**: JPEG (.jpg)

## Available Backends

- **openai** - OpenAI gpt-image-1 (recommended)
  - Uses reference images from `ref-images/` directory (up to 10 images)
  - Automatically includes character visual descriptions
  - Embeds story text as typography in the image
  - Falls back to standard generation if no reference images found
- **prompt** - Test mode (displays prompt without generating)

**Note**: The `replicate` and `ideogram` backends are deprecated and no longer functional.

## What Gets Generated

Each image includes:
1. **Reference Images** - Visual style from `ref-images/` directory
   - Style reference images (style-*.jpg) for overall aesthetic
   - Character reference images (el-*.jpg, no-*.jpg, etc.) for character appearance
2. **Visual Style** - Style description from `world.yaml`
3. **Character Visual Descriptions** - Physical descriptions from character YAML files
4. **Scene Illustration** - Visual description from the page YAML file (from `scenes` array)
5. **Story Text** - Embedded as readable typography

**Important**: Each generated image should be a single frame showing one moment in time. The visual descriptions should NOT include panels, subframes, or multiple scenes. Create one cohesive illustration per page.

## Page Format

### New Scene-Based Format

Pages now use a `scenes` array with separate visual/text for each page:

```yaml
scenes:
  - page: left
    page_number: 5
    focus: Character in ordinary world
    visual: |
      Detailed visual description for left page...
    text: |
      3-4 sentences of story text for left page...

  - page: right
    page_number: 6
    focus: First hint of something different
    visual: |
      Detailed visual description for right page...
    text: |
      3-4 sentences of story text for right page...
```

### Legacy Format (Still Supported)

Pages with single `visual` and `text` fields are still supported:

```yaml
visual: |
  Single visual description for entire spread...
text: |
  1-2 sentences for entire spread...
```

The script will generate in spread mode for legacy format pages.

## Reference Images

The script automatically includes reference images based on the page being generated:

- **Style images**: All files matching `ref-images/style-*.jpg` are always included
- **Character images**: Files matching `ref-images/{character-code}-*.jpg` are included when that character appears
  - Example: For page `el-no-07.yaml`, includes `el-*.jpg` and `no-*.jpg`

Place your reference images in the `ref-images/` directory following this naming convention.

### Character-Specific Reference Images

The image generation system automatically includes character-specific reference images to maintain visual consistency across all pages.

#### Reference Image Organization

```
ref-images/
├── style-*.jpg                  # Style references (always included)
├── no-noah-reference-01.jpg     # Noah character references
├── no-noah-reference-02.png
├── el-elise-reference-01.jpg    # Elise character references
├── el-elise-outfit.png
└── [character-code]-*.{jpg,png}  # Pattern for any character
```

#### How It Works

1. **Automatic Detection**: The script extracts the character code from the page filename (e.g., `no-01.yaml` → character code `no`)

2. **Pattern Matching**: It looks for reference images matching these patterns:
   - `{char-code}-*.jpg` (e.g., `no-*.jpg`, `el-*.jpg`)
   - `{CHAR-CODE}-*.jpg` (case insensitive)
   - Any image file containing the character code

3. **File Formats Supported**:
   - `.jpg` / `.jpeg`
   - `.png`

4. **Inclusion in Prompt**: Reference images are automatically added to the generation prompt with descriptions like:
   ```
   REFERENCE IMAGES FOR NO:
   Use these images for character consistency:
   - no-noah-reference-01.jpg
   - no-noah-outfit.png
   ```

#### Adding New Character References

To add reference images for a new character:

1. Create visual reference images (photos, illustrations, or sketches) showing:
   - Facial features and expressions
   - Clothing and outfit details
   - Hair style and color
   - Body proportions
   - Typical poses or gestures

2. Save them in `ref-images/` with the naming pattern:
   - `{character-code}-{description}.{jpg|png}`
   - Example: `no-casual-outfit.jpg`, `el-painting-pose.png`

3. The next time you generate images for that character, these references will be automatically included

#### Character Codes

Current character codes:
- `no` - Noah (story character)
- `el` - Elise (color character)

Add more as new characters are introduced to the series.

#### Best Practices

- **Consistency**: Use the same style/medium for all reference images
- **Clarity**: High-quality, well-lit images work best
- **Variety**: Include multiple angles and expressions
- **Naming**: Use descriptive names (e.g., `no-happy-expression.jpg`, `no-winter-outfit.png`)
- **Updates**: Replace or add references as the visual style evolves
- **Documentation**: See `docs/visual_style.md` for complete illustration guidelines

## Setup

1. Copy `.env.example` to `.env`
2. Add your API key:
   - `OPENAI_API_KEY` - For OpenAI backend
3. Add reference images to `ref-images/` directory (optional but recommended)

## Examples

```bash
# Generate both pages of a spread (new layout)
uv run scripts/gen_image.py openai pages/el-01.yaml

# Generate only the left page
uv run scripts/gen_image.py openai pages/el-01.yaml --scene left

# Generate only the right page
uv run scripts/gen_image.py openai pages/el-01.yaml --scene right

# Generate as single spread (legacy mode)
uv run scripts/gen_image.py openai pages/el-01.yaml --scene spread

# Generate all pages with default settings (5 workers)
uv run scripts/gen_all_images.py

# Generate all pages with 10 concurrent workers
uv run scripts/gen_all_images.py --workers 10

# Test mode - show prompt without generating
uv run scripts/gen_image.py prompt pages/el-no-04.yaml
```

## Output Location

All generated images are saved to the `out-images/` directory and are git-ignored (not committed to the repository). Each user generates their own images using their API keys.

## Node Types and Image Generation

### Meeting Node Pages
- Shared page file between characters (e.g., `el-no-04.yaml`)
- Same visual scene from different POVs
- Image alignment metadata in page file specifies POV variants

### Mirrored Node Pages
- Separate page files per character
- Same symbolic motif should appear in all related images
- Strict spread alignment across books

### Resonant Node Pages
- Separate page files per character
- Symbolic resonance phenomenon (sky shimmer, golden threads) should be visible
- Creates visual connection between related scenes
