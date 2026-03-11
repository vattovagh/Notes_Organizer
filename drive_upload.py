"""
Upload notes to Google Drive, sorted into subject folders.
Uses OAuth2 with DRIVEAPI.json; first run opens a browser to sign in.
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# Access to create and manage files/folders created by this app.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Paths relative to project root
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "DRIVEAPI.json")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "token_drive.json")

# Root folder name on Drive under which subject folders are created
DEFAULT_ROOT_FOLDER = "Notes"


def get_drive_service():
    """Build Drive API service, doing OAuth flow if needed."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Credentials not found: {CREDENTIALS_FILE}. "
                    "Use the JSON from Google Cloud Console (OAuth 2.0 Client ID, Desktop app)."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)


def get_or_create_folder(service, folder_name, parent_id=None):
    """
    Return the ID of a Drive folder with the given name under parent_id.
    Creates it if it doesn't exist. parent_id None means Drive root.
    """
    if parent_id is None:
        parent_id = "root"
    query = (
        f"name = {repr(folder_name)} and "
        f"'{parent_id}' in parents and "
        "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    )
    results = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = results.get("files", [])
    if files:
        return files[0]["id"]
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upload_file(service, local_path, folder_id, drive_name=None):
    """Upload a file to the given folder. Returns the new file's ID."""
    name = drive_name or os.path.basename(local_path)
    mime = "image/jpeg" if name.lower().endswith((".jpg", ".jpeg")) else "image/png"
    if not name.lower().endswith((".jpg", ".jpeg", ".png")):
        mime = "application/octet-stream"
    metadata = {"name": name, "parents": [folder_id]}
    media = MediaFileUpload(local_path, mimetype=mime, resumable=True)
    file = (
        service.files()
        .create(body=metadata, media_body=media, fields="id, name")
        .execute()
    )
    return file["id"]


def upload_notes_to_drive(
    local_folder_path,
    root_folder_name=DEFAULT_ROOT_FOLDER,
    image_extensions=(".jpg", ".jpeg", ".png"),
):
    """
    For each note image in local_folder_path:
      1. Extract text (Google Vision)
      2. Classify into a subject category
      3. Create/find that subject folder under root_folder_name on Drive
      4. Upload the image into that folder

    Returns list of (filename, category, drive_file_id or None on error).
    """
    from scan_contents import detect_handwritten_text
    from classify_note import classify_text

    local_folder_path = os.path.abspath(local_folder_path)
    if not os.path.isdir(local_folder_path):
        raise NotADirectoryError(local_folder_path)

    service = get_drive_service()
    root_id = get_or_create_folder(service, root_folder_name, None)

    files = [
        f
        for f in os.listdir(local_folder_path)
        if f.lower().endswith(image_extensions)
    ]
    files.sort()

    results = []
    for filename in files:
        path = os.path.join(local_folder_path, filename)
        try:
            text = detect_handwritten_text(path)
            category = classify_text(text).strip() if text.strip() else "Other"
            folder_id = get_or_create_folder(service, category, root_id)
            file_id = upload_file(service, path, folder_id, filename)
            results.append((filename, category, file_id))
            print(f"  {filename} -> {category} (uploaded)")
        except Exception as e:
            print(f"  {filename} -> Error: {e}")
            results.append((filename, None, None))

    return results


if __name__ == "__main__":
    import sys
    root_name = DEFAULT_ROOT_FOLDER
    folder = os.getcwd()
    if len(sys.argv) >= 2:
        folder = sys.argv[1]
    if len(sys.argv) >= 3:
        root_name = sys.argv[2]
    print(f"Uploading notes from: {folder}")
    print(f"Drive root folder: {root_name}")
    upload_notes_to_drive(folder, root_folder_name=root_name)
