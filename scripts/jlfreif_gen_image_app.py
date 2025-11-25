import streamlit as st
import yaml
from pathlib import Path
from google import genai
from google.genai import types


def create_prompt(scene_data):
    """Create a text prompt for image generation from scene data."""
    prompt_parts = []

    # Meta instructions
    prompt_parts.append("Create an image for a children's story book.")
    prompt_parts.append(
        "Add the provided text to the image in a storybook style with appropriate typography and placement."
    )
    prompt_parts.append("")

    # Image description section
    visual = scene_data.get("visual", "").strip()
    if visual:
        prompt_parts.append("IMAGE DESCRIPTION:")
        prompt_parts.append(f"{visual}")
        prompt_parts.append("")

    # Image text section
    text = scene_data.get("text", "").strip()
    if text:
        prompt_parts.append("IMAGE TEXT:")
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


st.title("Storybook Image Generator")
st.write("Generate images for your storybook pages using Nano Banana Pro")

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

    # Find the specific scene for this page side
    scenes = page_data.get("scenes", [])
    selected_scene = None
    for scene in scenes:
        if scene.get("page") == page_side:
            selected_scene = scene
            break

    if selected_scene:
        st.subheader(f"Page: {page_path.name} - {page_side.capitalize()}")

        # Create and display the prompt at the top
        prompt = create_prompt(selected_scene)
        st.text_area(
            "Prompt for image generation:", value=prompt, height=300, key="prompt"
        )

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
