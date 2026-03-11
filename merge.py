import cv2
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def merge_notes():
    output_pdf = 'all_pages.pdf'
    cd = os.getcwd()
    image_files = [f for f in os.listdir(cd) if f.endswith('.jpg')]
    
    # Sort the files to ensure consistent order
    image_files.sort()

    # Create a canvas object
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    for image_file in image_files:
        # Open each image
        image_path = os.path.join(cd, image_file)
        image = Image.open(image_path)

        # Convert image to RGB if necessary
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Get image dimensions
        img_width, img_height = image.size

        # Calculate scaling factor to fit the image on the PDF page
        scale_factor = min(width / img_width, height / img_height)
        img_width = int(img_width * scale_factor)
        img_height = int(img_height * scale_factor)

        # Center the image on the page
        x = (width - img_width) / 2
        y = (height - img_height) / 2

        # Draw the image on the PDF page
        c.drawImage(image_path, x, y, img_width, img_height)
        c.showPage()  # Create a new page for the next image

    # Save the PDF
    c.save()
    print(f"PDF saved as {output_pdf}")

    for file in image_files:
        os.remove(os.path.join(cd, file))

