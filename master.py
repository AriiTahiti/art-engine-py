from os import getcwd, listdir
import json

current_path = getcwd()

all_json = list(listdir(f'{current_path}/shuffled'))

all = []

for json_file in all_json:
        
    with open(f'{current_path}/shuffled/{json_file}', 'r') as f:
        data = json.load(f)
        del f
        
    for att in data['attributes']:
        if att['trait_type'] == 'SKELETON' and att['value'] == "LAVA SKELETON":
            print(json_file)
        


