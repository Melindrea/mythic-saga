import re
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class SheetInformation:
    game: str = ""
    sheet_id: str = ""
    sheet_url: str = ""
    name: str = ""
    storyteller: str = ""
    email: str = ""
    verbose: bool = ""
    override: bool = ""
    callings: list[int] = field(default_factory=list)
    sanction_date: datetime = datetime.now()
    masterlist_id: str = ""
    masterlist_url: str = ""
    player_sheet_id: str = None
    st_sheet_id: str = None
    update_player_sheet: bool = True
    update_st_sheet: bool = True
    
    def __str__(self) -> str:
        verbose = 'yes' if self.verbose else 'no'
        override = 'yes' if self.override else 'no'
        lines = [
            f"Game = {self.game}",
            f"Sheet ID = {self.sheet_id}",
            f"Sheet URL = {self.sheet_url}",
            f"Name = {self.name}",
            f"Storyteller = {self.storyteller}",
            f"Email = {self.email}",
            f"Verbose = {verbose}",
            f"Override validation = {override}",
            f"Callings = {', '.join(self.callings)}",
            f"Sanctioning Date = {self.get_formatted_sanction_date()}",
            f"Game Masterlist ID = {self.masterlist_id}",
            f"Game Masterlist URL = {self.masterlist_url}"
        ]
        if self.st_sheet_id:
            lines.append(f"ST Spreadsheet ID = {self.st_sheet_id}")
        
        if self.player_sheet_id:
            lines.append(f"Player Spreadsheet ID = {self.player_sheet_id}")

        return '\n'.join(lines)

    def proper_sanctioned_date(self) -> bool:
        if not self.given_sanctioned_date:
            return True # No need to check the formats if the sanction date isn't overriden
        
        datetime_object = None
        formats = ['%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']
        for format in formats:
            try:
                datetime_object = datetime.strptime(self.given_sanctioned_date, format)
            except ValueError:
                pass # Left empty on purpose
            else:
                # No exception means we've found a valid format
                break    
    
        if datetime_object:
            self.sanction_date = datetime_object
            return True
        
        return False

    def check_sanction_date(self) -> None:
        if not self.given_sanctioned_date:
            return # No override, no need to check format

        



    def get_formatted_sanction_date(self, format: str = '%m/%d/%Y') -> str:
        return self.sanction_date.strftime(format)

    def get_wrapped_callings(self) -> dict:
        return list(map(lambda calling: [calling], self.callings))

    def email_is_valid(self) -> bool:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        
        return re.match(regex, self.email)
    

    def callings_defined(self) -> bool:
        if self.game == 'scion' and self.callings is None:
            return False
        
        return True


