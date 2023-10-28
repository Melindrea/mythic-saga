import json
import re
from pathlib import Path

from service import get_service_object

def trim_and_split(string: str, delims: str = '[,.\\-\\%\\s]') -> list[str]:
    return list(filter(lambda x: x.strip() != '', re.split(delims, string)))
    
def main():
    callings1 = 'calling1,calling2,calling3'
    callings2 = 'calling1, calling2, calling3'
    callings3 = 'calling1 calling2 calling3'

    print(trim_and_split(callings1))
    print(trim_and_split(callings2))
    print(trim_and_split(callings3))
    #delims = '[,.\-\%\s]'
    #print(re.split(delims, callings1))
    #print(re.split(delims, callings2))
    #print(re.split(delims, callings3))
    

if __name__ == "__main__":
    main()