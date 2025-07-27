# Notes Organizer

A simple command-line Python application that automatically categorizes handwritten notes using OCR and AI, then organizes them in Google Drive.

## Features

- **OCR Processing**: Extracts text from handwritten notes using Tesseract
- **AI Classification**: Categorizes notes into subjects using transformer models
- **Google Drive Integration**: Automatically uploads and organizes files by subject
- **Auto-folder Creation**: Creates subject folders in Google Drive if they don't exist

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract OCR**:
   - **macOS**: `brew install tesseract`
   - **Ubuntu**: `sudo apt-get install tesseract-ocr`
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki

3. **Google Drive Setup**:
   - Create a Google Cloud Project
   - Enable Google Drive API
   - Download credentials.json and place it in the project root
   - Run `python setup_google_drive.py` to authenticate

4. **Environment Variables**:
   Create a `.env` file with:
   ```
   GOOGLE_CREDENTIALS_FILE=credentials.json
   ```

## Usage

### Simple Command Structure

```bash
# Process a single image
python notes_organizer.py image.jpg

# Process all images in a directory
python notes_organizer.py ./notes_folder

# Process with custom confidence threshold
python notes_organizer.py image.jpg --confidence 0.5

# Process and upload to specific Google Drive folder
python notes_organizer.py ./notes_folder --output "1ABC123DEF456"
```

### Command Options

- `input`: File or directory path (required)
- `--output`: Google Drive base folder ID (optional)
- `--confidence`: Classification confidence threshold (0.1-0.9, default: 0.3)
- `--tesseract`: Path to tesseract executable (optional)
- `--credentials`: Google credentials file path (default: credentials.json)

## Project Structure

```
Notes_Organizer/
├── notes_organizer.py     # Main CLI application
├── ocr_processor.py       # OCR text extraction
├── text_classifier.py     # AI text classification
├── google_drive.py        # Google Drive integration
├── setup_google_drive.py  # Google Drive authentication
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── credentials.json      # Google Drive credentials (not in repo)
```

## Supported Subjects

The AI classifier can categorize notes into various subjects including:
- Mathematics, Physics, Chemistry, Biology
- Computer Science, Engineering, Medicine
- History, Literature, Geography, Economics
- Psychology, Philosophy, Art, Music
- And many more...

## Examples

### Process a single note
```bash
python notes_organizer.py math_notes.jpg
```

### Process all notes in a folder
```bash
python notes_organizer.py ./my_notes --confidence 0.4
```

### Process and organize in Google Drive
```bash
python notes_organizer.py ./notes_folder --output "1ABC123DEF456"
```

## How it Works

1. **OCR Processing**: Extracts text from handwritten notes using Tesseract
2. **AI Classification**: Uses transformer models to categorize content into subjects
3. **Google Drive Organization**: Creates subject folders and uploads files automatically
4. **Auto-folder Creation**: Creates an "OrganizedNotes" base folder with subject subfolders

## Folder Structure

The system automatically creates this structure in your Google Drive:

```
Google Drive Root (or your specified folder)
└── OrganizedNotes/
    ├── mathematics/
    │   ├── math_notes.jpg
    │   ├── calculus_equations.png
    │   └── algebra_notes.jpg
    ├── physics/
    │   ├── mechanics_notes.jpg
    │   ├── thermodynamics.png
    │   └── quantum_physics.jpg
    ├── chemistry/
    │   ├── reactions.jpg
    │   ├── molecular_structures.png
    │   └── lab_notes.jpg
    ├── biology/
    │   ├── cell_biology.jpg
    │   ├── genetics_notes.png
    │   └── anatomy_diagrams.jpg
    └── computer_science/
        ├── algorithms.jpg
        ├── code_notes.png
        └── programming_concepts.jpg
```

**Note**: The "OrganizedNotes" folder is automatically created the first time you run the application. All your notes will be organized within this folder by subject.

## Troubleshooting

1. **Tesseract not found**: Make sure Tesseract is installed and in your PATH, or specify the path with `--tesseract`
2. **Google Drive authentication**: Run `python setup_google_drive.py` to set up authentication
3. **Low OCR accuracy**: Try improving image quality or adjusting preprocessing settings
4. **Classification issues**: Adjust the confidence threshold with `--confidence`

## License

MIT License 