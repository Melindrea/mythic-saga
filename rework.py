# Imports
from __future__ import print_function

import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from urllib.parse import urlparse, parse_qs, quote

from datetime import datetime

def get_credentials(scopes=('https://www.googleapis.com/auth/drive')):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return creds

def get_service_object(service, scopes = None):
    if scopes is None:
        creds = get_credentials()
    else:
        creds = get_credentials(scopes)
    
    try:
        return get_service(service, creds)
    except HttpError as err:
        print(err)
        
def get_service(service, creds):
    match service:
        case 'sheets':
            return build('sheets', 'v4', credentials=creds)
        case 'docs':
            return build('docs', 'v1', credentials=creds)
        case 'drive':
            return build('drive', 'v3', credentials=creds)
        case _:
            raise Exception(f'Service: {service} not implemented')

def main():
    sheet_service = get_service_object('sheets')
    document_service = get_service_object('docs')
    drive_service = get_service_object('drive')
    print(sheet_service)
    print(document_service)
    print(drive_service)
    

if __name__ == "__main__":
    main()