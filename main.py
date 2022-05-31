from PIL import Image
import pandas as pd
import random
import re
from itertools import chain
import time
import numpy as np
import hashlib
import json
import os
import shutil


def cap_sentence(s):
  return ''.join((c.upper() if prev == ' ' else c) for c, prev in zip(s, chain(' ', s)))
pattern = r'[0-9]'

Total_Generation = 4840

# Prepare the data
data = pd.read_excel('attributes.xlsx')
data['GROUPS'] = data['GROUPS'].ffill()
data = data[data['FILE NAMES'].notnull()]


data = data[data['GROUPS'] != 'LEGENDARIES']
data = data[data['GROUPS'] != '12-EXTRA']


Total_Appearance = data[['GROUPS', '% DISTRIBUTION']].groupby('GROUPS').sum()
Total_Appearance.reset_index(inplace=True)
Total_Appearance['layer_order'] = Total_Appearance['GROUPS'].str.extract('(^\d*)').astype(int)
Total_Appearance.sort_values('layer_order', inplace=True)


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
            number_to_remove = abs(dif)
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

        assert new == round(total_amt * row['% DISTRIBUTION'] / 100)
        final_dist[row.GROUPS]['all_attributes']['BLANK'] = total_amt - new
        final_dist[row.GROUPS]['available_attributes'] = list(df_full[df_full['GROUPS'] == row.GROUPS]['ATTRIBUTE NAMES'].unique())
        final_dist[row.GROUPS]['available_attributes'].append('BLANK')
        assert final_dist[row.GROUPS]['all_attributes']['BLANK'] + new == total_amt

    assert len(list(df_full['FILE NAMES'].unique())) == len(df_full)
    assert len(list(df_full['ATTRIBUTE NAMES'].unique())) == len(df_full)

    return final_dist


distribution = create_distribution_count(
    df_full=data,
    df_grp=Total_Appearance,
    total_amt=Total_Generation
)


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
                "description": "Generated JRS Collection of 4848 NFTs",
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
                    meta["attributes"].append({"name": new_string, "value": selected})
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


collection_metadata = create_metadata(
    count_dist=distribution,
    df_full=data,
    df_grp=Total_Appearance,
    total_amt=Total_Generation
)

# save collection
json_string = json.dumps(collection_metadata)
with open('final_collection.json', 'w') as outfile:
    json.dump(json_string, outfile)


def generate_collection_art(collection_meta: list):
    k = 0

    for new_meta in collection_meta:
        k += 1
        print(f'{new_meta["name"]}')

        background = None

        i = 1

        for seq in new_meta['sequence']:
            layer = list(seq.keys())[0]
            element = list(seq.values())[0]
            to_add = Image.open(f"layers/{layer}/{element}")
            if i == 1:
                background = to_add
                i = 2
            else:
                background.paste(to_add, (0, 0), to_add)

        background.save(f'build/images/{k}.png', "PNG")


generate_collection_art()

# import data
with open('final_collection.json') as f:
    metadatas =json.loads(f.read())
    collection_metadata = json.loads(metadatas)


for x in collection_metadata:

    meta_copy = x.copy()

    meta_copy['dna'] = hashlib.sha256(str(meta_copy["attributes"]).encode()).hexdigest()

    for popping in ["final_sequence", "sequence", "all_blanks", "edition", "date"]:
        meta_copy.pop(popping)

    name = re.findall(r'\d+', meta_copy['name'])[0]

    # save collection
    json_string = json.dumps(meta_copy)
    with open(f'build/json/{name}.json', 'w') as outfile:
        json.dump(json_string, outfile)


# add random Special Unit (if collection has it)
extra = data[data['GROUPS'] == '12-EXTRA']

for index_three, row_three in extra.iterrows():

    print(row_three['ATTRIBUTE NAMES'])
    selected = []

    rand = random.randint(1, 4041)

    with open(f'build/json/{rand}.json') as f:
        select_meta = json.loads(f.read())
        fit_meta = json.loads(select_meta)

    fit_meta['attributes'].append({"name": "Extra", "value": row_three['ATTRIBUTE NAMES']})

    original = Image.open(f"build/images/{rand}.png")
    to_add = Image.open(f"layers/12-EXTRA/{row_three['FILE NAMES']}")
    original.paste(to_add, (0, 0), to_add)

    # save collection
    json_string = json.dumps(fit_meta)
    with open(f'build/extra_json/{rand}.json', 'w') as outfile:
        json.dump(json_string, outfile)

    original.save(f'build/extra_images/{rand}.png', "PNG")


# Create the legends
legend = data[data['GROUPS'] == 'LEGENDARIES']

id_start = 4840
for index_four, row_four in legend.iterrows():
    id_start += 1
    meta = {
        "name": f"JRS #{id_start}",
        "description": "Generated JRS Collection of 4848 NFTs",
        "image": "",
        "dna": "",
        "attributes": [
        ]
    }

    print(meta['name'])

    meta['attributes'].append({"name": "Legendaries", "value": row_four['ATTRIBUTE NAMES']})
    meta['dna'] = hashlib.sha256(str(meta["attributes"]).encode()).hexdigest()

    # save collection
    json_string = json.dumps(meta)
    with open(f'build/json/{id_start}.json', 'w') as outfile:
        json.dump(json_string, outfile)

    original = Image.open(f"layers/LEGENDARIES/{row_four['FILE NAMES']}")
    original.save(f'build/images/{id_start}.png', "PNG")


# shuffle collection

json_list = os.listdir('build/intermediate_json/')
image_list = os.listdir('build/intermediate_images/')

# os.remove("build/intermediate_json/.DS_Store")

assert len(json_list) == 4848
assert len(image_list) == 4848


matching = []

current_dist = {}
for x in range(1, len(json_list)+1):
    current_dist[str(x)] = 1

all_selected = []

for json_value in json_list:
    name = re.findall(r'\d+', json_value)[0]

    selected = random.choices(list(current_dist.keys()),
                              list(current_dist.values()), k=1)[0]

    current_dist[selected] -= 1

    if selected in all_selected:
        print('inside')

    matching.append((name, selected))

    all_selected.append(selected)


for match in matching:

    print(match[0])

    src_path = f'build/intermediate_json/{match[0]}.json'
    dst_path = f'build/final_json/{match[0]}.json'
    shutil.move(src_path, dst_path)

    # Absolute path of a file
    old_name = f'build/final_json/{match[0]}.json'
    new_name = f'build/final_json/{match[1]}.json'
    os.rename(old_name, new_name)

    src_path = f'build/intermediate_images/{match[0]}.png'
    dst_path = f'build/final_images/{match[0]}.png'
    shutil.move(src_path, dst_path)

    # Absolute path of a file
    old_name = f'build/final_images/{match[0]}.png'
    new_name = f'build/final_images/{match[1]}.png'
    os.rename(old_name, new_name)


