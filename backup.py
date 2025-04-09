# https://developers.google.com/workspace/drive/api/quickstart/python
# https://developers.google.com/workspace/drive/api/reference/rest/v3 API folder 

import os, sys
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

from datetime import date, datetime

import shutil



####################Parameters####################
serviceJson = r"C:\Users\Tanner\OneDrive\Documents\credentials.json"
documents_location = r"C:\Users\Tanner\OneDrive\Documents" #   r"C:\Users\Tanner\Documents\My Cheat Tables" #-> testing small folder  
targetName = "Desktop Documents Backups" #Required google drive folder
####################################################

# SCOPES = ["https://www.googleapis.com/auth/drive.file"]  # Allows file upload
SCOPES = ["https://www.googleapis.com/auth/drive"]
formatted_date = datetime.now().strftime("%m_%d_%Y")

tokenPath = fr"{documents_location}\token.json"




downloads_location = documents_location.replace(r"\Documents", r"\Downloads").replace(r"\OneDrive", "")
# Ensure the filename is correctly formatted for output
zip_filename = downloads_location + fr"\Documents_{formatted_date}.zip"


print(f"Starting extract at {zip_filename}")
# Create ZIP archive
extract_filepath = shutil.make_archive(zip_filename.replace(".zip", ""), 'zip', documents_location)

print(f"Archive saved at: {extract_filepath}")


def authenticate():
    creds = None
    if os.path.exists(tokenPath):
        creds = Credentials.from_authorized_user_file(tokenPath, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(serviceJson, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(tokenPath, "w") as token:
            token.write(creds.to_json())
    return creds



def get_files():
  """Shows basic usage of the Drive v3 API.
  Prints the names and ids of the first 10 files the user has access to.
  """
  creds = authenticate()

  try:
    service = build("drive", "v3", credentials=creds)

    # Call the Drive v3 API
    results = (
        service.files()
        .list(pageSize=10, fields="nextPageToken, files(id, name)")
        .execute()
    )
    items = results.get("files", [])

    if not items:
      print("No files found.")
      return
    print("Files:")
    for item in items:
      print(f"{item['name']} ({item['id']})")
  except HttpError as error:
    # TODO(developer) - Handle errors from drive API.
    print(f"An error occurred: {error}")

  return items

def list_folders():
    creds = authenticate()  # Ensure authentication
    service = build("drive", "v3", credentials=creds)

    # Query for folders only
    query = "mimeType='application/vnd.google-apps.folder'"

    results = service.files().list(q=query, pageSize=50, fields="files(id, name)").execute()
    folders = results.get("files", [])

    if not folders:
        print("No folders found.")
        return None

    print("Folders:")
    for folder in folders:
        print(f"{folder['name']} ({folder['id']})")

    return folders  # Returns list of folder names & IDs for further use



# Example usage
folders = list_folders()
filtered = [folder for folder in folders if folder["name"] == targetName]

if len(filtered) != 1:
   print(f"Include the name of the folder {targetName}")
   sys.exit(1)

folder_id = filtered[0]['id']


# files = get_files()







# upload_file(zip_file_path, folder_id)


def upload_file(file_path, folder_id=None):
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    # Define file metadata
    file_metadata = {
        "name": os.path.basename(file_path),
        "mimeType": "application/zip"  # Change based on file type
    }

    if folder_id:
        file_metadata["parents"] = [folder_id]  # Upload to specific folder

    media = MediaFileUpload(file_path, mimetype="application/zip", resumable=True)

    file_id = service.files().create(body=file_metadata, media_body=media, fields="id").execute()['id']

    print(f"File uploaded successfully! File ID: {file_id}")
    return file_id


print(f"Google drive - Starting file upload of {extract_filepath} into the path of {targetName}")
# ID of the file we just created
file_id = upload_file(extract_filepath, folder_id)

def delete_files_except(file_id, folder_id):
    creds = authenticate()
    service = build("drive", "v3", credentials=creds)

    # List files in the folder
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if not files:
        print("No files found in the folder.")
        return

    print("Deleting files (except uploaded one):")
    for file in files:
        if file["id"] != file_id:  # Skip the newly uploaded file
            service.files().delete(fileId=file["id"]).execute()
            print(f"Deleted {file['name']} ({file['id']})")

# Delete all files in the folder except the one we created
delete_files_except(file_id, folder_id) #We do not need older hist
os.remove(extract_filepath) #We want to also remove our extract



