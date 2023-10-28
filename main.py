import json
import re
from pathlib import Path

from service import get_service_object

def trim_and_split(string: str, delims: str = '[,.\\-\\%\\s]') -> list[str]:
    return list(filter(lambda x: x.strip() != '', re.split(delims, string)))
    
def main():
    information = {
        'st': {
            'filename': 'st_filename',
            'id': 'st_id'
        },
        'player': {
            'filename': 'player_filename',
            'id': 'player_id'
        },
        'character_folder': {
            'id': 'character_folder_id'
        }
    }

    print(information.get('st').get('id'))

if __name__ == "__main__":
    main()