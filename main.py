import json

from pathlib import Path

from service import get_service_object

def main():
    with open('discord.txt', 'w') as f:
        lines = [
            '** QUICK LINKS **',
            f'Character sheet: info.sheet_url',
            f'Request sheet: player_sheet_url',
            f'ST spreadsheet (view-only): st_sheet_url',
        #   f'Wiki: {wiki_link}') # HERE BE DRAGONS
            f'Connecting e-mail: info.email'
        ]
        print('\n\n'.join(lines), file=f)
    

if __name__ == "__main__":
    main()