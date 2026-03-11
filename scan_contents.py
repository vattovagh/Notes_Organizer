import os
from google.cloud import vision
import io

from classify_note import classify_text

def detect_handwritten_text(path):
    """Detects handwritten text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    annotations = response.text_annotations

    if annotations:
        return annotations[0].description
    else:
        return "No text detected"

def scan_and_extract_info(file_path, output_text_file, classify=True):
    extracted_information = detect_handwritten_text(file_path)

    with open(output_text_file, 'w') as f:
        f.write(extracted_information)

    print(f"Text extracted and saved to {output_text_file}")

    if classify and extracted_information.strip():
        category = classify_text(extracted_information)
        note_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"Category: {category}")
        return category
    return None

def classify_notes_in_folder(folder_path, image_extensions=('.jpg', '.jpeg', '.png')):
    """
    Extract text and classify each note image in a folder.
    Returns a list of (filename, category) and prints results.
    """
    results = []
    folder_path = os.path.abspath(folder_path)
    if not os.path.isdir(folder_path):
        print(f"Not a directory: {folder_path}")
        return results

    files = [f for f in os.listdir(folder_path)
             if f.lower().endswith(image_extensions)]
    files.sort()

    for filename in files:
        image_path = os.path.join(folder_path, filename)
        try:
            text = detect_handwritten_text(image_path)
            category = classify_text(text) if text.strip() else "Other"
            results.append((filename, category))
            print(f"  {filename} -> {category}")
        except Exception as e:
            print(f"  {filename} -> Error: {e}")
            results.append((filename, None))

    return results


if __name__ == "__main__":
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_upload = "--upload" in sys.argv
    if args:
        # Classify (and optionally upload) all notes in the given folder
        folder = args[0]
        print(f"Classifying notes in: {folder}")
        if do_upload:
            from drive_upload import upload_notes_to_drive
            root_name = args[1] if len(args) > 1 else "Notes"
            upload_notes_to_drive(folder, root_folder_name=root_name)
        else:
            classify_notes_in_folder(folder)
    else:
        # Single file: default behavior
        file_name = 'test_note.jpg'
        output_text_file = 'extracted_text.txt'
        image_path = os.path.join(os.getcwd(), file_name)
        scan_and_extract_info(image_path, output_text_file)
