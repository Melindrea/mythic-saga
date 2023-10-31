from pathlib import Path
from dataclasses import dataclass, field

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

from lib.helpers import get_id_from_drive_url


@dataclass
class DriveService:
    dir_path: Path
    type: str = ''

    def __post_init__(self):
        self.service = get_service_object('drive', self.dir_path)

    def get(self, id: str, fields: str = None) -> dict:
        if fields is None:
            return self.service.files().get(fileId=id).execute()
        
        return self.service.files().get(fileId=id, fields=fields).execute()


    def search(self, query: str, file_fields: []) -> list:
        # search for the file, adapted from https://thepythoncode.com/article/using-google-drive--api-in-python
        result = []
        page_token = None
        while True:
            response = self.service.files().list(q=query,
                                            supportsAllDrives=True,
                                            #spaces="drive",
                                            fields=f"nextPageToken, files({','.join(file_fields)})",
                                            pageToken=page_token).execute()
            # iterate over filtered files
            for file in response.get("files", []):
                row = []
                for field in file_fields:
                    row.append(file[field])
                
                result.append(row)
            page_token = response.get('nextPageToken', None)
            if not page_token:
                # no more files
                break
        
        return result


    def get_folder_content_list(self, folder_id: str, file_fields: list, mime_type: str = None):
        query = f"'{folder_id}' in parents and trashed != true"
        
        if mime_type:
            query += f" and mimeType='{mime_type}'"

        return self.search(query, file_fields)
    
    
    def copy(self, id: str, parent: str, name: str) -> str:
        copy = self.service.files().copy(fileId=id, body={'parents': [parent], 'name': name} ).execute()
        return copy['id']


    def set_permissions(self, id: str, new_permissions: dict):
        return self.service.permissions().create(
          fileId=id, body=new_permissions).execute()
    
    
    def set_editor_permissions(self, e_mail, file_id):
        new_permissions = {
            'type': 'group',
            'role': 'writer',
            'emailAddress': e_mail
        }

        return self.set_permissions(id=file_id, new_permissions=new_permissions)        
        

    def set_viewer_permissions(self, file_id):
        new_permissions = {
            'type': 'anyone',
            'role': 'reader'
        }

        return self.set_permissions(id=file_id, new_permissions=new_permissions)
    

@dataclass
class SpreadSheetService:
    dir_path: Path

    def __post_init__(self):
        self.service = get_service_object('sheets', self.dir_path)

    
    def get(self, id: str, range: str) -> dict:
        return self.service.spreadsheets().values().get(spreadsheetId=id, range=range).execute()
        

    def get_template_ids(self, sheet_id) -> tuple[str, str, str]:
        cell_range = 'Overview!W5:W7'
        template_cells = self.get(id=sheet_id, range=cell_range)
        
        values = template_cells.get('values', [])
        st_link = values[0][0]
        player_link = values[1][0]
        character_folder_link = values[2][0]
        
        return (get_id_from_drive_url(st_link), get_id_from_drive_url(player_link), get_id_from_drive_url(character_folder_link))
    
    def append(self, id: str, range: str, body: dict) -> dict:
        return self.service.spreadsheets().values().append(
            spreadsheetId = id,
            range = range,
            valueInputOption = 'USER_ENTERED',
            body = body
        ).execute()
    

    def get_floor_xp(self, id: str):
        
        floor_xp = self.service.spreadsheets().values().get(
            spreadsheetId = id, range = "'XP log'!J2"
        ).execute()

        xp = floor_xp.get('values', [])[0][0]
        
        return { 
            'cell': "'XP log'!L2",
            'xp': xp
        }
    

    def update(self, id: str, data: dict, range: str) -> dict:
        return self.service.spreadsheets().values().update(
            spreadsheetId = id, 
            body = data, 
            range = range, 
            valueInputOption='USER_ENTERED').execute()

    def batch_update(self, id: str, data: dict) -> dict:
        batch_body = {
            'valueInputOption': 'USER_ENTERED',
            'data': data
        }

        return self.service.spreadsheets().values().batchUpdate(spreadsheetId=id, body=batch_body).execute()

@dataclass
class DocumentService:
    dir_path: Path

    def __post_init__(self):
        self.service = get_service_object('docs', self.dir_path)

    def get(self, id: str) -> dict:
        return self.service.documents().get(documentId=id).execute()


def get_credentials(dir_path: Path, scopes: list[str]=['https://www.googleapis.com/auth/drive']) -> Credentials:
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_path = dir_path / 'token.json'
    
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, scopes)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                dir_path / 'credentials.json',
                scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_service_object(service: str, dir_path: Path, scopes: list[str] = None) -> Resource:
    if scopes is None:
        creds = get_credentials(dir_path)
    else:
        creds = get_credentials(dir_path, scopes)
    
    try:
        return get_service(service, creds)
    except HttpError as err:
        print(err) # HERE BE DRAGONS: I don't like this, but for now it can stay like this
        
def get_service(service: str, creds: Credentials) -> Resource:
    match service:
        case 'sheets':
            return build('sheets', 'v4', credentials=creds)
        case 'docs':
            return build('docs', 'v1', credentials=creds)
        case 'drive':
            return build('drive', 'v3', credentials=creds)
        case _:
            raise Exception(f'Service: {service} not implemented')