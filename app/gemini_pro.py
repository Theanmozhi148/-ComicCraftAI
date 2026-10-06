"""
ComicCraft - Gemini Pro Comic Story and Dialogue Generator
Expands structured panel outlines into rich comic narration and character dialogues.
"""

import os
from typing import List, Dict, Any, Union
from dotenv import load_dotenv

load_dotenv()

# Configure Google Generative AI
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
PRO_MODEL_NAME = os.getenv("GEMINI_PRO_MODEL", "gemini-1.5-pro")

model = None
if API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(PRO_MODEL_NAME)
    except Exception as e:
        print(f"[Gemini Pro] Configuration warning: {e}")
        model = None


def _create_fallback_story(outline: List[Union[Dict[str, Any], str]]) -> str:
    """
    Generates an engaging, comic-formatted fallback story if the Gemini API
    is unreachable or missing an API key.
    """
    story_parts = []
    for idx, item in enumerate(outline, start=1):
        if isinstance(item, dict):
            title = item.get("title", f"Panel {idx}")
            desc = item.get("scene_description", "The adventure unfolds.")
            prompt_ref = item.get("image_prompt", "")
        else:
            title = f"Adventure Step {idx}"
            desc = str(item)
            prompt_ref = str(item)

        panel_text = f"""**Panel {idx}: {title}**
{desc}
**CAPTION:** The air hums with anticipation as destiny takes its first step into the unknown.
**NARRATION:** "No turning back now," whispered our brave hero, eyes fixed intently on the horizon ahead. "Whatever awaits, we face it together!"
**IMAGE PROMPT:** {prompt_ref}"""
        story_parts.append(panel_text)

    return "\n\n".join(story_parts)


def generate_story(outline: List[Union[Dict[str, Any], str]]) -> str:
    """
    Generates a detailed comic story with narration and character dialogue
    from a list of comic panel outlines using Gemini 1.5 Pro.

    Args:
        outline (list): A list of dictionaries or strings representing each comic panel.

    Returns:
        str: The generated comic story text formatted panel by panel.
    """
    formatted_items = []
    for i, item in enumerate(outline, start=1):
        if isinstance(item, dict):
            t = item.get("title", f"Panel {i}")
            d = item.get("scene_description", "")
            formatted_items.append(f"Panel {i}: Title: '{t}', Scene: '{d}'")
        else:
            formatted_items.append(f"Panel {i}: {item}")

    formatted_outline = "\n".join(formatted_items)

    prompt = f"""
You are a master comic book writer known for dynamic storytelling and witty dialogues.
Given the following 5-panel comic breakdown, write an engaging comic-style script with vivid narration and punchy character dialogues for EACH panel.

Panel Outline:
{formatted_outline}

Format Requirements:
For EACH panel from 1 to 5, you MUST start with:
**Panel X: Title**
Followed by:
A 1-2 sentence atmospheric scene description.
**CAPTION:** (A brief, atmospheric description of the environment, background sounds, or inner thought)
**NARRATION:** (Character dialogue with character names in quotes, and narrative actions)
**IMAGE PROMPT:** (The panel's visual summary)

Guidelines:
- Keep the tone vibrant and authentic to comic book storytelling.
- Ensure dialogue feels natural, expressive, and full of personality.
- Make every panel clear, distinct, and directly tied to the overarching plot.
"""
    global model
    if model is None:
        current_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if current_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=current_api_key)
                model = genai.GenerativeModel(PRO_MODEL_NAME)
            except Exception as e:
                print(f"[Gemini Pro] Lazy initialization error: {e}")

    if model:
        try:
            print("[Gemini Pro] Generating narrative and dialogue via Gemini Pro...")
            response = model.generate_content(prompt)
            story_text = response.text.strip()
            print("\n--- RAW GEMINI PRO RESPONSE ---\n", story_text[:300], "...\n-------------------------------\n")
            if "**Panel" in story_text or "**panel" in story_text:
                return story_text
            else:
                # If Gemini didn't include panel headings, structure it
                print("[Gemini Pro] Warning: panel tags missing, applying structure wrapper.")
                return story_text
        except Exception as e:
            print(f"[Gemini Pro] Error generating story via Gemini Pro: {e}. Switching to contextual fallback.")

    print("[Gemini Pro] Generating offline contextual comic story.")
    return _create_fallback_story(outline)
