
from argparse import ArgumentParser
from typing import Callable


def main(version: str) -> ArgumentParser:
    parser = ArgumentParser(
        prog="SheetBuilder",
        description="A script that creates spreadsheets and new lines in existing spreadsheets after sanctioning of a character in Mythic Saga."
    )
    parser.add_argument('-o', '--override', action='store_true', help="This allows you to override the extra validation checks such as Callings and valid e-mail.")
    parser.add_argument('-dr', '--dry_run', action='store_true', help='This option just prints out the original values and does not change anything.')
    parser.add_argument('-v', '--verbose', action='store_true', help="Show extra information while running.")
    parser.add_argument('--version', action='version', version='%(prog)s v' + version)
    
    return parser

def file(subparsers: ArgumentParser,
        function: Callable[[ArgumentParser], None],
        games: list[str]) -> None:
    parser = subparsers.add_parser('file', help='Adds several characters from a CSV-file. Format of each line is: # GAME (lowercase); GOOGLE_SHEET_ID; PLAYER_EMAIL; SANCTION_DATE (can be blank); SANCTION_ST (can be blank); CALLINGS (blank if not Scion)')
    parser.set_defaults(func=function)
    parser.add_argument('path', help="Path to CSV-file with character information to be read.")
    parser.add_argument('-st', '--storyteller', required=False, help="Sanctioning ST (if not defined in the file).")
    parser.add_argument('-d', '--given_sanctioned_date', required=False, help="Sanctioning date if not given in the file, and the date is not the current date. Formats: 1/31/23, 01/31/23,  1/31/2023, 01/31/2023, or 2023-01-31.")
    

def cli(
        subparsers: ArgumentParser,
        function: Callable[[ArgumentParser], None],
        games: list[str]) -> None:
    parser = subparsers.add_parser('cli', help='Adding a single character via the CLI, which has the most adaptability.')
    
    parser.set_defaults(func=function)
    parser.add_argument('game', help="The game the character belongs to.", choices=games)
    parser.add_argument('-sh', '--sheet_id', help="Google Doc ID string")
    parser.add_argument('-st', '--storyteller', help="Sanctioning ST")
    parser.add_argument('-d', '--given_sanctioned_date', required=False, help="For characters sanctioned before creating the sheets. Formats: 1/31/23, 01/31/23,  1/31/2023, 01/31/2023, or 2023-01-31")
    parser.add_argument('-e', '--email', help="Player's Gmail (for permissions)")
    parser.add_argument('-c', '--callings', metavar=('Calling1', 'Calling2', 'Calling3'), nargs=3, help="Three callings. Required in case of Scion.", required=False)
    parser.add_argument('-ps', '--player_sheet_id', required=False, help="If a Player Spreadsheet is already created put the ID here.")
    parser.add_argument('-sts', '--st_sheet-id', required=False, help="If an ST Spreadsheet is already created put the ID here.")
    parser.add_argument('-ups', '--update_player_sheet', action='store_false', help="If the player spreadsheet should not be updated, activate this flag.")
    parser.add_argument('-usts', '--update_st_sheet', action='store_false', help="If the ST spreadsheet should not be updated, activate this flag.")
        

