# Notes Organizer

Capture handwritten or printed notes, extract text (OCR), classify by subject, merge into PDFs, and upload to Google Drive in subject folders.

## What it does

- **Webcam capture** — Take photos of note pages; merge them into a single PDF.
- **Text extraction** — Google Cloud Vision (handwriting) or Tesseract (printed text via Flask).
- **Subject classification** — Keyword-based categories: Mathematics, Science, Computer Science, History, Literature, Art, Music, Philosophy, Other.
- **Google Drive** — Upload notes into a root folder with one subfolder per subject.

## Prerequisites

- Python 3.10+
- **Tesseract OCR** (for the Flask server): `brew install tesseract` (macOS) or install from [tesseract-ocr](https://github.com/tesseract-ocr/tesseract).
- **Google Cloud** — Enable [Cloud Vision API](https://console.cloud.google.com/apis/library/vision.googleapis.com) and [Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com), and create credentials (see below).

## Setup

1. **Clone and install dependencies**

   ```bash
   cd Notes_Project
   python3 -m venv myenv
   source myenv/bin/activate   # Windows: myenv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Credentials (not in the repo — add locally)**

   - **Vision API** — Service account JSON from Google Cloud Console. Save as `Vision_API.json` in the project root and set:
     ```bash
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/Notes_Project/Vision_API.json"
     ```
   - **Drive API** — OAuth 2.0 Client ID (Desktop app). Download the JSON and save as `DRIVEAPI.json` in the project root. On first upload run, a browser will open to sign in; tokens are stored in `token_drive.json` (also gitignored).

   These files are in `.gitignore`; do not commit them.

## Usage

| Command | Description |
|--------|-------------|
| `python scan_contents.py` | Extract text from `test_note.jpg` → `extracted_text.txt` and print category |
| `python scan_contents.py /path/to/notes` | Classify each image in the folder (extract + category), print only |
| `python scan_contents.py /path/to/notes --upload` | Same + upload each note to Drive in subject folders |
| `python drive_upload.py [folder] [Drive_root_name]` | Upload folder to Drive; default root folder is `"Notes"` |
| `python webcam.py` | Capture images with camera (S = save, Q = quit), then merge all `.jpg` in cwd into `all_pages.pdf` |
| `python server.py` | Start Flask server; `POST /upload` with an image returns Tesseract OCR text as JSON |
| `python classify_note.py extracted_text.txt` | Classify an existing text file |

## Ask questions about your notes (RAG)

Notes are OCR'd (Google Vision), chunked, embedded locally (`all-MiniLM-L6-v2`), stored in Chroma (`.chroma/`), and answered with Claude using only the retrieved excerpts, with citations.

```bash
export ANTHROPIC_API_KEY=...
python notes_rag.py ingest Test_Notes            # images or .txt files
python notes_rag.py ask "What is a derivative?" [--subject Mathematics] [--k 4]
python -m eval.run_eval [--k 4] [--no-judge]     # hit@k, MRR, answer correctness, refusals
```

Add your own questions to `eval/questions.json` (replace the EXAMPLE entries). Unit tests: `python -m unittest discover tests`.

The earlier Tesseract + BART + Drive-manager pipeline is kept in `archive/`.

## Project structure

- `classify_note.py` — Subject classification (keyword-based).
- `scan_contents.py` — Vision API extraction + optional classification/upload.
- `drive_upload.py` — Drive auth, create subject folders, upload files.
- `merge.py` — Build one PDF from all `.jpg` in current directory.
- `webcam.py` — Camera capture and call to `merge.py`.
- `server.py` — Flask app for Tesseract OCR on uploaded images.
- `notes_rag.py`, `rag/`, `eval/`, `tests/` — RAG ingest, question answering, and evaluation.
- `archive/` — superseded pipeline.

## License

Use and modify as you like.
