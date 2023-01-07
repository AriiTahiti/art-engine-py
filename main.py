from PIL import Image
import pandas as pd
import random
import re
from itertools import chain
import time
import hashlib
import json
import os
from multiprocessing import Pool

# Functions
def cap_sentence(s):
    return ''.join((c.upper() if prev == ' ' else c) for c, prev in zip(s, chain(' ', s)))

pattern = r'[0-9]'

def create_distribution_count(df_full: pd.DataFrame, df_grp: pd.DataFrame, total_amt: int) -> dict:
    # Final Distribution
    final_dist = {}
    
    for index, row in df_grp.iterrows():
        final_dist[row.GROUPS] = {}

        final_dist[row.GROUPS]['total'] = round(total_amt * row['% DISTRIBUTION'] / 100)

        sample = df_full[df_full['GROUPS'] == row.GROUPS].reset_index(drop=True)
        nb_grp = sample.index.max()
        new = 0

        final_dist[row.GROUPS]['all_attributes'] = {}
        
        for index2, row2 in sample.iterrows():
            attribute_prop = round(total_amt * row2['% DISTRIBUTION'] / 100)
            new += attribute_prop
            assert attribute_prop > 0
            final_dist[row2.GROUPS]['all_attributes'][row2['ATTRIBUTE NAMES']] = int(attribute_prop)
        
        if new != round(total_amt * row['% DISTRIBUTION'] / 100):
            dif = new - round(total_amt * row['% DISTRIBUTION'] / 100)
            number_to_remove = int(abs(dif))
            
            print(f'number_to_remove : {number_to_remove}')
            for x in range(number_to_remove):
                verif = 0
                while verif == 0:
                    n = random.randint(0, nb_grp)
                    to_change = sample.loc[n, 'ATTRIBUTE NAMES']
                    if final_dist[row.GROUPS]['all_attributes'][to_change] - 1 > 0:
                        if dif > 0:
                            final_dist[row.GROUPS]['all_attributes'][to_change] -= 1
                            new -= 1
                        else:
                            final_dist[row.GROUPS]['all_attributes'][to_change] += 1
                            new += 1
                        verif += 1

        assert int(new) == int(round(total_amt * row['% DISTRIBUTION'] / 100))
        final_dist[row.GROUPS]['all_attributes']['BLANK'] = total_amt - new
        final_dist[row.GROUPS]['available_attributes'] = list(df_full[df_full['GROUPS'] == row.GROUPS]['ATTRIBUTE NAMES'].unique())
        final_dist[row.GROUPS]['available_attributes'].append('BLANK')
        assert final_dist[row.GROUPS]['all_attributes']['BLANK'] + new == total_amt
    
    assert len(list(df_full['FILE NAMES'].unique())) == len(df_full), 'There is no unique file name'
    assert len(list(df_full['ATTRIBUTE NAMES'].unique())) == len(df_full), 'There is no unique attribute name'

    return final_dist

def create_metadata(count_dist: dict, df_full: pd.DataFrame, df_grp: pd.DataFrame, total_amt: int) -> list:

    current_dist = count_dist.copy()
    final_meta = []
    all_dna = []

    for x in range(1, total_amt+1):

        print(f'Generate #{x}')
        total_nb_layers = df_grp['layer_order'].max()
        done = 0

        while done == 0:

            meta = {
                "name": f"JRS #{x}",
                "description": f"Generated JRS Collection of {total_amt} NFTs",
                "image": "",
                "dna": "",
                "edition": 1,
                "date": int(time.time()),
                "attributes": [
                ],
                "final_sequence": [
                ],
                "sequence": [
                ],
                "all_blanks": [
                ]
            }

            for y in range(1, total_nb_layers+1):
                group = df_grp[df_grp['layer_order'] == y]['GROUPS']
                grp_selected = group.reset_index().iloc[0,1]

                selected = random.choices(list(current_dist[grp_selected]['all_attributes'].keys()),
                            list(current_dist[grp_selected]['all_attributes'].values()), k=1)[0]

                new_string = re.sub(pattern, '', grp_selected.lower())
                new_string = new_string.replace('-', '')
                new_string = cap_sentence(new_string)

                if selected != 'BLANK':
                    meta["attributes"].append({"name": new_string.upper(), "value": selected.replace(grp_selected, '')})
                    meta["final_sequence"].append({grp_selected: selected})
                    file = df_full[df_full['ATTRIBUTE NAMES'] == selected]['FILE NAMES']
                    file_selected = file.reset_index().iloc[0, 1]
                    meta["sequence"].append({grp_selected: file_selected})

                if selected == 'BLANK':
                    meta["all_blanks"].append({grp_selected: 'BLANK'})

            encoded = str(meta["attributes"]).encode()
            result = hashlib.sha256(encoded)

            if result.hexdigest() not in all_dna:
                final_meta.append(meta)

                all_dna.append(result.hexdigest())

                for var_one in meta["final_sequence"]:
                    current_dist[list(var_one.keys())[0]]['all_attributes'][list(var_one.values())[0]] -= 1
                for var_two in meta["all_blanks"]:
                    current_dist[list(var_two.keys())[0]]['all_attributes'][list(var_two.values())[0]] -= 1
                done = 1

            else:
                print("DNA EXISTS")

    return final_meta

def generate_collection_art(collection_meta: dict, name_id: int):
    i = 1
    for seq in collection_meta['sequence']:
        layer = list(seq.keys())[0]
        element = list(seq.values())[0]
        to_add = Image.open(f"layers/{layer}/{element}")
        if i == 1:
            background = to_add
            i = 2
        else:
            background.paste(to_add, (0, 0), to_add)

    background.save(f'build/images/{name_id}.png', "PNG")
    
    return name_id

def generate_json(collection_meta):
    for x in collection_meta:
        
        meta_copy = x.copy()

        meta_copy['dna'] = hashlib.sha256(str(meta_copy["attributes"]).encode()).hexdigest()

        for popping in ["final_sequence", "sequence", "all_blanks", "edition", "date"]:
            meta_copy.pop(popping)

        name = re.findall(r'\d+', meta_copy['name'])[0]

        # save collection
        json_string = json.dumps(meta_copy)
        with open(f'build/json/{name}.json', 'w') as outfile:
            json.dump(json_string, outfile)
            
def execution ():
    
    all_files = os.listdir()
    
    current_path = os.getcwd()

    
    print('Checking if build folder exist')
    if 'build' not in all_files:
        print('Creating build folder, images folder and json folder')
        os.mkdir(f'{current_path}/build')
        os.mkdir(f'{current_path}/build/images')
        os.mkdir(f'{current_path}/build/json')
    else :
        build_files = os.listdir(f'{current_path}/build')
        print('Checking if images folder in build exist')
        if 'images' not in build_files:
            print('Create images folder in build')
            os.mkdir(f'{current_path}/build/images')
        print('Checking if images folder in build exist')
        if 'json' not in build_files:
            print('Create json folder in build')
            os.mkdir(f'{current_path}/build/json')
            
    print('-- build folder READY --')
        
    if 'layers' not in all_files:
        raise NameError('The layers folder is not in the repository')
    
    if 'attributes.xlsx' not in all_files:
        raise NameError('The File attributes.xlsx is not in the repository')

    # Read all attributes data
    data = pd.read_excel('attributes.xlsx') 
    
    for col in data.columns:
        assert col in ['GROUPS', 'FILE NAMES', 'ATTRIBUTE NAMES', '% DISTRIBUTION'], f'the attributes.xlsx does not contain the column name {col}'
    
    # Forward Fill the Group Name
    data['GROUPS'] = data['GROUPS'].ffill()
    # Remove the raw where there is no File name
    data = data[data['FILE NAMES'].notnull()]
    
    number_generation = int(input('How many unique generation do you want to have ?'))
    print(f'We are going to generate {number_generation} images !')
    
    #### You can determine directly in the code the list of group to remove or you can create an input
    
    # groups_to_remove = input('Enter the name of the groups that you do not want to use seperated with a comma (enter nothing is you need to use all the groups) : ')
    # groups_to_remove = groups_to_remove.split(",")
    groups_to_remove = ['14-FEATHER', 'LEGENDARY']
    
    for group in groups_to_remove:
        print(f'removing {group}')
        data = data[(data['GROUPS'] != group)]
    
    data['% DISTRIBUTION'] = data['% DISTRIBUTION'].astype('float')
    data['ATTRIBUTE NAMES'] = data['ATTRIBUTE NAMES'] + data['GROUPS']
    
    Total_Appearance = data[['GROUPS', '% DISTRIBUTION']].groupby('GROUPS').sum()
    Total_Appearance.reset_index(inplace=True)
    Total_Appearance['layer_order'] = Total_Appearance['GROUPS'].str.extract('(^\d*)').astype(int)
    Total_Appearance.sort_values('layer_order', inplace=True)
    Total_Appearance.reset_index(inplace=True, drop=True)
    
    # create distribution
    distribution = create_distribution_count(
        df_full=data,
        df_grp=Total_Appearance,
        total_amt=number_generation
    )
    
    # create metadata
    collection_metadata = create_metadata(
        count_dist=distribution,
        df_full=data,
        df_grp=Total_Appearance,
        total_amt=number_generation
    )
        
    return collection_metadata

if __name__ == '__main__':

    # create the process pool
    with Pool() as pool:
        
        meta_datas = execution()
        items = [(meta_datas[i], i+1) for i in range(len(meta_datas))]  
        
        # call the same function with different data in parallel
        for result in pool.starmap(generate_collection_art, items):
            print(f'Generation id {result}')
        
        generate_json(collection_meta=meta_datas)
