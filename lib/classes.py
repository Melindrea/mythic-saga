import re
from dataclasses import dataclass, field
from datetime import datetime

from lib.helpers import get_valid_date


@dataclass
class SheetInformation:
    game: str = ""
    sheet_id: str = ""
    sheet_url: str = ""
    name: str = ""
    storyteller: str = ""
    email: str = ""
    callings: list[str] = field(default_factory=list)
    sanction_date: datetime = datetime.now()
    masterlist_id: str = ""
    masterlist_url: str = ""
    player_sheet_id: str = None
    player_sheet_url: str = None
    st_sheet_id: str = None
    st_sheet_url: str = None
    update_player_sheet: bool = True
    update_st_sheet: bool = True

    def __str__(self) -> str:
        lines = [
            f"Game = {self.game}",
            f"Sheet ID = {self.sheet_id}",
            f"Sheet URL = {self.sheet_url}",
            f"Player Spreadsheet ID = {self.player_sheet_id}",
            f"Player Speadsheet URL = {self.player_sheet_url}",
            f"ST Spreadsheet ID = {self.st_sheet_id}",
            f"ST Speadsheet URL = {self.st_sheet_url}",
            f"Name = {self.name}",
            f"Storyteller = {self.storyteller}",
            f"Email = {self.email}",
            f"Callings = {', '.join(self.callings)}",
            f"Sanctioning Date = {self.get_formatted_sanction_date()}",
            f"Game Masterlist ID = {self.masterlist_id}",
            f"Game Masterlist URL = {self.masterlist_url}",
        ]
        if self.st_sheet_id:
            lines.append(f"ST Spreadsheet ID = {self.st_sheet_id}")

        if self.player_sheet_id:
            lines.append(f"Player Spreadsheet ID = {self.player_sheet_id}")

        return "\n".join(lines)

    def get(self, attr: str):
        # Allows you to get the value of an attribute using variables
        return getattr(self, attr)

    def set(self, attr: str, value):
        # Allows you to set the value of an attribute using
        getattr(self, attr)  # Throws AttributeError if the attribute does not exist

        setattr(self, attr, value)

    def sanctioned_date_is_valid(self) -> bool:
        try:
            self.given_sanctioned_date
        except AttributeError:
            return True  # No need to check the formats if the sanction date isn't overriden

        if self.given_sanctioned_date is None:
            return True

        datetime_object = get_valid_date(self.given_sanctioned_date)

        if datetime_object:
            self.sanction_date = datetime_object
            return True

        return False

    def get_formatted_sanction_date(self, format: str = "%m/%d/%Y") -> str:
        return self.sanction_date.strftime(format)

    def get_wrapped_callings(self) -> list:
        return list(map(lambda calling: [calling], self.callings))

    def email_is_valid(self) -> bool:
        regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"

        match = re.match(regex, self.email)
        return match is not None

    def storyteller_is_valid(self) -> bool:
        if self.storyteller:
            return True

        return False

    def callings_defined(self) -> bool:
        if self.game == "scion" and (len(self.callings) < 3 or self.callings is None):
            return False

        return True
