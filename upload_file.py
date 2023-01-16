from requests import request
from decouple import config
import json
from os import listdir, getcwd, walk, path, sep, rename, remove
import random
import shutil
from requests import Session, Request


def pinata_upload(directory):
    
    files = []
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    files.append(('pinataMetadata', (None, '{"name":"' + directory.split(sep)[-1] + '"}')))

    for root, dirs, files_ in walk(path.abspath(directory)):
        for f in files_:
            complete_path = path.join(root, f)
            files.append(('file', (sep.join(complete_path.split(sep)[-2:]), open(complete_path, 'rb'))))
            
    built_request = Request('POST', url,
                            headers={
                                'Authorization': f'Bearer {config(f"pinata_token")}',
                            },
                            files=files
                            ).prepare()

    response = Session().send(built_request).json()

    print(response)
    
    print(f"New Token URI is {response['IpfsHash']}")


current_location = getcwd()

pinata_upload(f'{current_location}/waiting')

