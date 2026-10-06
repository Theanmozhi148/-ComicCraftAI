"""
ComicCraft - Image Generator
Generates comic-style panel illustrations from prompts using Stable Diffusion,
Hugging Face Inference API, web diffusion services, or artistic synthesis.
"""

import os
import re
import time
import hashlib
import random
import requests
from io import BytesIO
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from dotenv import load_dotenv

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY", "").strip()
SD_MODEL_ID = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")

# Ensure static panels folder exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PANELS_DIR = os.path.join(BASE_DIR, "static", "panels")
os.makedirs(PANELS_DIR, exist_ok=True)

# Optional local diffusers pipeline
_local_pipe = None


def sanitize_filename(prompt: str) -> str:
    """Creates a filesystem-safe, unique filename from prompt."""
    clean = re.sub(r'[^a-zA-Z0-9_\- ]', '', prompt).strip().lower()
    clean = re.sub(r'\s+', '_', clean)[:32]
    hash_str = hashlib.md5(f"{prompt}_{time.time()}_{random.random()}".encode()).hexdigest()[:8]
    if not clean:
        clean = "comic_panel"
    return f"{clean}_{hash_str}.png"


def _generate_via_hf_api(prompt: str) -> Optional[Image.Image]:
    """Generates image using Hugging Face Inference API."""
    if not HF_API_KEY:
        return None
    try:
        api_url = f"https://api-inference.huggingface.co/models/{SD_MODEL_ID}"
        headers = {"Authorization": f"Bearer {HF_API_KEY}"}
        payload = {
            "inputs": f"{prompt}, comic book style, highly detailed graphic novel illustration, 4k resolution, masterpiece",
            "parameters": {"negative_prompt": "blurry, low quality, deformed, distorted, watermark"}
        }
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
        else:
            print(f"[Image Gen] HF API returned status {response.status_code}: {response.text[:100]}")
    except Exception as e:
        print(f"[Image Gen] HF API request failed: {e}")
    return None


def _generate_via_web_sd(prompt: str) -> Optional[Image.Image]:
    """Generates image via high-speed Stable Diffusion Web endpoint."""
    try:
        encoded_prompt = requests.utils.quote(f"{prompt}, high quality vibrant comic book art, detailed graphic novel panel, artstation")
        seed = random.randint(1000, 999999)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512&seed={seed}&nologo=true"
        response = requests.get(url, timeout=20)
        if response.status_code == 200 and len(response.content) > 1000:
            img = Image.open(BytesIO(response.content))
            return img.convert("RGB")
    except Exception as e:
        print(f"[Image Gen] Web SD API generation failed: {e}")
    return None


def _generate_artistic_fallback(prompt: str) -> Image.Image:
    """
    Synthesizes a stylized, high-res comic panel illustration using Pillow
    when offline or when network services are unreachable.
    """
    width, height = 768, 512
    img = Image.new("RGB", (width, height), (24, 28, 40))
    draw = ImageDraw.Draw(img)

    # Stylized background gradient
    color_schemes = [
        ((15, 32, 67), (44, 115, 210), (255, 140, 66)),     # Twilight Adventure
        ((35, 10, 50), (140, 45, 120), (255, 210, 80)),    # Enchanted Magic
        ((10, 40, 30), (28, 120, 85), (200, 240, 120)),    # Forest Depths
        ((40, 15, 15), (180, 50, 40), (255, 190, 60)),     # Action Flare
        ((20, 20, 35), (70, 80, 140), (100, 220, 240))     # Cyber Scifi
    ]
    c1, c2, c3 = random.choice(color_schemes)

    # Render smooth vertical gradient
    for y in range(height):
        ratio = y / height
        if ratio < 0.6:
            sub_r = ratio / 0.6
            r = int(c1[0] * (1 - sub_r) + c2[0] * sub_r)
            g = int(c1[1] * (1 - sub_r) + c2[1] * sub_r)
            b = int(c1[2] * (1 - sub_r) + c2[2] * sub_r)
        else:
            sub_r = (ratio - 0.6) / 0.4
            r = int(c2[0] * (1 - sub_r) + c3[0] * sub_r)
            g = int(c2[1] * (1 - sub_r) + c3[1] * sub_r)
            b = int(c2[2] * (1 - sub_r) + c3[2] * sub_r)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Comic dot / halftone texture
    for _ in range(350):
        dx = random.randint(10, width - 10)
        dy = random.randint(10, height - 10)
        dot_r = random.randint(1, 3)
        draw.ellipse([dx, dy, dx + dot_r, dy + dot_r], fill=(255, 255, 255, 60))

    # Stylized mountain/horizon landscape silhouettes
    horizon_y = height * 0.62
    points = [(0, height), (0, horizon_y)]
    step = 50
    for x in range(0, width + step, step):
        vary = random.randint(-40, 30)
        points.append((x, horizon_y + vary))
    points.append((width, height))
    draw.polygon(points, fill=(15, 18, 26))

    # Distant celestial glow / sun
    draw.ellipse([width * 0.65 - 50, height * 0.25 - 50, width * 0.65 + 50, height * 0.25 + 50],
                 fill=(255, 250, 220), outline=(255, 200, 100), width=3)

    # Bold comic border
    border_thickness = 8
    draw.rectangle([0, 0, width, height], outline=(20, 20, 20), width=border_thickness)

    # Comic action caption box
    tag_h = 42
    draw.rectangle([border_thickness, border_thickness, width - border_thickness, border_thickness + tag_h],
                   fill=(254, 228, 64), outline=(20, 20, 20), width=3)

    # Short label inside box
    short_prompt = prompt[:65] + ("..." if len(prompt) > 65 else "")
    try:
        font = ImageFont.load_default()
        draw.text((border_thickness + 16, border_thickness + 12), f"SCENE: {short_prompt.upper()}",
                  fill=(15, 15, 15), font=font)
    except Exception:
        pass

    # Dynamic action lines in corner
    for i in range(5):
        draw.line([(width - 15 - i * 18, height - border_thickness), (width - border_thickness, height - 15 - i * 18)],
                  fill=(255, 230, 80), width=4)

    return img


def generate_image(prompt: str, filename: Optional[str] = None) -> str:
    """
    Generates a comic-style image based on the provided prompt and saves it
    to static/panels/.

    Args:
        prompt (str): Image generation prompt for the comic panel.
        filename (str, optional): Target filename. If None, auto-generated.

    Returns:
        str: Relative path to the saved image (e.g. 'static/panels/comic_panel_1.png').
    """
    if not filename:
        filename = sanitize_filename(prompt)
    elif not filename.endswith(".png"):
        filename = f"{filename}.png"

    output_path = os.path.join(PANELS_DIR, filename)

    print(f"[Image Generator] Creating comic illustration for: {prompt[:60]}...")

    image = None

    # Tier 1: Hugging Face Inference API
    if HF_API_KEY:
        print("[Image Generator] Attempting Hugging Face Inference API...")
        image = _generate_via_hf_api(prompt)

    # Tier 2: Web Stable Diffusion API (Pollinations/Flux)
    if image is None:
        print("[Image Generator] Requesting Stable Diffusion illustration...")
        image = _generate_via_web_sd(prompt)

    # Tier 3: Local Diffusers Pipeline (if initialized)
    if image is None and _local_pipe is not None:
        try:
            print("[Image Generator] Using local Diffusers pipeline...")
            image = _local_pipe(prompt).images[0]
        except Exception as e:
            print(f"[Image Generator] Local pipeline failed: {e}")

    # Tier 4: Stylized Pillow Comic Art Generator (Offline & bulletproof)
    if image is None:
        print("[Image Generator] Using stylized comic panel synthesizer.")
        image = _generate_artistic_fallback(prompt)

    # Save final panel image
    image.save(output_path, "PNG", quality=95)
    print(f"[Image Generator] Saved panel to {output_path}")

    # Return web-standard relative path
    return f"static/panels/{filename}"
