import streamlit as st
import yaml
from pathlib import Path
from google import genai
from google.genai import types
import io
import zipfile


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

# Initialize session state for storing generated images
if 'generated_images' not in st.session_state:
    st.session_state.generated_images = []

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

# Build a list of (display_name, file_path, page_side, page_data) tuples
page_options = []
for page_file in page_files:
    with open(page_file, "r") as f:
        page_data = yaml.safe_load(f)

    scenes = page_data.get("scenes", [])
    for scene in scenes:
        page_side = scene.get("page", "unknown")
        display_name = f"{page_file.stem} - {page_side}"
        page_options.append((display_name, page_file, page_side, page_data))

# Debug toggle
show_debug = st.checkbox("Show debug output", value=False)

if show_debug:
    st.write(f"🔍 DEBUG: Built {len(page_options)} page options")
    st.write("First 5 page options:")
    for i, (name, path, side, data) in enumerate(page_options[:5]):
        st.write(f"  {i}: {name} -> {path.name} (id: {data.get('id', 'N/A')})")

if not page_options:
    st.error("No pages found in the pages/ directory")
else:
    # Select multiple pages
    display_names = [opt[0] for opt in page_options]
    selected_displays = st.multiselect(
        "Select pages to generate (choose one or more):",
        display_names,
        default=[display_names[0]] if display_names else []
    )

    if not selected_displays:
        st.warning("Please select at least one page to generate images.")
    else:
        st.success(f"📚 {len(selected_displays)} page(s) selected for generation")

        # Global settings for all pages
        st.divider()
        st.subheader("Generation Settings")
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

        # Gen images button
        if st.button("Generate All Images", type="primary", use_container_width=True):
            model_display = "Nano Banana Pro" if "3-pro" in model else "Nano Banana Flash"

            # Clear previous images
            st.session_state.generated_images = []

            # Process each selected page
            for page_idx, selected_display in enumerate(selected_displays):
                st.divider()
                st.header(f"Page {page_idx + 1}/{len(selected_displays)}: {selected_display}")

                # Find the selected page data
                selected_option_idx = display_names.index(selected_display)
                _, page_path, page_side, page_data = page_options[selected_option_idx]

                if show_debug:
                    st.info(f"🔍 DEBUG: Selected '{selected_display}' (index: {selected_option_idx})")
                    st.info(f"🔍 DEBUG: Page path: {page_path.name}")
                    st.info(f"🔍 DEBUG: Page side: {page_side}")
                    st.info(f"🔍 DEBUG: Page ID from YAML: {page_data.get('id', 'NOT FOUND')}")

                # Get character codes from page filename
                char_codes = get_character_codes_from_page(page_path.name)
                if show_debug:
                    st.info(f"🔍 DEBUG: Extracted character codes: {char_codes}")

                # Load character-specific references
                char_ref_images = get_character_reference_images(char_codes)
                character_descriptions = load_character_descriptions(char_codes)

                if show_debug:
                    st.info(f"🔍 DEBUG: Character descriptions loaded: {list(character_descriptions.keys())}")
                    if character_descriptions:
                        for char_name, desc in character_descriptions.items():
                            st.write(f"   - {char_name}: {len(desc)} visual attributes")

                # Find the specific scene for this page side
                scenes = page_data.get("scenes", [])
                if show_debug:
                    st.info(f"🔍 DEBUG: Total scenes in page_data: {len(scenes)}")
                    for idx, scene in enumerate(scenes):
                        st.write(f"   Scene {idx}: page='{scene.get('page')}' (looking for '{page_side}')")

                selected_scene = None
                for scene in scenes:
                    if scene.get("page") == page_side:
                        selected_scene = scene
                        break

                if show_debug:
                    st.info(f"🔍 DEBUG: Selected scene found: {selected_scene is not None}")

                if not selected_scene:
                    st.error(f"Could not find scene for {page_side} page in {page_path.name}")
                    continue

                # Show character info if available
                if char_codes:
                    st.info(f"Characters: {', '.join([c.upper() for c in char_codes])}")

                if show_debug:
                    visual_preview = selected_scene.get("visual", "")[:100] + "..." if len(selected_scene.get("visual", "")) > 100 else selected_scene.get("visual", "")
                    text_preview = selected_scene.get("text", "")[:100] + "..." if len(selected_scene.get("text", "")) > 100 else selected_scene.get("text", "")
                    st.info(f"🔍 DEBUG: Scene visual preview: {visual_preview}")
                    st.info(f"🔍 DEBUG: Scene text preview: {text_preview}")

                # Create the enhanced prompt
                prompt = create_enhanced_prompt(
                    selected_scene,
                    visual_style,
                    character_descriptions,
                    char_ref_images,
                    style_refs
                )

                if show_debug:
                    prompt_scene_section = prompt[prompt.find("--- SCENE TO ILLUSTRATE ---"):prompt.find("--- SCENE TO ILLUSTRATE ---")+150] if "--- SCENE TO ILLUSTRATE ---" in prompt else "NOT FOUND"
                    st.write(f"🔍 DEBUG: Prompt SCENE section preview: {prompt_scene_section}")

                # Show prompt in expander
                with st.expander("View Prompt"):
                    st.text_area(
                        "Prompt for image generation:",
                        value=prompt,
                        height=300,
                        key=f"prompt_{page_idx}_{selected_display}"
                    )

                # Generate image
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

                    # Store and display the generated images
                    for idx, image_part in enumerate(generated_images):
                        # Get the image object and access its PIL representation
                        img_obj = image_part.as_image()
                        pil_image = img_obj._pil_image

                        # Store in session state
                        file_safe_name = selected_display.replace(" ", "_").replace("/", "-")
                        st.session_state.generated_images.append({
                            'image': pil_image,
                            'page_name': selected_display,
                            'file_name': f"{file_safe_name}_img{idx + 1}.png",
                            'aspect_ratio': aspect_ratio,
                            'model': model_display,
                            'page_idx': page_idx,
                            'img_idx': idx
                        })
                else:
                    st.warning("No images were generated. Please try again.")

            # All done
            st.divider()
            st.success(f"🎉 Completed generation for all {len(selected_displays)} page(s)!")
            st.balloons()

        # Display all generated images (persists across reruns)
        if st.session_state.generated_images:
            st.divider()
            st.header("Generated Images")

            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"Total images generated: {len(st.session_state.generated_images)}")
            with col2:
                if st.button("🗑️ Clear All", type="secondary"):
                    st.session_state.generated_images = []
                    st.rerun()

            # Create ZIP file with all images
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for img_data in st.session_state.generated_images:
                    img_buffer = io.BytesIO()
                    img_data['image'].save(img_buffer, format='PNG')
                    zip_file.writestr(img_data['file_name'], img_buffer.getvalue())

            # Download all button
            st.download_button(
                label="📦 Download All Images as ZIP",
                data=zip_buffer.getvalue(),
                file_name="storybook_images.zip",
                mime="application/zip",
                type="primary",
                use_container_width=True
            )

            st.divider()

            # Display each image with individual download button
            for img_data in st.session_state.generated_images:
                st.subheader(f"{img_data['page_name']} - Image {img_data['img_idx'] + 1}")

                st.image(
                    img_data['image'],
                    caption=f"{img_data['aspect_ratio']} - {img_data['model']}",
                    use_container_width=True,
                )

                # Individual download button
                img_buffer = io.BytesIO()
                img_data['image'].save(img_buffer, format='PNG')
                st.download_button(
                    label=f"Download {img_data['page_name']} - Image {img_data['img_idx'] + 1}",
                    data=img_buffer.getvalue(),
                    file_name=img_data['file_name'],
                    mime="image/png",
                    key=f"download_{img_data['page_idx']}_{img_data['img_idx']}_persistent"
                )

        # Preview section for selected pages (before generation)
        else:
            st.divider()
            st.subheader("Preview Selected Pages")
            for page_idx, selected_display in enumerate(selected_displays):
                # Find the selected page data
                selected_option_idx = display_names.index(selected_display)
                _, page_path, page_side, page_data = page_options[selected_option_idx]

                # Get character codes
                char_codes = get_character_codes_from_page(page_path.name)
                char_ref_images = get_character_reference_images(char_codes)
                character_descriptions = load_character_descriptions(char_codes)

                # Display character reference images in sidebar
                if char_ref_images and page_idx == 0:  # Only show for first page to avoid clutter
                    with st.sidebar:
                        st.subheader("👤 Character References")
                        for char_code, images in char_ref_images.items():
                            st.write(f"**{char_code.upper()}**")
                            for img_path in images:
                                st.image(str(img_path), caption=img_path.name, use_container_width=True)

                # Find the scene
                scenes = page_data.get("scenes", [])
                selected_scene = None
                for scene in scenes:
                    if scene.get("page") == page_side:
                        selected_scene = scene
                        break

                if selected_scene:
                    with st.expander(f"📄 {selected_display}", expanded=(page_idx == 0)):
                        st.write(f"**Characters:** {', '.join([c.upper() for c in char_codes])}" if char_codes else "No characters")

                        # Show scene text preview
                        text_preview = selected_scene.get("text", "").strip()
                        if text_preview:
                            st.write("**Text:**")
                            st.write(text_preview[:200] + "..." if len(text_preview) > 200 else text_preview)

                        # Show visual description preview
                        visual_preview = selected_scene.get("visual", "").strip()
                        if visual_preview:
                            st.write("**Visual Description:**")
                            st.write(visual_preview[:200] + "..." if len(visual_preview) > 200 else visual_preview)

                        # Show parsed YAML
                        with st.expander("View Full YAML"):
                            st.json(selected_scene)
                else:
                    st.error(f"Could not find scene for {selected_display}")
