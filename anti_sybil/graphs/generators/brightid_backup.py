import sys
sys.path.append('../../')

import anti_sybil.utils
import os
import requests
import sys

BACKUP_URL = 'https://storage.googleapis.com/brightid-backups/brightid.tar.gz'


def generate(data):
    if not BACKUP_URL:
        print('Set the backup url first.')
        sys.exit()
    if not os.path.exists(data['file_path']):
        os.makedirs(data['file_path'])
    rar_addr = os.path.join(data['file_path'], 'brightid.tar.gz')
    zip_addr = os.path.join(data['file_path'], 'brightid.zip')
    backup = requests.get(BACKUP_URL)
    with open(rar_addr, 'wb') as f:
        f.write(backup.content)
    anti_sybil.utils.tar_to_zip(rar_addr, zip_addr)
    json_graph = anti_sybil.utils.from_dump(zip_addr)
    graph = anti_sybil.utils.from_json(json_graph)
    return graph
