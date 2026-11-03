from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import re


def _natural_key(name):
    """Sort key so captured_image_2 comes before captured_image_10."""
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", name)]


def merge_notes(directory=None, prefix="captured_image_", output_pdf="all_pages.pdf",
                delete_originals=False):
    """
    Merge JPGs in `directory` (default: cwd) whose names start with `prefix` into one PDF.
    Originals are only deleted when delete_originals=True.
    Returns the PDF path, or None if there was nothing to merge.
    """
    directory = directory or os.getcwd()
    image_files = [
        f for f in os.listdir(directory)
        if f.lower().endswith((".jpg", ".jpeg")) and f.startswith(prefix)
    ]
    image_files.sort(key=_natural_key)

    if not image_files:
        print(f"No '{prefix}*.jpg' images found in {directory}")
        return None

    output_path = os.path.join(directory, output_pdf)
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    for image_file in image_files:
        image_path = os.path.join(directory, image_file)
        with Image.open(image_path) as image:
            img_width, img_height = image.size

        # Scale to fit the page, then center
        scale_factor = min(width / img_width, height / img_height)
        img_width = int(img_width * scale_factor)
        img_height = int(img_height * scale_factor)
        x = (width - img_width) / 2
        y = (height - img_height) / 2

        c.drawImage(image_path, x, y, img_width, img_height)
        c.showPage()

    c.save()
    print(f"PDF saved as {output_path}")

    if delete_originals:
        for file in image_files:
            os.remove(os.path.join(directory, file))

    return output_path
