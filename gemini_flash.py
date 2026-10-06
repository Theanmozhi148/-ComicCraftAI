"""
ComicCraft - Gemini Flash Comic Outline Generator
Generates structured 5-panel comic outlines using Google's Gemini Flash model.
"""

import os
import json
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configure Google Generative AI
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
FLASH_MODEL_NAME = os.getenv("GEMINI_FLASH_MODEL", "gemini-1.5-flash")

model = None
if API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(FLASH_MODEL_NAME)
    except Exception as e:
        print(f"[Gemini Flash] Configuration warning: {e}")
        model = None


def _clean_json_text(text: str) -> str:
    """Extracts raw JSON array string from potentially markdown-wrapped text."""
    text = text.strip()
    # Strip markdown code blocks
    if "```" in text:
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"\s*```$", "", text, flags=re.MULTILINE)
        text = text.strip()

    # Search for array brackets [...]
    match = re.search(r"(\[\s*\{.*\}\s*\])", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text


def _create_fallback_outline(user_prompt: str) -> List[Dict[str, Any]]:
    """
    Creates a creative, structured 5-panel fallback outline if Gemini API
    is unreachable or no API key is provided.
    """
    prompt_snippet = user_prompt.strip().replace("\n", " ")
    if len(prompt_snippet) > 80:
        prompt_snippet = prompt_snippet[:77] + "..."

    return [
        {
            "panel": 1,
            "title": "The Awakening Journey",
            "scene_description": f"The story begins as our hero steps into the realm of adventure. Prompt: '{prompt_snippet}'. Sunlight filters through mist, revealing an uncharted path ahead.",
            "image_prompt": f"comic book art style, hero standing at the edge of the world, epic cinematic wide angle, vibrant colors, detailed line art, {prompt_snippet}"
        },
        {
            "panel": 2,
            "title": "A Mysterious Discovery",
            "scene_description": "Venturing deeper, strange glowing symbols and ancient artifacts appear along the way. Tension rises as unseen eyes watch from the shadows.",
            "image_prompt": f"comic book panel, close up dramatic shot, glowing magical relic discovered, curious expression, expressive eyes, vibrant atmosphere"
        },
        {
            "panel": 3,
            "title": "The Unforeseen Obstacle",
            "scene_description": "Suddenly, a tremendous obstacle blocks the path! Our protagonist pauses, gathering strength and preparing for an unexpected confrontation.",
            "image_prompt": f"action comic book illustration, dynamic high angle shot, towering challenge ahead, sparks flying, bold inked contours, dramatic lighting"
        },
        {
            "panel": 4,
            "title": "Turning the Tide",
            "scene_description": "With quick thinking, courage, and a stroke of ingenuity, the hero unleashes a clever maneuver, finding hope against the odds.",
            "image_prompt": f"comic book climax panel, hero leaping into decisive action, motion blur effects, intense energy, comic speed lines, vibrant colors"
        },
        {
            "panel": 5,
            "title": "Triumphant Horizon",
            "scene_description": "The dust settles. The challenge is overcome, and a breathtaking vista opens towards future legends and new horizons.",
            "image_prompt": f"warm sunset comic panel, triumphant hero smiling looking towards the horizon, peaceful victory, detailed landscape, comic book masterpiece"
        }
    ]


def generate_outline(user_prompt: str) -> List[Dict[str, Any]]:
    """
    Generates a 5-panel comic layout based on the user's story idea using Gemini Flash.

    Args:
        user_prompt (str): The user's comic idea prompt.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, one for each comic panel.
    """
    prompt = f"""
You are a professional AI comic planner and storyboard artist.
Your task is to generate a strictly formatted JSON array containing exactly 5 panel descriptions for a comic based on the story idea below:

STORY IDEA: "{user_prompt}"

Each JSON object must include:
- "panel": (integer 1 through 5)
- "title": (string, short punchy comic title)
- "scene_description": (string, vivid 1-2 sentence description setting the atmosphere and context)
- "image_prompt": (string, detailed descriptive prompt optimized for Stable Diffusion image generation)

Respond ONLY with this valid JSON array, without any explanations, markdown code tags, or commentary:
[
  {{
    "panel": 1,
    "title": "Title here",
    "scene_description": "Scene description here",
    "image_prompt": "Image prompt for Stable Diffusion"
  }}
]
"""
    global model
    # Re-check API key dynamically in case environment variable was set after import
    if model is None:
        current_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if current_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=current_api_key)
                model = genai.GenerativeModel(FLASH_MODEL_NAME)
            except Exception as e:
                print(f"[Gemini Flash] Lazy initialization error: {e}")

    if model:
        try:
            print("[Gemini Flash] Generating 5-panel outline via Gemini Flash...")
            response = model.generate_content(prompt)
            output_text = response.text.strip()
            print("\n--- RAW GEMINI FLASH RESPONSE ---\n", output_text, "\n--------------------------------\n")

            cleaned_text = _clean_json_text(output_text)
            panel_data = json.loads(cleaned_text)

            if isinstance(panel_data, list) and len(panel_data) > 0:
                validated_panels = []
                for idx, panel in enumerate(panel_data, start=1):
                    if isinstance(panel, dict):
                        validated_panels.append({
                            "panel": int(panel.get("panel", idx)),
                            "title": str(panel.get("title", f"Panel {idx}")).strip(),
                            "scene_description": str(panel.get("scene_description", "An unfolding scene in the journey.")).strip(),
                            "image_prompt": str(panel.get("image_prompt", f"comic illustration of {user_prompt}")).strip()
                        })

                if len(validated_panels) >= 3:
                    # Pad to 5 panels if needed
                    while len(validated_panels) < 5:
                        p_num = len(validated_panels) + 1
                        validated_panels.append({
                            "panel": p_num,
                            "title": f"The Adventure Continues #{p_num}",
                            "scene_description": "The storyline progresses with unexpected developments and revelations.",
                            "image_prompt": f"comic book art style, scene {p_num} continuing {user_prompt}, cinematic atmosphere"
                        })
                    return validated_panels[:5]

            print("[Gemini Flash] Response JSON schema did not match expected structure. Using fallback outline.")
        except Exception as e:
            print(f"[Gemini Flash] Error during Gemini Flash generation: {e}. Switching to contextual fallback.")

    print("[Gemini Flash] Generating offline contextual outline.")
    return _create_fallback_outline(user_prompt)
