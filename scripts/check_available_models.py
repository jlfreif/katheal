"""Check what models are available with the current API key."""

from google import genai
import os
from pathlib import Path

# Try to load API key from secrets.toml
secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
if secrets_path.exists():
    import toml
    secrets = toml.load(secrets_path)
    api_key = secrets["google"]["api_key"]
else:
    print("Error: .streamlit/secrets.toml not found")
    exit(1)

# Initialize client
client = genai.Client(api_key=api_key)

print("Fetching available models...\n")

# List all models
try:
    models = client.models.list()

    print("=" * 80)
    print("ALL AVAILABLE MODELS:")
    print("=" * 80)

    image_models = []
    other_models = []

    for model in models:
        model_name = model.name
        display_name = getattr(model, 'display_name', 'N/A')
        supported_methods = getattr(model, 'supported_generation_methods', [])

        # Check if it's an image model
        if 'image' in model_name.lower() or 'imagen' in model_name.lower():
            image_models.append((model_name, display_name, supported_methods))
        else:
            other_models.append((model_name, display_name, supported_methods))

    if image_models:
        print("\n🎨 IMAGE GENERATION MODELS:")
        print("-" * 80)
        for name, display, methods in image_models:
            print(f"  Model: {name}")
            print(f"  Display Name: {display}")
            print(f"  Supported Methods: {methods}")
            print()
    else:
        print("\n❌ NO IMAGE GENERATION MODELS FOUND")
        print("This means Imagen 3 is not available with your current API key.")

    print("\n📝 OTHER MODELS:")
    print("-" * 80)
    for name, display, methods in other_models[:10]:  # Show first 10
        print(f"  Model: {name}")
        if display != 'N/A':
            print(f"  Display Name: {display}")
        print()

    if len(other_models) > 10:
        print(f"  ... and {len(other_models) - 10} more models")

    print("\n" + "=" * 80)
    print(f"TOTAL MODELS: {len(image_models) + len(other_models)}")
    print(f"IMAGE MODELS: {len(image_models)}")
    print("=" * 80)

except Exception as e:
    print(f"Error listing models: {e}")
