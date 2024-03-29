import os
from dataclasses import dataclass
from pathlib import Path

from .classes import SheetInformation
from .googleAPI import DocumentService, DriveService, SpreadSheetService
from .helpers import (
    build_url,
    character_name_from_document,
    get_character_row,
    get_wiki_url,
)


def sheet_factory(kwargs: dict = None) -> SheetInformation:
    if kwargs:
        sh = SheetInformation(**kwargs)
    else:
        sh = SheetInformation()
    return sh


@dataclass
class SheetController:
    info: SheetInformation
    document_service: DocumentService = None
    drive_service: DriveService = None
    spreadsheet_service: SpreadSheetService = None
    dir_path: Path = Path.cwd()
    input_path: Path = None
    output_path: Path = None
    is_verbose: bool = False
    is_dry_run: bool = False
    profile_filename: str = "discord.txt"

    def __post_init__(self):
        if self.document_service is None:
            self.document_service = DocumentService(dir_path=self.dir_path)
        if self.drive_service is None:
            self.drive_service = DriveService(dir_path=self.dir_path)
        if self.spreadsheet_service is None:
            self.spreadsheet_service = SpreadSheetService(dir_path=self.dir_path)

        if self.output_path is None:
            self.output_path = self.dir_path / "output"

        if self.input_path is None:
            self.input_path = self.dir_path / "input"

    def get_profile_filename(self) -> Path:
        return self.output_path / self.profile_filename

    def gather_information(self):
        self.info.masterlist_id = os.environ.get(f"{self.info.game.upper()}_LIST_ID")
        self.info.masterlist_url = build_url("spreadsheets", self.info.masterlist_id)
        self.info.sheet_url = build_url("document", self.info.sheet_id)

        self.info.name = character_name_from_document(
            self.document_service.get(self.info.sheet_id)
        )

        if self.is_verbose:
            print(f"New character is named: {self.info.name}")
            print(f"Character masterlist: { self.info.masterlist_url }")
            print(f"Character sheet: {self.info.sheet_url}")

    def get_templates(self) -> dict:
        # Get id to ST and player sheets
        (
            st_id,
            player_id,
            character_folder_id,
        ) = self.spreadsheet_service.get_template_ids(self.info.masterlist_id)

        st_template = self.drive_service.get(id=st_id)
        player_template = self.drive_service.get(id=player_id)

        st_filename = st_template["name"].replace("<Template>", self.info.name)
        player_filename = player_template["name"].replace("<Template>", self.info.name)

        if self.is_verbose:
            print(f"ID for ST template = {st_id}")
            print(f"ST Filename = {st_filename}")
            print(f"ID for Player template = {player_id}")
            print(f"Player Filename = {player_filename}")
            print(f"ID for Character Folder = {character_folder_id}")

        return {
            "st": {"filename": st_filename, "id": st_id},
            "player": {"filename": player_filename, "id": player_id},
            "character_folder": {"id": character_folder_id},
        }

    def create_spreadsheets(self, information: dict) -> None:
        spreadsheets = [("st", "ST"), ("player", "Player")]

        for spreadsheet in spreadsheets:
            id_var_name = f"{spreadsheet[0]}_sheet_id"
            id_value = self.info.get(id_var_name)

            if id_value is None:
                if self.is_dry_run:
                    print(f"Dry Run: Creating new {spreadsheet[1]} spreadsheet")
                    self.info.set(id_var_name, f"DryRun{spreadsheet[0]}ID")
                    print("ID: " + information.get(spreadsheet[0]).get("id"))
                    print("Parent: " + information.get("character_folder").get("id"))
                    print("Name: " + information.get(spreadsheet[0]).get("filename"))
                else:
                    print(f"Creating new {spreadsheet[1]} spreadsheet")
                    copy_id = self.drive_service.copy(
                        id=information.get(spreadsheet[0]).get("id"),
                        parent=information.get("character_folder").get("id"),
                        name=information.get(spreadsheet[0]).get("filename"),
                    )
                    self.info.set(id_var_name, copy_id)

                    if self.is_verbose:
                        print(
                            f"New {spreadsheet[1]} Spreadsheet has ID = {self.info.get(id_var_name)}"
                        )
            else:
                print(
                    f"Using existing {spreadsheet[1]} Spreadsheet with ID = {self.info.get(id_var_name)}"
                )

            # Set the URL based on the ID
            id_value = self.info.get(id_var_name)
            url = build_url("spreadsheets", id_value)
            self.info.set(f"{spreadsheet[0]}_sheet_url", url)

    def update_spreadsheets(self) -> None:
        print(self.info)
        if self.is_dry_run:
            print("Dry Run: Updating spreadsheets with information and permissions.")

        # Player can edit their player spreadsheet
        if self.is_verbose:
            print(
                f"Updating player spreadsheet with editor permissions for {self.info.email}"
            )

        if not self.is_dry_run:
            self.drive_service.set_editor_permissions(
                self.info.email, self.info.player_sheet_id
            )

        # Anyone can view/read the ST spreadsheets, player spreadsheet, Character sheet
        if self.is_verbose:
            print(
                "Setting view/read permission to anyone on ST spreadsheet, player spreadsheet, character sheet."
            )

        if not self.is_dry_run:
            for bit in ["player_", "st_", ""]:
                id = self.info.get(f"{bit}sheet_id")
                self.drive_service.set_viewer_permissions(id)

        # Add a character row to the masterlist of character, below the prior character
        list_range, value_range = get_character_row(
            self.info.game, self.info.st_sheet_id
        )
        if self.is_verbose:
            print("Adding new character row to Character Masterlist.")

        if not self.is_dry_run:
            result = self.spreadsheet_service.append(
                self.info.masterlist_id, list_range, value_range
            )

            if self.is_verbose:
                print(result)

        # Update the ST spreadsheet with information and a copied XP log, as well as floor XP.
        values = [
            [self.info.name],
            [self.info.sheet_url],
            [self.info.get_formatted_sanction_date()],
            [self.info.storyteller],
            [self.info.player_sheet_url],
            [self.info.st_sheet_url],
        ]
        character_data = [{"range": "Overview!B1:B6", "values": values}]

        floor_xp = self.spreadsheet_service.get_floor_xp(self.info.masterlist_id)

        character_data.append({"range": floor_xp["cell"], "values": [[floor_xp["xp"]]]})

        if self.info.game == "scion":
            character_data.append(
                {"range": "Overview!Q2:Q4", "values": self.info.get_wrapped_callings()}
            )

        if self.is_verbose:
            print("Updating ST spreadsheet with information, XP log and floor XP.")

        if not self.is_dry_run:
            result = self.spreadsheet_service.batch_update(
                self.info.st_sheet_id, character_data
            )

            if self.is_verbose:
                print(result)

        # Link the player spreadsheet to the ST spreadsheet.
        values = [[f'=IMPORTRANGE("{self.info.st_sheet_url}", "Overview!A1:P20")']]

        data = {"values": values}

        if self.is_verbose:
            print("Updating Player spreadsheet with link to ST spreadsheet.")

        if not self.is_dry_run:
            result = self.spreadsheet_service.update(
                self.info.player_sheet_id, data, "Overview--read only!A1"
            )

            if self.is_verbose:
                print(result)

    def print_profile(self) -> None:
        profile_filename = self.get_profile_filename()
        if self.is_verbose:
            print(f"Printing profile information to {profile_filename}.")

        lines = [
            "## QUICK LINKS",
            f"* Sanctioned: {self.info.get_formatted_sanction_date()}",
            f"* Character sheet: {self.info.sheet_url}",
            f"* Request sheet: {self.info.player_sheet_url}",
            f"* ST spreadsheet (view-only): {self.info.st_sheet_url}",
            #   f'* Wiki: {get_wiki_url(self.info.game, self.info.name)}' # HERE BE DRAGONS
            f"* Connecting e-mail: {self.info.email}",
        ]

        if self.info.game == "scion":
            lines.append(f"* Legend 1 ({self.info.get_formatted_sanction_date()})")
            lines.append(f"### Deeds")

            lines.append(f"\n")
            lines.append(f"## {self.info.name} of the <pantheon>")
            lines.append("Played by @<user>\n")

            lines.append("### Titles")
            lines.append("- <title>\n")

            lines.append("### Deeds")

        if self.is_dry_run:
            print("\n".join(lines))

        else:
            with open(profile_filename, "w") as f:
                print("\n".join(lines), file=f)

    def initiate(self):
        self.gather_information()

        self.create_spreadsheets(self.get_templates())

        self.update_spreadsheets()

        self.print_profile()
