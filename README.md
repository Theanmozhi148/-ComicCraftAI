# ComicCraft - AI Comic Story Creator using Gemini Models

ComicCraft is an end-to-end, AI-driven comic book story and illustration generation application. By orchestrating **Google Gemini AI models** (`gemini-1.5-flash` for structured panel outlines, `gemini-1.5-pro` for detailed comic narration and dialogues) and **Stable Diffusion** for comic-style illustrations, ComicCraft streamlines the entire creative storytelling process.

Built with **FastAPI**, **Jinja2**, and **FPDF**, ComicCraft provides both an interactive, responsive web interface and RESTful JSON APIs to generate 5-panel comic strips and export them as publication-ready PDFs.

---

## 🌟 Key Features

1. **Structured Storyboard Outlines (Gemini Flash)**:
   - Converts user story prompts into a coherent, 5-panel storyboard breakdown.
   - Generates panel titles, vivid scene descriptions, and tailored visual prompts.

2. **Rich Narration & Dialogue Generation (Gemini Pro)**:
   - Expands storyboard outlines into engaging, comic-style narratives.
   - Formats distinct environment **CAPTIONs** and dynamic character **NARRATIONs** & speech dialogues.

3. **Multi-Tiered Comic Illustration (Stable Diffusion)**:
   - Seamlessly generates panel illustrations matching the chosen art style (*Comic Book*, *Anime*, *Pixel Art*, *Realistic*, *Vintage Pop-Art*).
   - Supports Hugging Face Inference API, web-based Diffusion inference, local diffusers pipeline, and an offline artistic synthesizer.

4. **Automated Layout Assembly & Multi-Page PDF Export**:
   - `layout_builder.py` unifies images, scene context, captions, and dialogues into structured panel data.
   - `exporters.py` compiles the comic into a multi-page PDF formatted with `fpdf2`, saving it to `static/exports/`.

5. **Modern, Responsive Web Interface**:
   - Scenic atmospheric homepage with glassmorphic cards and intuitive form controls.
   - Real-time animated progress indicators during AI generation.
   - Responsive comic preview cards displaying artwork, captions, and dialogues.
   - One-click PDF download with automated redirect to confirmation page.

---

## 📁 Project Directory Structure

```
comiccraft/
├── app/
│   ├── __init__.py           # Application package initializer
│   ├── main.py               # FastAPI entrypoint, static files, lifecycle management
│   ├── routes.py             # Route handlers (/, /generate, /generate-comic/json, /export-success, /test-image)
│   ├── gemini_flash.py       # 5-panel storyboard outline generator (Gemini Flash)
│   ├── gemini_pro.py         # Comic narration and character dialogues generator (Gemini Pro)
│   ├── image_generator.py    # Multi-tier Stable Diffusion illustration generator
│   ├── layout_builder.py     # Matches images and story into structured comic layout
│   └── exporters.py          # Multi-page PDF generation via FPDF
├── templates/
│   ├── index.html            # Input form homepage with scenic background
│   ├── comic_preview.html    # Panel-by-panel comic preview with PDF download
│   ├── export_success.html   # Export confirmation page
│   └── result.html           # Plan result redirection template
├── static/
│   ├── css/
│   │   └── style.css         # Modern responsive comic styling & animations
│   ├── js/
│   │   └── main.js           # Client interactions, loading state, PDF download trigger
│   ├── images/
│   │   └── scenic-bg.jpg     # Scenic atmospheric background image
│   ├── fonts/
│   │   └── DejaVuSans.ttf    # Unicode TrueType font for PDF export
│   ├── panels/               # Generated panel illustrations
│   └── exports/              # Exported comic PDFs
├── .env.example              # Environment variables template
├── .env                      # Local configuration file (API keys)
├── requirements.txt          # Python dependencies
├── run.py                    # One-click application runner
└── README.md                 # Project documentation
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10, 3.11, 3.12, 3.13)
- Pip package manager

### 2. Environment Setup
Create and activate a virtual environment:

```bash
# Windows
python -m venv env
env\Scripts\activate

# macOS / Linux
python3 -m venv env
source env/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and enter your API keys:
```env
# Get a free Gemini API key: https://aistudio.google.com/
GEMINI_API_KEY=your_gemini_api_key_here

# (Optional) Hugging Face API key for Stable Diffusion:
HF_API_KEY=your_huggingface_api_key_here
```

*(Note: ComicCraft includes an intelligent offline & test fallback mode, meaning you can test and run the full pipeline end-to-end even before inserting API keys!)*

### 5. Launch the Server
Run using either `python run.py` or `uvicorn`:
```bash
python run.py
```
Or:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open your browser and navigate to:
- **Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📖 API Endpoints Reference

### `GET /`
Renders the HTML comic creation form.

### `POST /generate`
Accepts `multipart/form-data`:
- `prompt` (string, required): Main story concept.
- `character_name` (string): Hero's name (e.g. "Free").
- `setting` (string): Location (e.g. "Forest", "Cyberpunk City").
- `tone` (string): Narrative mood ("Dramatic", "Funny", "Light-hearted", "Poetic").
- `style` (string): Visual art style ("Comic Book", "Anime", "Realistic", "Pixel Art").

Returns the rendered `comic_preview.html`.

### `POST /generate-comic/json`
Accepts JSON body:
```json
{
  "prompt": "A brave fox exploring an enchanted forest.",
  "character_name": "Free",
  "setting": "Enchanted Forest",
  "tone": "Dramatic",
  "style": "Comic Book"
}
```
Returns:
```json
{
  "status": "success",
  "layout": [ ... 5 panels ... ],
  "pdf_path": "/static/exports/comic_20261005120000.pdf"
}
```

### `GET /export-success`
Displays the download success page with query parameter `?pdf_path=...`.

### `GET /test-image`
Generates a standalone illustration from a query prompt:
`GET /test-image?prompt=futuristic+superhero`

### `GET /download-pdf`
Streams the generated PDF file directly to the browser with content-disposition attachment.

---

## 📄 License
This project is released under the MIT License.
