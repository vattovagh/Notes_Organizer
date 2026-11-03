import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload
from typing import List, Dict, Optional
import mimetypes
from datetime import datetime

class GoogleDriveManager:
    """
    Manages Google Drive operations for organizing notes by subject
    """
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive']
    
    def __init__(self, credentials_file: str = 'credentials.json'):
        """
        Initialize Google Drive manager
        
        Args:
            credentials_file: Path to Google credentials JSON file
        """
        self.credentials_file = credentials_file
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Google Drive API"""
        creds = None
        # The file token.json stores the user's access and refresh tokens
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            print("Successfully authenticated with Google Drive!")
        except HttpError as error:
            print(f'An error occurred: {error}')
            raise
    
    def create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            ID of the created folder
        """
        try:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            
            if parent_folder_id:
                folder_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()
            
            print(f'Folder created: {folder_name} (ID: {folder["id"]})')
            return folder.get('id')
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def find_folder(self, folder_name: str, parent_folder_id: str = None) -> Optional[str]:
        """
        Find a folder by name
        
        Args:
            folder_name: Name of the folder to find
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            ID of the folder if found, None otherwise
        """
        try:
            query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            
            if parent_folder_id:
                query += f" and '{parent_folder_id}' in parents"
            
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                return folders[0]['id']
            else:
                return None
                
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def get_or_create_folder(self, folder_name: str, parent_folder_id: str = None) -> str:
        """
        Get existing folder or create new one
        
        Args:
            folder_name: Name of the folder
            parent_folder_id: ID of parent folder (optional)
            
        Returns:
            ID of the folder
        """
        folder_id = self.find_folder(folder_name, parent_folder_id)
        
        if folder_id:
            print(f'Found existing folder: {folder_name}')
            return folder_id
        else:
            return self.create_folder(folder_name, parent_folder_id)
    
    def upload_file(self, file_path: str, folder_id: str, filename: str = None) -> Optional[str]:
        """
        Upload a file to Google Drive
        
        Args:
            file_path: Path to the file to upload
            folder_id: ID of the destination folder
            filename: Custom filename (optional)
            
        Returns:
            ID of the uploaded file
        """
        try:
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                return None
            
            # Determine filename
            if filename is None:
                filename = os.path.basename(file_path)
            
            # Determine MIME type
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            # Prepare file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id]
            }
            
            # Upload file
            with open(file_path, 'rb') as file:
                media = MediaIoBaseUpload(
                    file,
                    mimetype=mime_type,
                    resumable=True
                )
                
                file_obj = self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            
            print(f'File uploaded: {filename} (ID: {file_obj["id"]})')
            return file_obj.get('id')
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def upload_multiple_files(self, file_paths: List[str], folder_id: str) -> List[Optional[str]]:
        """
        Upload multiple files to Google Drive
        
        Args:
            file_paths: List of file paths to upload
            folder_id: ID of the destination folder
            
        Returns:
            List of uploaded file IDs
        """
        file_ids = []
        
        for file_path in file_paths:
            file_id = self.upload_file(file_path, folder_id)
            file_ids.append(file_id)
        
        return file_ids
    
    def organize_notes_by_subject(self, notes_data: List[Dict], base_folder_id: str = None) -> Dict[str, List[str]]:
        """
        Organize notes by subject in Google Drive
        
        Args:
            notes_data: List of dictionaries with 'image_path', 'subject', 'text' keys
            base_folder_id: ID of base folder (optional)
            
        Returns:
            Dictionary mapping subjects to lists of uploaded file IDs
        """
        organized_files = {}
        
        for note in notes_data:
            image_path = note.get('image_path')
            subject = note.get('subject', 'unknown')
            text = note.get('text', '')
            
            if not image_path or not os.path.exists(image_path):
                continue
            
            # Create or get subject folder
            subject_folder_id = self.get_or_create_folder(subject, base_folder_id)
            
            if subject_folder_id is None:
                print(f"Failed to create folder for subject: {subject}")
                continue
            
            # Upload file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{subject}_{timestamp}_{os.path.basename(image_path)}"
            
            file_id = self.upload_file(image_path, subject_folder_id, filename)
            
            if file_id:
                if subject not in organized_files:
                    organized_files[subject] = []
                organized_files[subject].append(file_id)
        
        return organized_files
    
    def list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """
        List all files in a folder
        
        Args:
            folder_id: ID of the folder
            
        Returns:
            List of file information dictionaries
        """
        try:
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                spaces='drive',
                fields='files(id, name, mimeType, createdTime, size)'
            ).execute()
            
            return results.get('files', [])
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f'File deleted: {file_id}')
            return True
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def get_file_info(self, file_id: str) -> Optional[Dict]:
        """
        Get information about a file
        
        Args:
            file_id: ID of the file
            
        Returns:
            File information dictionary
        """
        try:
            file_info = self.service.files().get(
                fileId=file_id,
                fields='id, name, mimeType, createdTime, size, parents'
            ).execute()
            
            return file_info
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None 