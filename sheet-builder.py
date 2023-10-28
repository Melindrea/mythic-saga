# -*- coding: utf-8 -*-
"""Building a character sheet on Google Docs & Google Spreadsheets

This is the base CLI script that ties all of it together. 
It creates new lines in the character list, adds permissions and creates 
both the ST and Player spreadsheets.
"""

import argparse
import os

from dotenv import load_dotenv, find_dotenv

from classes import SheetInformation
from controller import create_connections

load_dotenv(find_dotenv())
VERSION = os.environ.get('VERSION')
# This removes any blankspaces and capitalization
GAMES = list(map(lambda game: game.strip().lower(), os.environ.get('GAMES').split(',')))

def validate_arguments(args: SheetInformation) -> list[str]:
    if args.override:
        return []
    
    errors = []

    if not args.email_is_valid():
        errors.append(f"The value used for player's e-mail ({args.email}) is not a valid e-mail (probably).")

    if not args.callings_defined():
        errors.append("You need to add three Callings when creating a Scion.")

    if not args.proper_sanctioned_date():
        errors.append(f"Invalid data format: {args.given_sanctioned_date}. For use with the -d or --given_sanctioned_date arguments, the usable formats are: 1/31/23, 01/31/23,  1/31/2023, 01/31/2023, or 2023-01-31")

    return errors
    

if __name__=='__main__':
    parser = argparse.ArgumentParser(
        prog="SheetBuilder",
        description="A script that creates spreadsheets and new lines in existing spreadsheets after sanctioning of a character in Mythic Saga."
    )
    parser.add_argument('game', help="The game the character belongs to.", choices=GAMES)
    parser.add_argument('-sh', '--sheet_id', help="Google Doc ID string")
    parser.add_argument('-st', '--storyteller', help="Sanctioning ST")
    parser.add_argument('-d', '--given_sanctioned_date', required=False, help="For characters sanctioned before creating the sheets. Formats: 1/31/23, 01/31/23,  1/31/2023, 01/31/2023, or 2023-01-31")
    parser.add_argument('-e', '--email', help="Player's Gmail (for permissions)")
    parser.add_argument('-c', '--callings', metavar=('Calling1', 'Calling2', 'Calling3'), nargs=3, help="Three callings. Required in case of Scion.", required=False)
    parser.add_argument('-v', '--verbose', action='store_true', help="Show extra information while running.")
    parser.add_argument('--version', action='version', version='%(prog)s v' + VERSION)
    parser.add_argument('-o', '--override', action='store_true', help="This allows you to override the extra validation checks such as Callings and valid e-mail.")
    parser.add_argument('-ps', '--player_sheet_id', required=False, help="If a Player Spreadsheet is already created put the ID here.")
    parser.add_argument('-sts', '--st_sheet-id', required=False, help="If an ST Spreadsheet is already created put the ID here.")
    parser.add_argument('-ups', '--update_player_sheet', action='store_false', help="If the player spreadsheet should not be updated, activate this flag.")
    parser.add_argument('-usts', '--update_st_sheet', action='store_false', help="If the ST spreadsheet should not be updated, activate this flag.")
    parser.add_argument('-dr', '--dry_run', action='store_true', help='This option just prints out the original values and does not change anything.')

    args = SheetInformation()
    parser.parse_args(namespace=args)

    errors = validate_arguments(args)
    if errors:
        parser.error('\n'.join(errors))
    
    if args.dry_run:
        print(args)
    else:
        create_connections(args)
    
