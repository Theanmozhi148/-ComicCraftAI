"""
ComicCraft - Comprehensive Pipeline & Endpoint Verification Test Suite
"""

import os
import sys
from starlette.testclient import TestClient

# Ensure comiccraft directory is on python path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf
from app.main import app


def test_gemini_flash_outline():
    print("\n[TEST 1] Testing Gemini Flash outline generator...")
    prompt = "A brave fox exploring an enchanted forest."
    outline = generate_outline(prompt)

    assert isinstance(outline, list), "Outline should be a list"
    assert len(outline) == 5, f"Outline should contain 5 panels, got {len(outline)}"
    for panel in outline:
        assert "panel" in panel, "Missing 'panel' key"
        assert "title" in panel, "Missing 'title' key"
        assert "scene_description" in panel, "Missing 'scene_description' key"
        assert "image_prompt" in panel, "Missing 'image_prompt' key"
    print("  --> PASS: 5-panel outline generated and validated.")


def test_gemini_pro_story():
    print("\n[TEST 2] Testing Gemini Pro story generator...")
    outline = generate_outline("A brave fox exploring an enchanted forest.")
    story = generate_story(outline)

    assert isinstance(story, str), "Story should be a string"
    assert len(story) > 50, "Story text should not be empty"
    print(f"  --> PASS: Story generated successfully ({len(story)} chars).")


def test_image_generator():
    print("\n[TEST 3] Testing Image Generator...")
    prompt = "comic art of a brave red fox standing in a misty forest"
    img_path = generate_image(prompt, filename="test_panel_verification")

    assert os.path.exists(img_path) or os.path.exists(os.path.join(CURRENT_DIR, img_path)), f"Image file not found: {img_path}"
    full_path = img_path if os.path.isabs(img_path) else os.path.join(CURRENT_DIR, img_path)
    file_size = os.path.getsize(full_path)
    assert file_size > 500, f"Image file is suspiciously small: {file_size} bytes"
    print(f"  --> PASS: Image generated at {full_path} ({file_size} bytes).")


def test_layout_builder_and_pdf_export():
    print("\n[TEST 4] Testing Layout Builder & PDF Export...")
    prompt = "A brave fox exploring an enchanted forest."
    outline = generate_outline(prompt)
    story = generate_story(outline)
    images = [generate_image(p["image_prompt"]) for p in outline]

    layout = build_comic_layout(images, story, outline)
    assert len(layout) == 5, f"Expected 5 panels in layout, got {len(layout)}"
    assert layout[0]["panel"] == 1
    assert "title" in layout[0]
    assert "image_path" in layout[0]

    pdf_path = save_pdf(layout)
    full_pdf_path = pdf_path if os.path.isabs(pdf_path) else os.path.join(CURRENT_DIR, pdf_path)
    assert os.path.exists(full_pdf_path), f"PDF file not found: {full_pdf_path}"
    pdf_size = os.path.getsize(full_pdf_path)
    assert pdf_size > 2000, f"PDF file size too small: {pdf_size} bytes"
    print(f"  --> PASS: PDF exported successfully at {full_pdf_path} ({pdf_size} bytes).")


def test_fastapi_endpoints():
    print("\n[TEST 5] Testing FastAPI web & API endpoints...")
    client = TestClient(app)

    # 1. Homepage GET /
    res_home = client.get("/")
    assert res_home.status_code == 200, f"Home returned {res_home.status_code}"
    assert "Create Your Comic" in res_home.text
    print("  --> PASS: GET / returns 200 OK.")

    # 2. Test Image Route GET /test-image
    res_test_img = client.get("/test-image?prompt=epic+superhero")
    assert res_test_img.status_code == 200
    json_data = res_test_img.json()
    assert "path" in json_data
    print("  --> PASS: GET /test-image returns 200 with image path.")

    # 3. JSON Generation Route POST /generate-comic/json
    res_json_gen = client.post("/generate-comic/json", json={
        "prompt": "Cybernetic detective solving a neon city mystery",
        "character_name": "Nexus",
        "setting": "Cyberpunk City",
        "tone": "Dramatic",
        "style": "Comic Book"
    })
    assert res_json_gen.status_code == 200, f"JSON generation returned {res_json_gen.status_code}"
    gen_data = res_json_gen.json()
    assert gen_data["status"] == "success"
    assert len(gen_data["layout"]) == 5
    assert "pdf_path" in gen_data
    print(f"  --> PASS: POST /generate-comic/json generated 5 panels and PDF {gen_data['pdf_path']}.")

    # 4. Export Success Route GET /export-success
    res_success = client.get(f"/export-success?pdf_path={gen_data['pdf_path']}")
    assert res_success.status_code == 200
    assert "Comic Exported Successfully" in res_success.text
    print("  --> PASS: GET /export-success returns 200 OK.")


if __name__ == "__main__":
    test_gemini_flash_outline()
    test_gemini_pro_story()
    test_image_generator()
    test_layout_builder_and_pdf_export()
    test_fastapi_endpoints()
    print("\n[SUCCESS] ALL PIPELINE TESTS PASSED! 100% OPERATIONAL.\n")
