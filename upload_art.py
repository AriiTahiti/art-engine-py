import w3storage
from decouple import config
import json

from os import listdir, getcwd, path, rename


def upload_selected_art():
    
    selected_art = listdir('build/images')
    current_path = getcwd()
    w3 = w3storage.API(token=config(f"w3storage_key"))
    
    all_errors = []
    
    idx = 1

    for art in selected_art:
        
        try:

            _num = art[: -4]

            if art != '.DS_Store':

                print(f'Uploading art {art} -- index {idx}')

                readme_cid = w3.post_upload((f'{art}', open(f'{current_path}/build/images/{art}', 'rb')))

                print(f'Updating Metadata of art {art}')

                with open(f'{current_path}/build/json/{_num}.json', 'r') as f:
                    data = json.load(f)
                    data = json.loads(data)
                    del f

                data['image'] = f"https://ipfs.io/ipfs/{readme_cid}"

                with open(f'{current_path}/uploaded/json/{_num}.json', 'w') as json_file:
                    json.dump(data, json_file)
                    del json_file

                print('Moving Image')
                old_image = path.join(f'{current_path}/build/images', f"{_num}.png")
                new_image = path.join(f'{current_path}/uploaded/images', f"{_num}.png")
                
                rename(old_image, new_image)
                print('done')

                idx += 1
                
        except :
            
            print(f'We are experimenting an error with {art} -- Upload it Manually')
            all_errors.append(art)
            idx += 1
            
    print('all errors are : {all_errors}')
    
    

upload_selected_art()

