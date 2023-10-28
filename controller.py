import os

from pathlib import Path
from classes import SheetInformation
from helpers import build_url, character_name_from_document, get_character_row, get_wiki_url
from service import DocumentService, DriveService, SpreadSheetService
from dataclasses import dataclass, field

@dataclass
class SheetController:
    info: SheetInformation
    document_service: DocumentService = None
    drive_service: DriveService = None
    spreadsheet_service: SpreadSheetService = None
    dir_path: Path = Path.cwd()
    is_verbose: bool = False
    is_dry_run: bool = False
    profile_filename: str = 'discord.txt'

    def __post_init__(self):
        if self.document_service is None:
            self.document_service = DocumentService(dir_path=self.dir_path)
        if self.drive_service is None:
            self.drive_service = DriveService(dir_path=self.dir_path)
        if self.spreadsheet_service is None:
            self.spreadsheet_service = SpreadSheetService(dir_path=self.dir_path)

    
    def gather_information(self):
        self.info.masterlist_id = os.environ.get(f"{self.info.game.upper()}_LIST_ID")
        self.info.masterlist_url = build_url('spreadsheets', self.info.masterlist_id)
        self.info.sheet_url = build_url('document', self.info.sheet_id)

        self.info.name = character_name_from_document(self.document_service.get(self.info.sheet_id))

        if self.is_verbose:
            print(f'New character is named: {self.info.name}')
            print(f'Character masterlist: { self.info.masterlist_url }')
            print(f'Character sheet: {self.info.sheet_url}')

        
    def get_templates(self) -> dict:
        # Get id to ST and player sheets
        st_id, player_id, character_folder_id = self.spreadsheet_service.get_template_ids(self.info.masterlist_id)

        st_template = self.drive_service.get(id=st_id)
        player_template = self.drive_service.get(id=player_id)

        st_filename = st_template['name'].replace('<Template>', self.info.name)
        player_filename = player_template['name'].replace('<Template>', self.info.name)
        
        if self.is_verbose:
            print(f"ID for ST template = {st_id}")
            print(f"ST Filename = {st_filename}")
            print(f"ID for Player template = {player_id}")
            print(f"Player Filename = {player_filename}")
            print(f"ID for Character Folder = {character_folder_id}")
        
        return {
            'st': {
                'filename': st_filename,
                'id': st_id
            },
            'player': {
                'filename': player_filename,
                'id': player_id
            },
            'character_folder': {
                'id': character_folder_id
            }
        }


    def create_spreadsheets(self, information: dict) -> None:
        if self.info.st_sheet_id is None:
            if self.is_dry_run:
                print("Dry Run: Creating new ST sheet")
                self.info.st_sheet_id = "DryRunSTID"
            else:
                print("Creating new ST sheet")
                self.info.st_sheet_id = self.drive_service.copy(
                    id=information.get('st').get('id'),
                    parent=information.get('character_folder').get('id'),
                    name=information.get('st').get('filename')
                )
                if self.is_verbose:
                    print(f"New ST Spreadsheet has ID = {self.info.st_sheet_id}")
        else:
            print(f"Using existing ST Spreadsheet with ID = {self.info.st_sheet_id}")
        
        if self.info.player_sheet_id is None:
            if self.is_dry_run:
                print("Dry Run: Creating new player sheet")
                self.info.player_sheet_id = "DryRunPlayerID"
            else:
                print("Creating new player sheet")
                self.info.player_sheet_id = self.drive_service.copy(
                    id=information.get('player').get('id'),
                    parent=information.get('character_folder').get('id'),
                    name=information.get('player').get('filename')
                )
                if self.is_verbose:
                    print(f"New Player Spreadsheet has ID = {self.info.player_sheet_id}")
        else:
            print(f"Using existing Player Spreadsheet with ID = {self.info.player_sheet_id}")
        

        self.info.player_sheet_url = build_url('spreadsheets', self.info.player_sheet_id)
        self.info.st_sheet_url = build_url('spreadsheets', self.info.st_sheet_id)
        if self.is_verbose:
            print(f'Player sheet URL: {self.info.player_sheet_url}, ST sheet URL: {self.info.st_sheet_url}')

    
    def update_spreadsheets(self) -> None:
        # Player can edit their player spreadsheet
        if self.is_verbose:
            print(f"Updating player spreadsheet with editor permissions for {self.info.email}")
        
        if not self.is_dry_run:
            self.drive_service.set_editor_permissions(self.info.email, self.info.player_sheet_id)
        
        # Anyone can view/read the ST spreadsheets, player spreadsheet, Character sheet
        if self.is_verbose:
            print("Setting view/read permission to anyone on ST spreadsheet, player spreadsheet, character sheet.")
        
        if not self.is_dry_run:
            self.drive_service.set_viewer_permissions(self.info.player_sheet_id)
            self.drive_service.set_viewer_permissions(self.info.st_sheet_id)
            self.drive_service.set_viewer_permissions(self.info.sheet_id)

        # Add a character row to the masterlist of character, below the prior character
        list_range, value_range = get_character_row(self.info.game, self.info.st_sheet_id)
        if self.is_verbose:
            print ("Adding new character row to Character Masterlist.")
        
        if not self.is_dry_run:
            result = self.spreadsheet_service.append(self.info.masterlist_id, list_range, value_range)

            if self.is_verbose:
                print(result)

        # Update the ST spreadsheet with information and a copied XP log, as well as floor XP.
        values = [
            [self.info.name],
            [self.info.sheet_url],
            [self.info.get_formatted_sanction_date()],
            [self.info.storyteller],
            [self.info.player_sheet_url],
            [self.info.st_sheet_url]
        ]
        character_data = [
            {'range': 'Overview!B1:B6', 'values': values}
        ]

        floor_xp = self.spreadsheet_service.get_floor_xp(self.info.masterlist_id)

        character_data.append(
            {'range': floor_xp['cell'], 'values': [[floor_xp['xp']]]}
        )

        if self.info.game == 'scion':
            character_data.append(
                {'range': 'Overview!Q2:Q4', 'values': self.info.get_wrapped_callings()}
            )
        
        if self.is_verbose:
            print("Updating ST spreadsheet with information, XP log and floor XP.")
        
        if not self.is_dry_run:
            result = self.spreadsheet_service.batch_update(self.info.st_sheet_id, character_data)

            if self.is_verbose:
                print(result)
        
        
        # Link the player spreadsheet to the ST spreadsheet.
        values = [
        [f'=IMPORTRANGE("{self.info.st_sheet_url}", "Overview!A1:P20")']
        ]

        data = { 'values' : values }

        if self.is_verbose:
            print("Updating Player spreadsheet with link to ST spreadsheet.")
        
        if not self.is_dry_run:
            result = self.spreadsheet_service.update(self.info.player_sheet_id, data, 'Overview--read only!A1')

            if self.is_verbose:
                print(result)


    def print_profile(self) -> None:
        if self.is_verbose:
            print(f"Printing profile information to {self.profile_filename}.")
        
        lines = [
            '## QUICK LINKS',
            f'* Sanctioned: {self.info.get_formatted_sanction_date()}',
            f'* Character sheet: {self.info.sheet_url}',
            f'* Request sheet: {self.info.player_sheet_url}',
            f'* ST spreadsheet (view-only): {self.info.st_sheet_url}',
        #   f'* Wiki: {get_wiki_url(self.info.game, self.info.name)}' # HERE BE DRAGONS
            f'* Connecting e-mail: {self.info.email}'
        ]

        if self.info.game == 'scion':
            lines.append(f'* Legend 1 ({self.info.get_formatted_sanction_date()})')
            lines.append(f'### Deeds')
            
            lines.append(f'\n')
            lines.append(f'## {self.info.name} of the <pantheon>')
            lines.append('Played by @<user>\n') 

            lines.append('### Titles')
            lines.append('- <title>\n')

            lines.append('### Deeds')

        if self.is_dry_run:
            print('\n'.join(lines))
        
        else:
            with open(self.profile_filename, 'w') as f:
                print('\n'.join(lines), file=f)


    def initiate(self):
        self.gather_information()
        
        self.create_spreadsheets(self.get_templates())

        if self.is_dry_run:
            print("Dry Run: Updating spreadsheets with information and permissions.")
        
        self.update_spreadsheets()

        self.print_profile()
        