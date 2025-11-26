import streamlit as st
import yaml
from pathlib import Path
from google import genai
from google.genai import types


def load_visual_style():
    """Load the visual style from world.yaml."""
    world_path = Path("world.yaml")

    if not world_path.exists():
        return ""

    try:
        with open(world_path, "r") as f:
            world_data = yaml.safe_load(f)
    except Exception as e:
        st.warning(f"Failed to load world.yaml: {e}")
        return ""

    visual_style = world_data.get("visual_style", [])
    if visual_style:
        return "\n".join(f"- {item}" for item in visual_style)
    return ""


def get_character_codes_from_page(page_filename):
    """
    Extract character codes from page filename.
    Examples: el-01.yaml -> ['el'], no-01.yaml -> ['no'], el-no-04.yaml -> ['el', 'no']
    """
    # Remove .yaml extension and get the stem
    stem = page_filename.replace('.yaml', '')

    # Split by hyphen
    parts = stem.split('-')

    # Character codes are 2-letter alphabetic parts
    char_codes = []
    for part in parts:
        if len(part) == 2 and part.isalpha():
            char_codes.append(part)

    return char_codes


def get_character_reference_images(character_codes):
    """
    Get reference images for specific characters.
    Returns dict mapping character code to list of image paths.
    """
    ref_dir = Path("ref-images")
    if not ref_dir.exists():
        return {}

    character_refs = {}

    for char_code in character_codes:
        refs = []

        # Look for images matching character code patterns
        for ext in ['jpg', 'png', 'jpeg']:
            refs.extend(ref_dir.glob(f"{char_code}-*.{ext}"))
            refs.extend(ref_dir.glob(f"{char_code.upper()}-*.{ext}"))
            refs.extend(ref_dir.glob(f"ref-{char_code}-*.{ext}"))
            refs.extend(ref_dir.glob(f"ref-{char_code.upper()}-*.{ext}"))

        # Remove duplicates
        refs = list(set(refs))

        if refs:
            character_refs[char_code] = sorted(refs)

    return character_refs


def get_style_reference_images():
    """Get style reference images."""
    ref_dir = Path("ref-images")
    if not ref_dir.exists():
        return []

    style_refs = []
    for ext in ['jpg', 'png', 'jpeg']:
        style_refs.extend(ref_dir.glob(f"style-*.{ext}"))

    return sorted(style_refs)


def load_character_descriptions(character_codes):
    """
    Load visual descriptions for characters.
    Returns dict mapping character names to their visual descriptions.
    """
    char_dir = Path("characters")
    if not char_dir.exists():
        return {}

    character_descriptions = {}

    for char_code in character_codes:
        # Try to find matching character file
        for char_file in char_dir.glob("*.yaml"):
            if 'template' in char_file.name or 'example' in char_file.name:
                continue

            try:
                with open(char_file, 'r') as f:
                    char_data = yaml.safe_load(f)

                # Check if this is the right character
                if char_data.get('id') == char_code:
                    char_name = char_data.get('attributes', {}).get('name', char_code.upper())
                    visual_desc = char_data.get('attributes', {}).get('visual_description', [])

                    if visual_desc:
                        character_descriptions[char_name] = visual_desc
                    break
            except:
                continue

    return character_descriptions


def create_enhanced_prompt(scene_data, visual_style, character_descriptions, char_ref_images, style_ref_images):
    """Create an enhanced prompt including visual style, character descriptions, and reference image info."""
    prompt_parts = []

    # Meta instructions
    prompt_parts.append("Create an image for a children's story book.")
    prompt_parts.append(
        "Add the provided text to the image in a storybook style with appropriate typography and placement."
    )
    prompt_parts.append("")

    # Add visual style
    if visual_style:
        prompt_parts.append("--- VISUAL STYLE ---")
        prompt_parts.append(visual_style)
        prompt_parts.append("")

    # Add character descriptions
    if character_descriptions:
        prompt_parts.append("--- CHARACTER VISUAL DESCRIPTIONS ---")
        for char_name, desc_list in character_descriptions.items():
            prompt_parts.append(f"\n{char_name}:")
            for item in desc_list:
                prompt_parts.append(f"- {item}")
        prompt_parts.append("")

    # Add reference image information
    if char_ref_images or style_ref_images:
        prompt_parts.append("--- REFERENCE IMAGES ---")
        prompt_parts.append("The following reference images should guide the visual style and character appearance:")
        prompt_parts.append("")

        if char_ref_images:
            prompt_parts.append("CHARACTER REFERENCES:")
            for char_code, images in char_ref_images.items():
                prompt_parts.append(f"  {char_code.upper()} character:")
                for img_path in images:
                    prompt_parts.append(f"    - {img_path.name}")
            prompt_parts.append("")

        if style_ref_images:
            prompt_parts.append("STYLE REFERENCES:")
            for img_path in style_ref_images:
                prompt_parts.append(f"  - {img_path.name}")
            prompt_parts.append("")

    # Image description section
    visual = scene_data.get("visual", "").strip()
    if visual:
        prompt_parts.append("--- SCENE TO ILLUSTRATE ---")
        prompt_parts.append(f"{visual}")
        prompt_parts.append("")

    # Image text section
    text = scene_data.get("text", "").strip()
    if text:
        prompt_parts.append("--- TEXT TO INCLUDE IN IMAGE ---")
        prompt_parts.append(f"{text}")

    return "\n".join(prompt_parts)


@st.cache_data(show_spinner=False)
def generate_image_with_gemini(prompt, aspect_ratio="16:9", model="gemini-3-pro-image-preview"):
    """Generate an image using Google Gemini Nano Banana Pro."""
    # Get API key from Streamlit secrets
    api_key = st.secrets["google"]["api_key"]

    # Initialize the client
    client = genai.Client(api_key=api_key)

    # Generate image
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['IMAGE'],
            image_config=types.ImageConfig(
                aspect_ratio=aspect_ratio,
            )
        )
    )

    # Extract images from response parts
    images = []
    for part in response.parts:
        if part.inline_data:
            images.append(part)

    return images


# App title and description
st.title("Storybook Image Generator")
st.write("Generate images for your storybook pages using Nano Banana Pro")

# Sidebar for reference images and style
with st.sidebar:
    st.header("Reference Materials")

    # Load visual style
    visual_style = load_visual_style()

    # Visual style expander
    if visual_style:
        with st.expander("📖 Visual Style Guide", expanded=False):
            st.markdown(visual_style)

    # Style reference images
    style_refs = get_style_reference_images()
    if style_refs:
        st.subheader("🎨 Style References")
        for img_path in style_refs:
            st.image(str(img_path), caption=img_path.name, use_container_width=True)
    else:
        st.info("No style reference images found (style-*.jpg)")

# Get all page files and create a list of individual pages
pages_dir = Path("pages")
page_files = sorted(pages_dir.glob("*.yaml"))

# Build a list of (display_name, file_path, page_side) tuples
page_options = []
for page_file in page_files:
    with open(page_file, "r") as f:
        page_data = yaml.safe_load(f)

    scenes = page_data.get("scenes", [])
    for scene in scenes:
        page_side = scene.get("page", "unknown")
        display_name = f"{page_file.stem} - {page_side}"
        page_options.append((display_name, page_file, page_side, page_data))

if not page_options:
    st.error("No pages found in the pages/ directory")
else:
    # Select a page
    display_names = [opt[0] for opt in page_options]
    selected_display = st.selectbox("Select a page:", display_names, index=0)

    # Find the selected page data
    selected_idx = display_names.index(selected_display)
    _, page_path, page_side, page_data = page_options[selected_idx]

    # Get character codes from page filename
    char_codes = get_character_codes_from_page(page_path.name)

    # Load character-specific references
    char_ref_images = get_character_reference_images(char_codes)
    character_descriptions = load_character_descriptions(char_codes)

    # Display character reference images in sidebar
    if char_ref_images:
        with st.sidebar:
            st.subheader("👤 Character References")
            for char_code, images in char_ref_images.items():
                st.write(f"**{char_code.upper()}**")
                for img_path in images:
                    st.image(str(img_path), caption=img_path.name, use_container_width=True)

    # Find the specific scene for this page side
    scenes = page_data.get("scenes", [])
    selected_scene = None
    for scene in scenes:
        if scene.get("page") == page_side:
            selected_scene = scene
            break

    if selected_scene:
        st.subheader(f"Page: {page_path.name} - {page_side.capitalize()}")

        # Show character info if available
        if char_codes:
            st.info(f"Characters in this page: {', '.join([c.upper() for c in char_codes])}")

        # Create and display the enhanced prompt
        prompt = create_enhanced_prompt(
            selected_scene,
            visual_style,
            character_descriptions,
            char_ref_images,
            style_refs
        )

        st.text_area(
            "Prompt for image generation:", value=prompt, height=400, key="prompt"
        )

        # Character descriptions expander
        if character_descriptions:
            with st.expander("View Character Descriptions"):
                for char_name, desc_list in character_descriptions.items():
                    st.write(f"**{char_name}:**")
                    for item in desc_list:
                        st.write(f"- {item}")

        # Image generation controls
        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["1:1", "3:4", "4:3", "9:16", "16:9"],
                index=3,  # Default to 9:16
            )
        with col2:
            model = st.selectbox(
                "Model",
                ["gemini-3-pro-image-preview", "gemini-2.5-flash-image"],
                format_func=lambda x: "Nano Banana Pro" if "3-pro" in x else "Nano Banana Flash",
                index=0,  # Default to Pro
            )

        # Gen image button
        if st.button("Gen image", type="primary", use_container_width=True):
            model_display = "Nano Banana Pro" if "3-pro" in model else "Nano Banana Flash"

            # Create a status expander for logs
            with st.status(f"Generating with {model_display}...", expanded=True) as status:
                st.write(f"🔄 Calling model: {model}")
                st.write(f"📝 Prompt length: {len(prompt)} characters")
                st.write(f"📐 Aspect ratio: {aspect_ratio}")

                if char_ref_images:
                    total_refs = sum(len(imgs) for imgs in char_ref_images.values())
                    st.write(f"👤 Character references: {total_refs} image(s)")

                if style_refs:
                    st.write(f"🎨 Style references: {len(style_refs)} image(s)")

                generated_images = generate_image_with_gemini(
                    prompt, aspect_ratio=aspect_ratio, model=model
                )

                st.write(f"✅ Response received")
                st.write(f"Generated images count: {len(generated_images)}")

                if generated_images:
                    st.write(f"First image type: {type(generated_images[0])}")
                    status.update(label=f"✅ Generation complete!", state="complete")
                else:
                    status.update(label="⚠️ No images generated", state="error")

            if generated_images and len(generated_images) > 0:
                st.success(f"✅ Successfully generated {len(generated_images)} image(s)!")
                st.balloons()

                # Display the generated images
                for idx, image_part in enumerate(generated_images):
                    st.subheader(f"Generated Image {idx + 1}")

                    # Get the image object and access its PIL representation
                    img_obj = image_part.as_image()

                    # Access the actual PIL image from the Image object
                    pil_image = img_obj._pil_image

                    st.image(
                        pil_image,
                        caption=f"{aspect_ratio} - {model_display}",
                        use_container_width=True,
                    )

                    # Option to save the image
                    import io
                    buf = io.BytesIO()
                    pil_image.save(buf, format='PNG')
                    st.download_button(
                        label=f"Download Image {idx + 1}",
                        data=buf.getvalue(),
                        file_name=f"generated_image_{idx + 1}.png",
                        mime="image/png"
                    )
            else:
                st.warning("No images were generated. Please try again.")

        st.divider()

        # Display the YAML content in an expander
        with st.expander("View parsed YAML"):
            st.json(selected_scene)

        # Show the raw YAML in an expander
        with st.expander("View raw YAML file"):
            with open(page_path, "r") as f:
                st.code(f.read(), language="yaml")
    else:
        st.error(f"Could not find scene for {page_side} page")
