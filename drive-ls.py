# -*- coding: utf-8 -*-
"""List all files in Google Drive Folder

Given the URL of a Google Drive folder, this will list all the files in it, with options
"""

import argparse
import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

from helpers import build_url, get_id_from_drive_url, get_google_type_from_mimetype
from service import DriveService

load_dotenv(find_dotenv())
VERSION = os.environ.get('VERSION')

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        prog="DriveLS",
        description="A script that creates a list of all the files in any given Google Drive Folder."
    )
    parser.add_argument('google_folder_url', help="Link to the folder, gotten via 'Share => Copy link'.")
    # https://drive.google.com/drive/folders/asdadioasdioj?usp=drive_link
    parser.add_argument('-b', '--build_url', required=False, choices=['copy', 'view', 'edit'], help="If the ID should be turned into a copy, view or edit link.")
    parser.add_argument('-md', '--markdown', action='store_true', help="Whether the links should be turned into a markdown list")
    parser.add_argument('-f', '--file', required=False, help="Filename to print the parsed files to.")

    args = parser.parse_args()
    id = get_id_from_drive_url(args.google_folder_url)
    
    dir_path = Path.cwd()
    drive_service = DriveService(dir_path=dir_path)

    files = drive_service.get_folder_content_list(id, ['id', 'name', 'mimeType'])
    
    def get_name(element: list) -> str:
        return element[1]
    
    if args.build_url:
        files = [(build_url(get_google_type_from_mimetype(n[2]), n[0], args.build_url), n[1]) for n in files]
    
    files.sort(key=get_name)
    
    if args.markdown:
        lines = []
        for file in files:
            lines.append(f'* [{file[1]}]({file[0]})')
        files = lines
    
    if args.file:
        with open(args.file, 'w', encoding='utf-8') as f:        
            print('\n'.join(files), file=f)

    else:
        print('\n'.join(files))