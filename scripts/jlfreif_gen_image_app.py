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


def generate_image_with_imagen(prompt, aspect_ratio="16:9", num_images=1, model="imagen-4.0-generate-001"):
    """Generate an image using Google Imagen 4."""
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets["google"]["api_key"]

        # Initialize the client
        client = genai.Client(api_key=api_key)

        # Generate images
        st.write(f"🔄 Calling model: {model}")
        st.write(f"📝 Prompt length: {len(prompt)} characters")
        st.write(f"📐 Aspect ratio: {aspect_ratio}, Count: {num_images}")

        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=num_images,
                aspect_ratio=aspect_ratio,
            )
        )

        st.write(f"✅ Response received: {type(response)}")
        st.write(f"Generated images count: {len(response.generated_images) if response.generated_images else 0}")

        # Debug: Show full response structure
        st.write("📋 Response attributes:", dir(response))
        st.write("📋 Full response:", response)

        if response.generated_images:
            st.write(f"First image type: {type(response.generated_images[0])}")
            # Check for filtered reasons
            for idx, img in enumerate(response.generated_images):
                if hasattr(img, 'raiFilteredReason') and img.raiFilteredReason:
                    st.warning(f"Image {idx + 1} was filtered: {img.raiFilteredReason}")
        else:
            st.warning("⚠️ No images returned - possibly filtered by content safety")

        return response.generated_images
    except Exception as e:
        st.error(f"❌ Error generating image: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None


st.title("Storybook Image Generator")
st.write("Generate images for your storybook pages using Imagen 4")

# Get all page files and create a list of individual pages
pages_dir = Path("pages")
page_files = sorted(pages_dir.glob("*.yaml"))

# Build a list of (display_name, file_path, page_side) tuples
page_options = []
for page_file in page_files:
    try:
        with open(page_file, "r") as f:
            page_data = yaml.safe_load(f)

        scenes = page_data.get("scenes", [])
        for scene in scenes:
            page_side = scene.get("page", "unknown")
            display_name = f"{page_file.stem} - {page_side}"
            page_options.append((display_name, page_file, page_side, page_data))
    except Exception as e:
        st.warning(f"Could not load {page_file.name}: {e}")

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
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["1:1", "3:4", "4:3", "9:16", "16:9"],
                index=4,  # Default to 16:9
            )
        with col2:
            model = st.selectbox(
                "Imagen Model",
                ["imagen-4.0-generate-001", "imagen-4.0-fast-generate-001", "imagen-4.0-ultra-generate-001"],
                format_func=lambda x: x.replace("imagen-4.0-", "").replace("-001", "").replace("-", " ").title(),
                index=0,  # Default to standard
            )
        with col3:
            num_images = st.number_input(
                "Images", min_value=1, max_value=4, value=1
            )

        # Gen image button
        if st.button("Gen image", type="primary", use_container_width=True):
            model_display = model.replace("imagen-4.0-", "").replace("-001", "").replace("-", " ").title()
            with st.spinner(f"Generating with Imagen 4 {model_display}..."):
                generated_images = generate_image_with_imagen(
                    prompt, aspect_ratio=aspect_ratio, num_images=num_images, model=model
                )

                if generated_images and len(generated_images) > 0:
                    st.success(f"✅ Successfully generated {len(generated_images)} image(s)!")
                    st.balloons()

                    # Display the generated images
                    for idx, generated_image in enumerate(generated_images):
                        st.subheader(f"Generated Image {idx + 1}")
                        try:
                            # Convert the image to PIL format for display
                            from PIL import Image as PILImage
                            import io

                            # Get the image data
                            img_data = generated_image.image._pil_image

                            st.image(
                                img_data,
                                caption=f"{aspect_ratio} - {model_display}",
                                use_container_width=True,
                            )
                        except AttributeError:
                            # Try alternative method if _pil_image doesn't exist
                            try:
                                # Try to get bytes directly
                                img_bytes = generated_image.image._image_bytes
                                st.image(
                                    img_bytes,
                                    caption=f"{aspect_ratio} - {model_display}",
                                    use_container_width=True,
                                )
                            except Exception as e2:
                                st.error(f"Error displaying image {idx + 1}: {e2}")
                                st.write("Available attributes:", dir(generated_image.image))
                        except Exception as e:
                            st.error(f"Error displaying image {idx + 1}: {e}")
                            st.write("Available attributes:", dir(generated_image.image))
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
