import os
import uuid
import base64
from google import genai
from dotenv import load_dotenv
import requests

load_dotenv()
google_api_key = os.environ.get("GOOGLE_API_KEY")
client = genai.Client(api_key=google_api_key)

IMG_DIR = "img"
os.makedirs(IMG_DIR, exist_ok=True)

def llm_image(image_b64: str, mime_type: str = "image/png") -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {"text": "Make a better, more aesthetic rangoli (kolam) design from this image."},
            {"inline_data": {"mime_type": mime_type, "data": image_b64}}
        ]
    )

    image_base64 = None
    for candidate in response.candidates:
        for part in candidate.content.parts:
            if hasattr(part, "inline_data") and part.inline_data.mime_type.startswith("image/"):
                image_base64 = part.inline_data.data
                break

    if not image_base64:
        raise ValueError("No image could be generated")

    output_filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(IMG_DIR, output_filename)
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_base64))

    return output_filename

STABILITY_KEY = os.environ["STABILITY_API_KEY"]

def sd_image(image_b64: str, prompt: str) -> str:
    response = requests.post(
        "https://api.stability.ai/v2beta/stable-image/generate/core",
        headers={
            "Authorization": f"Bearer {STABILITY_KEY}",
            "Accept": "application/json"
        },
        files={
            "image": ("input.png", base64.b64decode(image_b64), "image/png")
        },
        data={
            "prompt": prompt,
            "mode": "image-to-image",
            "strength": 0.5
        }
    )

    if response.status_code != 200:
        raise ValueError(f"Stability API error {response.status_code}: {response.text}")

    data = response.json()

    # Stability returns images in artifacts
    artifacts = data.get("artifacts", [])
    if not artifacts or "base64" not in artifacts[0]:
        raise ValueError("No image generated")

    img_b64 = artifacts[0]["base64"]
    filename = f"{uuid.uuid4()}.png"
    output_path = os.path.join(IMG_DIR, filename)

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(img_b64))

    return filename