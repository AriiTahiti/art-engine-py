
import json
from os import getcwd, listdir


def verify_metadata():
    
    current_path = getcwd()
    
    description = "Generated JRS private collection of 4,444 unique Pirates"
    
    
    for file in list(listdir(f'{current_path}/uploaded/json')):
        if '.json' in file:
                        
            with open(f'{current_path}/uploaded/json/{file}', 'r') as f:
                data = json.load(f)
                del f
                
            assert 'JRS #' in data['name'], f'Name in File {file} is not good'
            
            assert data['description'] ==  description,  f'Description in File {file} is not good'
            
            assert 'https://ipfs.io/ipfs/' in  data['image'],  f'IPFS (image) in File {file} is not good'
            
            # Verify that the cid is correct
            cid = data['image'].replace('https://ipfs.io/ipfs/', '')
            
            assert len(cid) == 59,  f'CID (image) in File {file} is not good'
            
            assert data['dna'] !=  '',  f'DNA in File {file} doen not exist'
            
            assert isinstance(data['attributes'], list),  f'attributes in File {file} is not a list'



verify_metadata()

manual = []

def shuffle_collection():

    idx = 1
    
    current_path = getcwd()
    all_json = list(listdir(f'{current_path}/uploaded/json'))

    for json_file in all_json:
        
        if '.json' in json_file:
            
            print(json_file)

            _num = json_file[: -5]
            
            if _num in ['4104', '4166']:
                manual.append([_num, idx])
                

            with open(f'{current_path}/uploaded/json/{_num}.json', 'r') as f:
                data = json.load(f)
                del f
                
            data['name'] = f'JRS #{idx}'

            with open(f'{current_path}/shuffled/{idx}', 'w') as f:
                json.dump(data, f)
                del f

            idx += 1
            

# shuffle_collection()

def verify_metadata():
    
    current_path = getcwd()
    
    description = "Generated JRS private collection of 4,444 unique Pirates"
    
    for file in list(listdir(f'{current_path}/shuffled')):
        
        print(file)
                        
        with open(f'{current_path}/shuffled/{file}', 'r') as f:
            data = json.load(f)
            del f
        
        assert f'JRS #{file}' in data['name'], f'Name in File {file} is not good'
        
        assert data['description'] ==  description,  f'Description in File {file} is not good'
        
        assert 'https://ipfs.io/ipfs/' in  data['image'],  f'IPFS (image) in File {file} is not good'
        
        # Verify that the cid is correct
        cid = data['image'].replace('https://ipfs.io/ipfs/', '')
        
        assert len(cid) == 59,  f'CID (image) in File {file} is not good'
        
        assert data['dna'] !=  '',  f'DNA in File {file} doen not exist'
        
        assert isinstance(data['attributes'], list),  f'attributes in File {file} is not a list'
        
        for att in data['attributes']:
            
            for key, value in att.items():
                
                assert key in ['value', 'trait_type'], 'ERROR'


verify_metadata()



current_path = getcwd()
len(list(listdir(f'{current_path}/shuffled_fixed')))

        
        