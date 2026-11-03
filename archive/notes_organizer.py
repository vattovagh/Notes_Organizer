import os
import glob
from typing import List, Dict, Tuple
import argparse
from datetime import datetime

from ocr_processor import OCRProcessor
from text_classifier import TextClassifier
from google_drive import GoogleDriveManager

class NotesOrganizer:
    """
    Main class that coordinates OCR, text classification, and Google Drive organization
    """
    
    def __init__(self, tesseract_path: str = None, credentials_file: str = 'credentials.json'):
        """
        Initialize Notes Organizer
        
        Args:
            tesseract_path: Path to tesseract executable
            credentials_file: Path to Google credentials file
        """
        print("Initializing Notes Organizer...")
        
        # Initialize components
        self.ocr_processor = OCRProcessor(tesseract_path)
        self.text_classifier = TextClassifier()
        self.drive_manager = GoogleDriveManager(credentials_file)
        
        print("Notes Organizer initialized successfully!")
    
    def process_single_image(self, image_path: str, confidence_threshold: float = 0.3) -> Dict:
        """
        Process a single image: extract text, classify, and prepare for upload
        
        Args:
            image_path: Path to the image file
            confidence_threshold: Minimum confidence for classification
            
        Returns:
            Dictionary with processing results
        """
        print(f"Processing image: {image_path}")
        
        # Extract text using OCR
        extracted_text = self.ocr_processor.extract_text(image_path)
        
        if not extracted_text.strip():
            print(f"No text extracted from {image_path}")
            return {
                'image_path': image_path,
                'text': '',
                'subject': 'unknown',
                'confidence': 0.0,
                'ocr_confidence': 0.0,
                'status': 'no_text_extracted'
            }
        
        # Get OCR confidence
        ocr_confidence = self.ocr_processor.get_text_confidence(image_path)
        
        # Classify the extracted text
        subject, classification_confidence = self.text_classifier.classify_text(
            extracted_text, confidence_threshold
        )
        
        result = {
            'image_path': image_path,
            'text': extracted_text,
            'subject': subject,
            'confidence': classification_confidence,
            'ocr_confidence': ocr_confidence,
            'status': 'success'
        }
        
        print(f"Classification result: {subject} (confidence: {classification_confidence:.2f})")
        return result
    
    def process_multiple_images(self, image_paths: List[str], confidence_threshold: float = 0.3) -> List[Dict]:
        """
        Process multiple images
        
        Args:
            image_paths: List of image file paths
            confidence_threshold: Minimum confidence for classification
            
        Returns:
            List of processing results
        """
        results = []
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"\nProcessing image {i}/{len(image_paths)}: {os.path.basename(image_path)}")
            
            result = self.process_single_image(image_path, confidence_threshold)
            results.append(result)
        
        return results
    
    def organize_and_upload(self, processing_results: List[Dict], base_folder_id: str = None) -> Dict[str, List[str]]:
        """
        Organize processed notes by subject and upload to Google Drive
        
        Args:
            processing_results: List of processing results from process_multiple_images
            base_folder_id: ID of base folder in Google Drive (optional)
            
        Returns:
            Dictionary mapping subjects to lists of uploaded file IDs
        """
        print("\nOrganizing and uploading notes to Google Drive...")
        
        # Filter out failed processing results
        valid_results = [result for result in processing_results if result['status'] == 'success']
        
        if not valid_results:
            print("No valid results to upload")
            return {}
        
        # Create or get the "OrganizedNotes" base folder
        organized_notes_folder_id = self.drive_manager.get_or_create_folder("OrganizedNotes", base_folder_id)
        
        if organized_notes_folder_id is None:
            print("Failed to create OrganizedNotes folder")
            return {}
        
        print(f"Using OrganizedNotes folder (ID: {organized_notes_folder_id})")
        
        # Upload to Google Drive within the OrganizedNotes folder
        uploaded_files = self.drive_manager.organize_notes_by_subject(valid_results, organized_notes_folder_id)
        
        # Print summary
        print("\nUpload Summary:")
        for subject, file_ids in uploaded_files.items():
            print(f"  {subject}: {len(file_ids)} files uploaded")
        
        return uploaded_files
    
    def process_directory(self, directory_path: str, file_extensions: List[str] = None, 
                         confidence_threshold: float = 0.3, base_folder_id: str = None) -> Dict:
        """
        Process all images in a directory
        
        Args:
            directory_path: Path to directory containing images
            file_extensions: List of file extensions to process (default: common image formats)
            confidence_threshold: Minimum confidence for classification
            base_folder_id: ID of base folder in Google Drive (optional)
            
        Returns:
            Dictionary with processing and upload results
        """
        if file_extensions is None:
            file_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']
        
        # Find all image files
        image_paths = []
        for ext in file_extensions:
            pattern = os.path.join(directory_path, ext)
            image_paths.extend(glob.glob(pattern))
            # Also check for uppercase extensions
            pattern = os.path.join(directory_path, ext.upper())
            image_paths.extend(glob.glob(pattern))
        
        if not image_paths:
            print(f"No image files found in {directory_path}")
            return {}
        
        print(f"Found {len(image_paths)} image files to process")
        
        # Process images
        processing_results = self.process_multiple_images(image_paths, confidence_threshold)
        
        # Organize and upload
        upload_results = self.organize_and_upload(processing_results, base_folder_id)
        
        return {
            'processing_results': processing_results,
            'upload_results': upload_results,
            'total_images': len(image_paths),
            'successful_uploads': sum(len(files) for files in upload_results.values())
        }
    
    def get_processing_summary(self, processing_results: List[Dict]) -> Dict:
        """
        Generate a summary of processing results
        
        Args:
            processing_results: List of processing results
            
        Returns:
            Summary dictionary
        """
        total_images = len(processing_results)
        successful_extractions = sum(1 for r in processing_results if r['status'] == 'success')
        successful_classifications = sum(1 for r in processing_results if r['subject'] != 'unknown')
        
        # Subject distribution
        subject_counts = {}
        for result in processing_results:
            subject = result['subject']
            subject_counts[subject] = subject_counts.get(subject, 0) + 1
        
        # Average confidences
        avg_ocr_confidence = sum(r['ocr_confidence'] for r in processing_results) / total_images if total_images > 0 else 0
        avg_classification_confidence = sum(r['confidence'] for r in processing_results) / total_images if total_images > 0 else 0
        
        return {
            'total_images': total_images,
            'successful_extractions': successful_extractions,
            'successful_classifications': successful_classifications,
            'subject_distribution': subject_counts,
            'average_ocr_confidence': avg_ocr_confidence,
            'average_classification_confidence': avg_classification_confidence
        }

def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description='Organize handwritten notes using OCR and AI')
    parser.add_argument('input', help='Input file or directory path')
    parser.add_argument('--output', help='Google Drive base folder ID (optional)')
    parser.add_argument('--confidence', type=float, default=0.3, help='Classification confidence threshold')
    parser.add_argument('--tesseract', help='Path to tesseract executable')
    parser.add_argument('--credentials', default='credentials.json', help='Google credentials file path')
    
    args = parser.parse_args()
    
    # Initialize organizer
    organizer = NotesOrganizer(args.tesseract, args.credentials)
    
    # Process input
    if os.path.isfile(args.input):
        # Single file
        result = organizer.process_single_image(args.input, args.confidence)
        upload_results = organizer.organize_and_upload([result], args.output)
    elif os.path.isdir(args.input):
        # Directory
        results = organizer.process_directory(args.input, confidence_threshold=args.confidence, base_folder_id=args.output)
        
        # Print summary
        if results:
            summary = organizer.get_processing_summary(results['processing_results'])
            print("\n" + "="*50)
            print("PROCESSING SUMMARY")
            print("="*50)
            print(f"Total images processed: {summary['total_images']}")
            print(f"Successful text extractions: {summary['successful_extractions']}")
            print(f"Successful classifications: {summary['successful_classifications']}")
            print(f"Average OCR confidence: {summary['average_ocr_confidence']:.2f}")
            print(f"Average classification confidence: {summary['average_classification_confidence']:.2f}")
            
            print("\nSubject Distribution:")
            for subject, count in summary['subject_distribution'].items():
                print(f"  {subject}: {count}")
    else:
        print(f"Error: {args.input} is not a valid file or directory")
        return 1
    
    print("\nProcessing completed successfully!")
    return 0

if __name__ == "__main__":
    exit(main()) 