#!/usr/bin/env python3
"""
Google Drive Setup Script

This script helps you set up Google Drive authentication for the Notes Organizer.
Follow these steps:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Drive API
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials JSON file
6. Place it in this directory as 'credentials.json'
7. Run this script to authenticate
"""

import os
import sys
from google_drive import GoogleDriveManager

def main():
    print("="*60)
    print("GOOGLE DRIVE SETUP FOR NOTES ORGANIZER")
    print("="*60)
    print()
    
    # Check if credentials file exists
    if not os.path.exists('credentials.json'):
        print("❌ Error: credentials.json not found!")
        print()
        print("Please follow these steps:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select an existing one")
        print("3. Enable the Google Drive API")
        print("4. Go to 'Credentials' and create an OAuth 2.0 Client ID")
        print("5. Download the JSON file and rename it to 'credentials.json'")
        print("6. Place it in this directory")
        print("7. Run this script again")
        print()
        return 1
    
    print("✅ Found credentials.json")
    print()
    print("Starting authentication process...")
    print("A browser window will open for you to sign in to Google.")
    print("After signing in, you'll be redirected back here.")
    print()
    
    try:
        # Initialize Google Drive manager (this will trigger authentication)
        drive_manager = GoogleDriveManager('credentials.json')
        
        print("✅ Authentication successful!")
        print()
        print("Your Google Drive is now connected to the Notes Organizer.")
        print("You can now use the application to upload and organize your notes.")
        print()
        
        # Test the connection by listing some files
        print("Testing connection...")
        try:
            # Try to list files in root directory
            files = drive_manager.list_files_in_folder('root')
            print(f"✅ Connection test successful! Found {len(files)} items in your Drive root.")
        except Exception as e:
            print(f"⚠️  Connection test failed: {str(e)}")
            print("This might be normal if you don't have permission to list root files.")
        
        print()
        print("Setup completed successfully! 🎉")
        return 0
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print()
        print("Common issues:")
        print("- Make sure you have internet connection")
        print("- Check that your credentials.json file is valid")
        print("- Ensure you have enabled the Google Drive API in your Google Cloud project")
        print("- Make sure you're using the correct Google account")
        print()
        return 1

if __name__ == "__main__":
    exit(main()) 