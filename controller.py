import os

from pathlib import Path
from classes import SheetInformation
from helpers import build_url, character_name_from_document, get_character_row, get_wiki_url
from service import DocumentService, DriveService, SheetService


def create_connections(info: SheetInformation):
    dir_path = Path.cwd()
    info.masterlist_id = os.environ.get(f"{info.game.upper()}_LIST_ID")
    
    document_service = DocumentService(dir_path=dir_path)
    drive_service = DriveService(dir_path=dir_path)
    sheet_service = SheetService(dir_path=dir_path)
    
    info.masterlist_url = build_url('spreadsheets', info.masterlist_id)
    info.sheet_url = build_url('document', info.sheet_id)

    info.name = character_name_from_document(document_service.get(info.sheet_id))

    if info.verbose:
        print(f'New character is named: {info.name}')
        print(f'Character masterlist: { info.masterlist_url }')
        print(f'Character sheet: {info.sheet_url}')

    # Get id to ST and player sheets
    st_id, player_id, character_folder_id = sheet_service.get_template_ids(info.masterlist_id)

    if info.verbose:
        print(f"ID for ST template = {st_id}")
        print(f"ID for Player template = {player_id}")
        print(f"ID for Character Folder = {character_folder_id}")
    
    game_folder_response = drive_service.get(id=st_id, fields='parents')
    game_folder_id = game_folder_response['parents'][0]
    
    st_template = drive_service.get(id=st_id)
    player_template = drive_service.get(id=player_id)

    st_file_name = st_template['name'].replace('<Template>', info.name)
    player_file_name = player_template['name'].replace('<Template>', info.name)

    
    # 2.3
    player_sheet_id = info.player_sheet_id
    st_sheet_id = info.st_sheet_id
    if info.st_sheet_id is None:
        print("Creating new ST sheet")
        st_sheet_id = drive_service.copy(id=st_id, parent=character_folder_id, name=st_file_name)
        if info.verbose:
           print(f"New ST Spreadsheet has ID = {st_sheet_id}")
    else:
        print(f"Using existing ST Spreadsheet with ID = {st_sheet_id}")
    
    if player_sheet_id is None:
        print("Creating new player sheet")
        player_sheet_id = drive_service.copy(id=player_id, parent=character_folder_id, name=player_file_name)
        if info.verbose:
           print(f"New Player Spreadsheet has ID = {player_sheet_id}")
    else:
        print(f"Using existing Player Spreadsheet with ID = {player_sheet_id}")
    

    player_sheet_url = build_url('spreadsheets', player_sheet_id)
    st_sheet_url = build_url('spreadsheets', st_sheet_id)
    if info.verbose:
        print(f"{player_sheet_url=}, {st_sheet_url=}")

    # 2.4
    drive_service.set_editor_permissions(info.email, player_sheet_id)
    
    
    # 2.5 
    drive_service.set_viewer_permissions(player_sheet_id)
    drive_service.set_viewer_permissions(st_sheet_id)
    drive_service.set_viewer_permissions(info.sheet_id)

    # 2.6
    list_range, value_range = get_character_row(info.game, st_sheet_id)
    result = sheet_service.append(info.masterlist_id, list_range, value_range)

    if info.verbose:
        print(result)
    
    
    if info.update_st_sheet:
        # ST sheet, XP log
        values = [
            [info.name],
            [info.sheet_url],
            [info.get_formatted_sanction_date()],
            [info.storyteller],
            [player_sheet_url],
            [st_sheet_url]
        ]
        character_data = [
            {'range': 'Overview!B1:B6', 'values': values}
        ]

        floor_xp = sheet_service.get_floor_xp(info.masterlist_id)

        
        character_data.append(
            {'range': floor_xp['cell'], 'values': [[floor_xp['xp']]]}
        )

        if info.game == 'scion':
            character_data.append(
                {'range': 'Overview!Q2:Q4', 'values': info.get_wrapped_callings()}
            )
        
        result = sheet_service.batch_update(st_sheet_id, character_data)

        if info.verbose:
            print(result)
    
    if info.update_player_sheet:
        # Player sheet
        values = [
        [f'=IMPORTRANGE("{st_sheet_url}", "Overview!A1:P20")']
        ]

        data = { 'values' : values }
        result = sheet_service.update(player_sheet_id, data, 'Overview--read only!A1')

        if info.verbose:
            print(result)
        
    #wiki_link = get_wiki_url(info.game, info.name)
    #print(f'Wiki link: {wiki_link}') # HERE BE DRAGONS

    with open('discord.txt', 'w') as f:
        lines = [
            '## QUICK LINKS',
            f'* Sanctioned: {info.get_formatted_sanction_date()}',
            f'* Character sheet: {info.sheet_url}',
            f'* Request sheet: {player_sheet_url}',
            f'* ST spreadsheet (view-only): {st_sheet_url}',
        #   f'* Wiki: {wiki_link}' # HERE BE DRAGONS
            f'* Connecting e-mail: {info.email}'
        ]

        if info.game == 'scion':
            lines.append(f'* Legend 1 ({info.get_formatted_sanction_date()})')
            lines.append(f'### Deeds')
            
            lines.append(f'\n')
            lines.append(f'## {info.name} of the <pantheon>')
            lines.append('Played by @<user>\n') 

            lines.append('### Titles')
            lines.append('- <title>\n')

            lines.apped('### Deeds')
        
        print('\n'.join(lines), file=f)



    