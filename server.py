from flask import Flask, request, jsonify
from PIL import Image
import pytesseract
import io

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    image = Image.open(io.BytesIO(file.read()))
    text = pytesseract.image_to_string(image)

    return jsonify({"text": text})

if __name__ == '__main__':
    app.run(debug=True)
