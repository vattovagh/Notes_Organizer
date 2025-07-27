import cv2
import pytesseract
import numpy as np
from PIL import Image
import os
from typing import List, Tuple

class OCRProcessor:
    """
    Handles OCR processing of handwritten notes using Tesseract
    """
    
    def __init__(self, tesseract_path: str = None):
        """
        Initialize OCR processor
        
        Args:
            tesseract_path: Path to tesseract executable (if not in PATH)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Configure Tesseract for better handwriting recognition
        self.config = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,!?;:()[]{}"\'-+=/* '
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply thresholding to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up the image
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from a single image
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(processed_image, config=self.config)
            
            # Clean up the extracted text
            text = self.clean_text(text)
            
            return text
            
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return ""
    
    def extract_text_from_multiple_images(self, image_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Extract text from multiple images
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of tuples (image_path, extracted_text)
        """
        results = []
        
        for image_path in image_paths:
            if os.path.exists(image_path):
                text = self.extract_text(image_path)
                results.append((image_path, text))
            else:
                print(f"Image file not found: {image_path}")
                results.append((image_path, ""))
        
        return results
    
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = text.replace('|', 'I')
        text = text.replace('0', 'O')  # Be careful with this one
        
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable())
        
        return text.strip()
    
    def get_text_confidence(self, image_path: str) -> float:
        """
        Get confidence score for OCR extraction
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Confidence score (0-100)
        """
        try:
            image = cv2.imread(image_path)
            if image is None:
                return 0.0
            
            processed_image = self.preprocess_image(image)
            
            # Get OCR data with confidence scores
            data = pytesseract.image_to_data(processed_image, config=self.config, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                return sum(confidences) / len(confidences)
            else:
                return 0.0
                
        except Exception as e:
            print(f"Error getting confidence for {image_path}: {str(e)}")
            return 0.0 