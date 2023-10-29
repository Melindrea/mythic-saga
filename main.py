from dataclasses import dataclass
import json
import re
from pathlib import Path

from service import get_service_object

def trim_and_split(string: str, delims: str = '[,.\\-\\%\\s]') -> list[str]:
    return list(filter(lambda x: x.strip() != '', re.split(delims, string)))

@dataclass
class Temp:
    one_thing: str = "one thing"
    two_thing: str = "two thing"
    foo: str = "fum"

    def get(self, attr: str):
        # Allows you to get the value of an attribute using variables
        return getattr(self, attr)

    
    def set(self, attr: str, value):
        setattr(self, attr, value)
 
def main():
    t = Temp()
    #t.set('foo', 'bar')
    print(t.foo)
    print(t.get('foo'))
    # getattr(object, attrname)
    # setattr(object, attrname, value)
    #for i in ['one', 'two']:
        #id = f'{i}_thing'
        
        #print(f'{i=}, {t.get(id)}')
    

if __name__ == "__main__":
    main()