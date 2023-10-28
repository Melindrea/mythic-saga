# -*- coding: utf-8 -*-
"""Building a character sheet on Google Docs & Google Spreadsheets

This is the base CLI script that ties all of it together. 
It creates new lines in the character list, adds permissions and creates 
both the ST and Player spreadsheets.
"""

import csv
from datetime import datetime
import os

from dotenv import load_dotenv, find_dotenv

from argparse import ArgumentParser

from classes import SheetInformation
from controller import create_connections
import arg_parser
from helpers import get_valid_date, trim_and_split_string

load_dotenv(find_dotenv())
VERSION = os.environ.get('VERSION')
# This removes any blankspaces and capitalization
GAMES = list(map(lambda game: game.strip().lower(), os.environ.get('GAMES').split(',')))

def validate_arguments(args: SheetInformation) -> list[str]:
    if args.override:
        return []
    
    errors = []

    if not args.valid_storyteller():
        errors.append(f"The ST needs to be named.")

    if not args.email_is_valid():
        errors.append(f"The value used for player's e-mail ({args.email}) is not a valid e-mail (probably).")

    if not args.callings_defined():
        errors.append("You need to add three Callings when creating a Scion.")

    if not args.proper_sanctioned_date():
        errors.append(f"Invalid data format: {args.given_sanctioned_date}. For use with the -d or --given_sanctioned_date arguments, the usable formats are: 1/31/23, 01/31/23,  1/31/2023, 01/31/2023, or 2023-01-31")

    return errors


def cli_func(parser: ArgumentParser) -> None:
    sh = SheetInformation()
    parser.parse_args(namespace=sh)
    
    errors = validate_arguments(sh)
    if errors:
        parser.error('\n'.join(errors))
    
    if sh.dry_run:
        print(sh)
    else:
        create_connections(sh)


def file_func(parser: ArgumentParser) -> None:
    args = parser.parse_args()
    characters = []
    with open(args.path) as csvfile:
        list_reader = csv.DictReader(csvfile, delimiter=';', fieldnames=['game', 'sheet_id', 'email', 'sanction_date', 'storyteller', 'callings'])
        for row in list_reader:
            sanction_date = None
            if row['sanction_date']: # We check if the row has a valid date
                sanction_date = get_valid_date(row['sanction_date'])
            
            if not sanction_date and args.given_sanctioned_date: # If the row date fell through, check arg
                sanction_date = get_valid_date(args.given_sanctioned_date)

            if not sanction_date:
                sanction_date = datetime.now()
            
            storyteller = row['storyteller'].strip() if row['storyteller'] else args.storyteller

            callings = []
            if row['callings']:
                callings = trim_and_split_string(row['callings'])
                
            character = SheetInformation(
                sanction_date=sanction_date,
                storyteller=storyteller,
                game=row['game'].strip().lower(),
                sheet_id=row['sheet_id'].strip(),
                email=row['email'].strip().lower(),
                callings=callings
            )
            errors = validate_arguments(character)
            if errors:
                parser.error(f'Row with sheet ID {row['sheet_id']} invalid:' + '\n'.join(errors))

            characters.append(character)

    for character in characters:
        if args.dry_run:
            print(character)
        else:
            create_connections(character)


    """
    errors = validate_arguments(sh)
    if errors:
        parser.error('\n'.join(errors))
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
    """


def main():
    parser = arg_parser.main(VERSION)

    subparsers = parser.add_subparsers(help='{sub-command} --help')

    # create the parser for the "cli" command
    arg_parser.cli(subparsers, cli_func, GAMES)

    # Create the parser for the "file" command
    arg_parser.file(subparsers, file_func, GAMES)

    args = parser.parse_args()
    args.func(parser)

if __name__=='__main__':
    main()
    
