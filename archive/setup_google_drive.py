#!/usr/bin/env python3
"""
Google Drive Setup Script
Sets up Google Drive authentication for the Notes Organizer
"""

import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

def setup_google_drive():
    """Set up Google Drive authentication"""
    creds = None
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("Error: credentials.json not found!")
        print("Please download credentials.json from Google Cloud Console and place it in this directory.")
        print("Instructions:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing one")
        print("3. Enable Google Drive API")
        print("4. Create credentials (OAuth 2.0 Client ID)")
        print("5. Download credentials.json")
        return False
    
    print("Found credentials.json")
    
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        
        print("Authentication successful!")
    
    # Test the connection
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=10).execute()
        files = results.get('files', [])
        print(f"Connection test successful! Found {len(files)} items in your Drive root.")
    except Exception as e:
        print(f"Connection test failed: {str(e)}")
        return False
    
    print("Setup completed successfully!")
    return True

if __name__ == '__main__':
    try:
        if setup_google_drive():
            print("Google Drive setup completed successfully!")
        else:
            print("Google Drive setup failed!")
    except Exception as e:
        print(f"Authentication failed: {str(e)}") 