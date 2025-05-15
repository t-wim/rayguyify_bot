import os
import openai
import requests
import json
import uuid
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from pathlib import Path

def generate_ai_image(topic: str, caption: str = "") -> str:
    # Lade Prompt aus JSON
    with open("rayguyify_ai_prompts.json", "r", encoding="utf-8") as f:
        prompts = json.load(f)
    prompt = prompts.get(topic)
    if not prompt:
        raise ValueError(f"No prompt found for topic: {topic}")

    # OpenAI API-Key
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    # Bild anfordern
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024",
        response_format="url"
    )
    image_url = response["data"][0]["url"]
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert("RGBA")

    # RayGuy einfügen
    ray = Image.open("templates/base_raycast.png").convert("RGBA")
    scale = 0.6
    ray = ray.resize((int(image.width * scale), int(ray.height * scale)))
    x = (image.width - ray.width) // 2
    y = image.height - ray.height - 30
    image.paste(ray, (x, y), ray)

    # Caption zeichnen
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    w, h = draw.textsize(caption, font=font)
    draw.text(((image.width - w) // 2, image.height - h - 20), caption,
              font=font, fill="white", stroke_width=2, stroke_fill="black")

    # Speichern
    out_dir = Path("ai_generated")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / f"{topic}_{uuid.uuid4().hex[:6]}.png"
    image.save(out_path)
    return str(out_path)