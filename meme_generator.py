
import os
import json
from pathlib import Path
from ai_generator import generate_ai_image
from meme_generator_fallback import generate as fallback_generate

TOPICS = json.load(open("topics.json"))
USE_AI = os.getenv("USE_AI", "1") == "1"

def generate(topic: str, caption: str = "") -> str:
    if topic not in TOPICS:
        topic = list(TOPICS.keys())[0]
    info = TOPICS[topic]
    if not caption:
        caption = info.get("default_caption", topic.upper())

    if USE_AI:
        try:
            return generate_ai_image(topic, caption)
        except Exception as e:
            print(f"[Fallback] AI image generation failed for topic '{topic}': {e}")
    return fallback_generate(topic, caption)
