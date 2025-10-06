
import json
import os
import uuid
import base64
from google import genai
from dotenv import load_dotenv
import requests
import re
from src.api.schemas import KolamRequest

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

def llm_prompt(prompt: str, model_name: str = "gemini-2.5-flash") -> str:
    try:
        response = client.models.generate_content(
            model=model_name, contents=prompt
        )
        return response.text.strip() if hasattr(response, "text") else str(response)
    except Exception as e:
        print(f"⚠️ LLM Error: {e}")
        return json.dumps({"error": str(e)})


def llm_prompt_for_kolam(kolam_json: dict) -> dict:
    """
    Uses Gemini to enhance a Kolam JSON while guaranteeing schema conformity.
    Returns a dict matching KolamRequest schema.
    """
    prompt = f"""
You are a geometry-aware AI artist specializing in Kolam (symmetric geometric art).

Your task:
Improve the given Kolam design into a more aesthetic, symmetric, and flower-like pattern 
Incorporate both curved and straight paths to achieve a visually pleasing and balanced pattern.

### Output Schema (STRICT)
Return ONLY a valid JSON object that exactly matches this schema — no markdown, code fences, or explanation.

KolamRequest:
{{
  "dots": [{{"x": float, "y": float}}],
  "paths": [
    {{
      "type": "line",
      "p1": {{"x": float, "y": float}},
      "p2": {{"x": float, "y": float}}
    }},
    {{
      "type": "curve",
      "p1": {{"x": float, "y": float}},
      "ctrl": {{"x": float, "y": float}},
      "p2": {{"x": float, "y": float}}
    }}
  ]
}}

### Rules
- Use symmetry around the center (both X and Y axes).
- Dots should roughly form concentric layers or petals.
- Curves should create flower-like arcs connecting nearby dots.
- Keep structure consistent and renderable (no missing keys or invalid coordinates).
- Use absolute numeric coordinates only.
- Do NOT include any explanations, markdown, comments, or code fences.
- Output must be directly parseable with `json.loads()`.

### Input Kolam
{json.dumps(kolam_json, indent=2)}

Now return ONLY the improved JSON object:
"""

    try:
        llm_text = llm_prompt(prompt)

        # Step 1: Clean up common LLM junk like ```json fences
        llm_text = re.sub(r"^```(json)?", "", llm_text)
        llm_text = re.sub(r"```$", "", llm_text)
        llm_text = llm_text.strip()

        # Step 2: Extract JSON if wrapped with text accidentally
        match = re.search(r"\{.*\}", llm_text, re.S)
        if match:
            llm_text = match.group(0)

        # Step 3: Parse JSON
        improved_json = json.loads(llm_text)

        # Step 4: Validate schema
        _ = KolamRequest(**improved_json)
        return improved_json

    except Exception as e:
        print(f"⚠️ LLM Enhancement failed: {e}")
        return kolam_json
