import os
from urllib.parse import parse_qs, quote, urlparse


def build_url(type: str, id: str, action: str = None) -> str:
    if type in ['document', 'spreadsheets', 'slide']:
        url = f'https://docs.google.com/{type}/d/{id}'

        if action is not None:
            url += f'/{action}'

        return url
    
    return f'https://drive.google.com/open?id={id}'


def get_type_from_mimetype(type: str) -> str:
    mime_types = {
        'application/vnd.google-apps.audio': '',	
        'application/vnd.google-apps.document': 'document',
        'application/vnd.google-apps.drive-sdk': '',
        'application/vnd.google-apps.drawing': '',
        'application/vnd.google-apps.file': 'file',
        'application/vnd.google-apps.folder': '',
        'application/vnd.google-apps.form': '',
        'application/vnd.google-apps.fusiontable': '',
        'application/vnd.google-apps.jam': '',
        'application/vnd.google-apps.map': '',
        'application/vnd.google-apps.photo': '',
        'application/vnd.google-apps.presentation': 'slide',
        'application/vnd.google-apps.script': '',
        'application/vnd.google-apps.shortcut': '',
        'application/vnd.google-apps.site': '',
        'application/vnd.google-apps.spreadsheet': 'spreadsheets',
        'application/vnd.google-apps.unknown': '',
        'application/vnd.google-apps.video': ''
    }
    return mime_types.get(type)


def character_name_from_document(document: dict) -> str:
    title = document.get('title')
    title_chunks = title.split('/')
    
    return title_chunks[0].strip()


def get_id_from_drive_url(drive_url: str) -> str:
    parsed_url = urlparse(drive_url)

    # https://drive.google.com/open?id=1ZVa0qapDKghiMRIAjjvl4d9lbueMDbwFQZlbFX9ILWo
    qs = parse_qs(parsed_url.query)
    id = qs.get('id')
    if id is not None:
        return id[0]
    
    # https://drive.google.com/drive/folders/1OQQsB0EbsENM-6tCGlPnk_rNVuNirGo4?usp=drive_link
    bits = parsed_url.path.split('/')
    return bits[-1]

    raise Exception(drive_url)

def get_character_row(game: str, st_sheet_id: str) -> tuple[str, dict]:
    # This removes any blankspaces and capitalization
    games = list(map(lambda game: game.strip().lower(), os.environ.get('GAMES').split(',')))
    
    if game not in games:
        print(f'Game {game} is not active.')
        return None
    
    row = []
    for cell in ['B1', 'B3', 'E2', 'E3', 'B2', 'url', 'B5', 'C1', 'B7']:
        if cell == 'url':
            row.append(build_url('spreadsheets', st_sheet_id))
        else:
            row.append(f'=IMPORTRANGE(INDIRECT(CONCAT("F", ROW())), "Overview!{cell}")')

    
    if game == 'scion':
        list_range = 'Character list!A2:M'

        for i in [2, 3, 4]:
            row.append(f'=IMPORTRANGE(INDIRECT(CONCAT("F", ROW())), "Overview!Q{i}")')
        
    elif game in ['exalted', 'modern']:
        list_range = 'Character list!A2:I'

    # Values will be appended after the last row of the table.
    value_range_body = {
        'values': [ row ]
    }

    return list_range, value_range_body


def get_wiki_url(game: str, character_name: str) -> str:
    if game == 'scion':
        prefix = 'ScD'
    elif game == 'exalted':
        prefix = 'ExND'
    elif game == 'modern':
        prefix = 'ExM'
        
    return f'https://wiki.mythic-saga.com/view/{prefix}:{quote(character_name)}'