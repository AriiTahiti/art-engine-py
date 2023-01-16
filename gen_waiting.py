import json
from os import getcwd 


current_path = getcwd()

for x in range(1, 4445):
    
    with open(f'{current_path}/json_base.json', 'r') as f:
        data = json.load(f)
        del f
            
    data['name'] = f'NAME #{x}'
    
    with open(f'{current_path}/waiting/{x}', 'w') as outfile:
        json.dump(data, outfile)
            