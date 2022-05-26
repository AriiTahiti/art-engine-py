from PIL import Image
import pandas as pd
import random
import re
from itertools import chain
import time
import numpy as np
import hashlib


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

# Final Distribution
final_dist = {}

Total_Appearance = data[['GROUPS', '% DISTRIBUTION']].groupby('GROUPS').sum()
Total_Appearance.reset_index(inplace=True)
Total_Appearance['layer_order'] = Total_Appearance['GROUPS'].str.extract('(^\d*)').astype(int)
Total_Appearance.sort_values('layer_order', inplace=True)

for index, row in Total_Appearance.iterrows():
    final_dist[row.GROUPS] = {}

    final_dist[row.GROUPS]['total'] = round(Total_Generation * row['% DISTRIBUTION'] / 100)

    sample = data[data['GROUPS'] == row.GROUPS].reset_index(drop=True)
    nb_grp = sample.index.max()
    new = 0

    final_dist[row.GROUPS]['all_attributes'] = {}
    for index2, row2 in sample.iterrows():
        attribute_prop = round(Total_Generation * row2['% DISTRIBUTION'] / 100)
        new += attribute_prop
        assert attribute_prop > 0
        final_dist[row2.GROUPS]['all_attributes'][row2['ATTRIBUTE NAMES']] = int(attribute_prop)

    if new != round(Total_Generation * row['% DISTRIBUTION'] / 100):
        dif = new - round(Total_Generation * row['% DISTRIBUTION'] / 100)
        number_to_remove = abs(dif)
        for x in range(number_to_remove):
            verif = 0
            while verif == 0:
                n = random.randint(0, nb_grp)
                to_change = sample.loc[n, 'ATTRIBUTE NAMES']
                if final_dist[row2.GROUPS]['all_attributes'][to_change] - 1 > 0:
                    if dif > 0:
                        final_dist[row2.GROUPS]['all_attributes'][to_change] -= 1
                        new -= 1
                    else :
                        final_dist[row2.GROUPS]['all_attributes'][to_change] += 1
                        new += 1
                    verif += 1

    assert new >= round(Total_Generation * row['% DISTRIBUTION'] / 100)
    final_dist[row.GROUPS]['all_attributes']['BLANK'] = Total_Generation - new
    final_dist[row.GROUPS]['available_attributes'] = list(data[data['GROUPS'] == row.GROUPS]['ATTRIBUTE NAMES'].unique())
    final_dist[row.GROUPS]['available_attributes'].append('BLANK')
    assert final_dist[row.GROUPS]['all_attributes']['BLANK'] + new >= Total_Generation

final_meta = []

current_dist = final_dist.copy()

assert len(list(data['FILE NAMES'].unique())) == len(data)
assert len(list(data['ATTRIBUTE NAMES'].unique())) == len(data)

all_dna = []

def category_selected(layer):

    selection = random.choices(list(current_dist[layer]['all_attributes'].keys()),
                            list(current_dist[layer]['all_attributes'].values()), k=1)[0]

    return selection


for x in range(1, Total_Generation+1):

    print(f'Generate #{x}')
    total_nb_layers = Total_Appearance['layer_order'].max()
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
            ]
        }

        for y in range(1, total_nb_layers+1):
            group = Total_Appearance[Total_Appearance['layer_order'] == y]['GROUPS']
            grp_selected = group.reset_index().iloc[0,1]

            selected = category_selected(layer=grp_selected)
            new_string = re.sub(pattern, '', grp_selected.lower())
            new_string = new_string.replace('-', '')
            new_string = cap_sentence(new_string)

            if selected != 'BLANK':
                meta["attributes"].append({"name": new_string, "value": selected})
                meta["final_sequence"].append({grp_selected: selected})
                file = data[data['ATTRIBUTE NAMES'] == selected]['FILE NAMES']
                file_selected = file.reset_index().iloc[0, 1]
                meta["sequence"].append({grp_selected: file_selected})

        encoded = str(meta["attributes"]).encode()
        result = hashlib.sha256(encoded)

        if result.hexdigest() not in all_dna:
            final_meta.append(meta)

            all_dna.append(result.hexdigest())

            for var in meta["final_sequence"]:
                current_dist[list(var.keys())[0]]['all_attributes'][list(var.values())[0]] -= 1

            done = 1

        else:
            print("DNA EXISTS")


k = 0
for new_meta in final_meta:
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
            i=2
        else:
            background.paste(to_add, (0,0), to_add)

    background.save(f'build/images/{k}.png', "PNG")

import json


json_string = json.dumps(final_meta)

# Directly from dictionary
with open('_metadata_to_clean.json', 'w') as outfile:
    json.dump(json_string, outfile)

########### Analysis ###########

metadata = pd.DataFrame(final_meta)

# clean / prepare dataset
layers = ['Accessories', 'Background', 'Bandanas', 'Beard', 'Cloths', 'Extra', 'Eye Cover',
          'Eyes', 'Hats', 'In Mouth', 'Skeleton', 'Teeth']

for var in layers:
    metadata[var] = np.nan

for index, row in metadata.iterrows():
    all_attributes = row.attributes
    for attr in all_attributes:
        metadata.loc[index, attr['name']] = attr['value']

# Assert Background

background = pd.DataFrame(metadata['Background'].value_counts())


# Assert EyeCover

eye_cover = pd.DataFrame(metadata['Eye Cover'].value_counts())
sum(metadata['Eye Cover'].value_counts())

bandanas = pd.DataFrame(metadata['Bandanas'].value_counts())
sum(metadata['Bandanas'].value_counts())

cloths = pd.DataFrame(metadata['Cloths'].value_counts())
sum(metadata['Cloths'].value_counts())

teeth = pd.DataFrame(metadata['Teeth'].value_counts())

skeleton = pd.DataFrame(metadata['Skeleton'].value_counts())


