"""
ComicCraft - Exporters Module
Compiles the comic panels, imagery, narration, and dialogues into a
professionally formatted multi-page PDF document using FPDF.
"""

import os
import re
from datetime import datetime
from typing import List, Dict, Any
from fpdf import FPDF

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_FOLDER = os.path.join(BASE_DIR, "static", "exports")
FONT_FOLDER = os.path.join(BASE_DIR, "static", "fonts")
os.makedirs(EXPORT_FOLDER, exist_ok=True)
os.makedirs(FONT_FOLDER, exist_ok=True)

FONT_PATH = os.path.join(FONT_FOLDER, "DejaVuSans.ttf")


def _sanitize_for_standard_font(text: str) -> str:
    """Replaces non-latin characters and typographical quotes for clean PDF rendering."""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"',
        "\u2014": "--", "\u2013": "-",
        "\u2026": "...", "\u2022": "*",
        "\u00a0": " ", "\t": "    "
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    # Filter out characters outside latin-1 if using core fonts
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ComicPDF(FPDF):
    def header(self):
        # Header banner on every page
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 6, "ComicCraft - AI Comic Story Creator", align="R")
        self.ln(4)

    def footer(self):
        # Footer on every page
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")


def save_pdf(layout: List[Dict[str, Any]]) -> str:
    """
    Compiles the full comic into a multi-page PDF file using FPDF.
    Each panel's image and narration are placed neatly on separate pages.

    Args:
        layout (list): List of panel dictionaries containing image_path, title, and text.

    Returns:
        str: Relative path to the saved PDF file (e.g. 'static/exports/comic_20261005120000.pdf').
    """
    pdf = ComicPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    use_custom_font = False
    if os.path.exists(FONT_PATH):
        try:
            # fpdf2 supports add_font with TTF
            pdf.add_font("DejaVu", "", FONT_PATH)
            pdf.add_font("DejaVu", "B", FONT_PATH)
            font_family = "DejaVu"
            use_custom_font = True
        except Exception as e:
            print(f"[Exporters] Warning loading font {FONT_PATH}: {e}")
            font_family = "Helvetica"
    else:
        font_family = "Helvetica"

    # Iterate through all panels
    for panel in layout:
        pdf.add_page()

        panel_num = panel.get("panel", 1)
        panel_title = panel.get("title", f"Panel {panel_num}")
        image_path = panel.get("image_path", "")
        story_text = panel.get("text", "")
        scene_desc = panel.get("scene_description", "")

        # Format texts
        if not use_custom_font:
            panel_title = _sanitize_for_standard_font(panel_title)
            story_text = _sanitize_for_standard_font(story_text)
            scene_desc = _sanitize_for_standard_font(scene_desc)

        # Panel Title Box
        pdf.set_y(15)
        pdf.set_fill_color(240, 243, 248)
        pdf.set_text_color(25, 30, 45)
        pdf.set_font(font_family, "B" if not use_custom_font else "", 15)
        pdf.cell(pdf.epw, 11, f"Panel {panel_num}: {panel_title}", align="C", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Resolve image path
        resolved_img = image_path
        if not os.path.isabs(resolved_img):
            resolved_img = os.path.join(BASE_DIR, image_path)

        # Image placement
        y_image = 32
        image_height = 105
        spacing_after_image = 8
        page_width = pdf.epw  # Effective page width inside margins

        if os.path.exists(resolved_img):
            try:
                # Center image on page
                img_x = (pdf.w - page_width) / 2
                pdf.image(resolved_img, x=img_x, y=y_image, w=page_width, h=image_height)
                # Outer comic border around image
                pdf.set_draw_color(30, 30, 30)
                pdf.set_line_width(0.6)
                pdf.rect(x=img_x, y=y_image, w=page_width, h=image_height)
            except Exception as e:
                pdf.set_y(y_image)
                pdf.set_font(font_family, "", 10)
                pdf.multi_cell(pdf.epw, 8, f"[Image display error: {str(e)}]", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_y(y_image + 20)
            pdf.set_font(font_family, "", 11)
            pdf.set_text_color(180, 50, 50)
            pdf.multi_cell(pdf.epw, 8, f"[Panel Illustration Generated: {image_path}]", align="C", new_x="LMARGIN", new_y="NEXT")

        # Text placement below image
        text_start_y = y_image + image_height + spacing_after_image
        pdf.set_y(text_start_y)

        # Scene description (in italics / muted tone)
        if scene_desc:
            pdf.set_font(font_family, "I" if not use_custom_font else "", 10)
            pdf.set_text_color(90, 95, 105)
            pdf.multi_cell(pdf.epw, 5.5, f"Scene: {scene_desc}", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        # Dialogue and narration
        story_lines = story_text.strip().splitlines()
        # Remove title line like "**Panel 1: Title**" if present
        if story_lines and story_lines[0].strip().lower().startswith("**panel"):
            story_lines = story_lines[1:]
        cleaned_text = "\n".join(story_lines).strip()

        # Render styled lines
        for line in cleaned_text.splitlines():
            line = line.strip()
            if not line:
                pdf.ln(2)
                continue

            if line.upper().startswith("**CAPTION:**") or line.upper().startswith("CAPTION:"):
                clean_cap = re.sub(r"^\*{0,2}CAPTION:\*{0,2}\s*", "", line, flags=re.IGNORECASE)
                pdf.set_font(font_family, "B" if not use_custom_font else "", 10)
                pdf.set_text_color(160, 90, 10)
                pdf.multi_cell(pdf.epw, 6, f"CAPTION: {clean_cap}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            elif line.upper().startswith("**NARRATION:**") or line.upper().startswith("NARRATION:"):
                clean_nar = re.sub(r"^\*{0,2}NARRATION:\*{0,2}\s*", "", line, flags=re.IGNORECASE)
                pdf.set_font(font_family, "B" if not use_custom_font else "", 10)
                pdf.set_text_color(20, 80, 150)
                pdf.multi_cell(pdf.epw, 6, f"NARRATION: {clean_nar}", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)
            elif line.upper().startswith("**IMAGE PROMPT:**") or line.upper().startswith("IMAGE PROMPT:"):
                # Skip prompt in final printable PDF
                pass
            else:
                pdf.set_font(font_family, "", 10)
                pdf.set_text_color(40, 40, 40)
                pdf.multi_cell(pdf.epw, 6, line, new_x="LMARGIN", new_y="NEXT")

    # Save with timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"comic_{timestamp}.pdf"
    abs_pdf_path = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(abs_pdf_path)
    print(f"[Exporters] Successfully generated PDF at: {abs_pdf_path}")

    # Return standard relative path for web and downloads
    return f"static/exports/{filename}"
