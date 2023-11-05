import os
import re
from datetime import datetime
from urllib.parse import parse_qs, quote, urlparse


def trim_and_split_string(string: str, delims: str = "[,.\\-\\%\\s]") -> list[str]:
    return list(filter(lambda x: x.strip() != "", re.split(delims, string)))


def get_valid_date(date: str) -> datetime:
    datetime_object = None
    formats = ["%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d"]
    for format in formats:
        try:
            datetime_object = datetime.strptime(date, format)
        except ValueError:
            pass  # Left empty on purpose
        else:
            # No exception means we've found a valid format
            break

    return datetime_object


def build_url(type: str, id: str, action: str = None) -> str:
    if type in ["document", "spreadsheets", "slide"]:
        url = f"https://docs.google.com/{type}/d/{id}"

        if action is not None:
            url += f"/{action}"

        return url

    return f"https://drive.google.com/open?id={id}"


def get_google_type_from_mimetype(type: str) -> str:
    mime_types = {
        "application/vnd.google-apps.audio": "",
        "application/vnd.google-apps.document": "document",
        "application/vnd.google-apps.drive-sdk": "",
        "application/vnd.google-apps.drawing": "",
        "application/vnd.google-apps.file": "file",
        "application/vnd.google-apps.folder": "",
        "application/vnd.google-apps.form": "",
        "application/vnd.google-apps.fusiontable": "",
        "application/vnd.google-apps.jam": "",
        "application/vnd.google-apps.map": "",
        "application/vnd.google-apps.photo": "",
        "application/vnd.google-apps.presentation": "slide",
        "application/vnd.google-apps.script": "",
        "application/vnd.google-apps.shortcut": "",
        "application/vnd.google-apps.site": "",
        "application/vnd.google-apps.spreadsheet": "spreadsheets",
        "application/vnd.google-apps.unknown": "",
        "application/vnd.google-apps.video": "",
    }
    return mime_types.get(type, "")


def character_name_from_document(document: dict) -> str:
    title = document.get("title", "")
    title_chunks = title.split("/")

    return title_chunks[0].strip()


def get_id_from_drive_url(drive_url: str) -> str:
    parsed_url = urlparse(drive_url)

    # https://drive.google.com/open?id=1ZVa0qapDKghiMRIAjjvl4d9lbueMDbwFQZlbFX9ILWo
    qs = parse_qs(parsed_url.query)
    id = qs.get("id")
    if id is not None:
        return id[0]

    # https://drive.google.com/drive/folders/1OQQsB0EbsENM-6tCGlPnk_rNVuNirGo4?usp=drive_link
    bits = parsed_url.path.split("/")
    return bits[-1]

    raise Exception(drive_url)


def get_character_row(game: str, st_sheet_id: str) -> tuple[str, dict]:
    # This removes any blankspaces and capitalization
    games = list(
        map(lambda game: game.strip().lower(), os.environ.get("GAMES").split(","))
    )

    if game not in games:
        raise ValueError(f"Game {game} is not active.")

    import_range = '=IMPORTRANGE(INDIRECT(CONCAT("F", ROW())), "Overview!'

    row = []
    for cell in ["B1", "B3", "E2", "E3", "B2", "url", "B5", "C1", "B7"]:
        if cell == "url":
            row.append(build_url("spreadsheets", st_sheet_id))
        else:
            row.append(f'{import_range}{cell}")')

    if game == "scion":
        lr_end = "M"

        for i in [2, 3, 4]:
            row.append(f'{import_range}Q{i}")')

    elif game in ["exalted", "modern"]:
        lr_end = "I"

    else:
        raise ValueError(f"No list_range associated with {game}.")

    # Values will be appended after the last row of the table.
    value_range_body = {"values": [row]}
    list_range = f"Character list!A2:{lr_end}"
    return list_range, value_range_body


def get_wiki_url(game: str, character_name: str) -> str:
    prefix = os.environ.get(f"{game.upper()}_WIKI_PREFIX")

    if prefix:
        wiki_url = os.environ.get("WIKI_URL")
        return f"{wiki_url}/{prefix}:{quote(character_name)}"

    raise ValueError(f"Game {game} is not active.")
