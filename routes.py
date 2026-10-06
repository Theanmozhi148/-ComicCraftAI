"""
ComicCraft - Application Routes
Defines all endpoint routes for frontend views, comic generation,
JSON API integration, and PDF downloads.
"""

import os
import traceback
from fastapi import APIRouter, Request, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter()


class PromptRequest(BaseModel):
    prompt: str = Field(..., description="Main story idea or prompt for the comic")
    character_name: str = Field(default="Hero", description="Protagonist name")
    setting: str = Field(default="Forest", description="Scene location or environment")
    tone: str = Field(default="Dramatic", description="Mood or narrative tone")
    style: str = Field(default="Comic Book", description="Art and illustration style")


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Renders the ComicCraft homepage form."""
    return templates.TemplateResponse(request=request, name="index.html")


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form("Hero"),
    setting: str = Form("Forest"),
    tone: str = Form("Dramatic"),
    style: str = Form("Comic Book"),
):
    """
    Handles form submission, processes the input using Gemini Flash, Gemini Pro,
    and Stable Diffusion, and returns the interactive comic preview page.
    """
    try:
        # Combine user inputs into a cohesive master prompt
        full_prompt = (
            f"{prompt}\n"
            f"The main character is {character_name}.\n"
            f"The setting is a {setting}.\n"
            f"The tone is {tone}. The art style is {style}."
        )

        print("\n==========================================")
        print(f"[ComicCraft] Starting comic creation pipeline:")
        print(f"  Character: {character_name}")
        print(f"  Setting:   {setting}")
        print(f"  Tone:      {tone}")
        print(f"  Art Style: {style}")
        print(f"  Prompt:    {prompt}")
        print("==========================================\n")

        # Step 1: Generate 5-panel comic outline using Gemini Flash
        outline = generate_outline(full_prompt)

        if not isinstance(outline, list) or len(outline) == 0:
            raise ValueError("Invalid outline structure generated from AI models.")

        # Step 2: Generate full story, narration and character dialogues using Gemini Pro
        full_story = generate_story(outline)

        # Step 3: Generate visual illustrations for each panel using Stable Diffusion
        images = []
        for panel_item in outline:
            p_prompt = panel_item.get("image_prompt", prompt) if isinstance(panel_item, dict) else str(panel_item)
            # Enhance prompt with user's selected art style
            enhanced_img_prompt = f"{p_prompt}, {style} style, {tone} atmosphere"
            img_path = generate_image(enhanced_img_prompt)
            images.append(img_path)

        # Step 4: Build organized comic layout
        layout = build_comic_layout(images, full_story, outline)

        # Step 5: Export comic to multi-page PDF
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/").lstrip("/")

        return templates.TemplateResponse(request=request, name="comic_preview.html", context={
            "layout": layout,
            "pdf_path": web_pdf_path,
            "character_name": character_name,
            "setting": setting,
            "tone": tone,
            "style": style,
            "story_prompt": prompt
        })

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-comic/json")
async def generate_comic_json(payload: PromptRequest):
    """
    API route that accepts JSON payloads, triggers comic generation,
    and returns comic layout data along with the generated PDF path.
    """
    try:
        full_prompt = (
            f"{payload.prompt}\n"
            f"The main character is {payload.character_name}.\n"
            f"The setting is a {payload.setting}.\n"
            f"The tone is {payload.tone}. The art style is {payload.style}."
        )

        outline = generate_outline(full_prompt)
        full_story = generate_story(outline)

        images = []
        for panel_item in outline:
            p_prompt = panel_item.get("image_prompt", payload.prompt) if isinstance(panel_item, dict) else str(panel_item)
            enhanced_img_prompt = f"{p_prompt}, {payload.style} style, {payload.tone} mood"
            images.append(generate_image(enhanced_img_prompt))

        layout = build_comic_layout(images, full_story, outline)
        pdf_path = save_pdf(layout)
        web_pdf_path = "/" + pdf_path.replace("\\", "/").lstrip("/")

        return JSONResponse(content={
            "status": "success",
            "character_name": payload.character_name,
            "setting": payload.setting,
            "tone": payload.tone,
            "style": payload.style,
            "layout": layout,
            "pdf_path": web_pdf_path
        })
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request, pdf_path: str = Query("")):
    """
    Displays the export confirmation page after the comic is downloaded,
    with a call-to-action to create another comic.
    """
    web_pdf_path = "/" + pdf_path.replace("\\", "/").lstrip("/") if pdf_path else ""
    return templates.TemplateResponse(request=request, name="export_success.html", context={
        "pdf_path": web_pdf_path
    })


@router.get("/test-image")
async def test_image(prompt: str = "A futuristic city at sunset, sci-fi, cinematic, artstation"):
    """
    Developer utility route to test image generation from a direct prompt
    without full comic creation.
    """
    try:
        image_path = generate_image(prompt)
        web_img_path = "/" + image_path.replace("\\", "/").lstrip("/")
        return {
            "message": "Image generated successfully",
            "path": image_path,
            "web_url": web_img_path
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download-pdf")
async def download_pdf(file_path: str = Query(...)):
    """Direct file download route for browser convenience."""
    clean_path = file_path.lstrip("/").replace("\\", "/")
    full_path = os.path.join(BASE_DIR, clean_path)
    if os.path.exists(full_path):
        filename = os.path.basename(full_path)
        return FileResponse(
            path=full_path,
            media_type="application/pdf",
            filename=filename
        )
    raise HTTPException(status_code=404, detail="Requested PDF was not found.")
