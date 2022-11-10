import json
import os
import shutil
from os import path

import requests
from celery import shared_task
from gister.settings import CACHE_DIR, WEB3_STORAGE_TOKEN, WEB3_STORAGE_URL
from dashboard.models import Gist, File


def update_metadata(gist, filepath, field, value, type_field, push=False):
    abs_path = path.join(CACHE_DIR, filepath)
    with open(abs_path, 'r+') as f:
        metadata = json.loads(f.read())
        if type_field == 'files':
            metadata['files'][field]['cid'] = value
        f.seek(0)
        f.write(json.dumps(metadata))
        f.truncate()

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }

    if push:
        with open(abs_path, 'rb') as f:
            response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
            gist.manifest_cid = response.json().get("cid")

            gist.save()
            return gist.manifest_cid
    return 'No update metadata'


#@shared_task
def upload_file(*args, **kwargs):
    gist_id = kwargs.get('gist_id')
    gist = Gist.objects.get(id=gist_id)
    file_id = kwargs.get('file_id')
    filename = kwargs.get('filename')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }

    file = File.objects.get(id=file_id, gist_id=gist_id)
    with open(path.join(CACHE_DIR, file.path), 'rb') as f:
        response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
        file.cid = response.json().get("cid")
        file.save()

        push = File.objects.filter(id=file_id, cid='').count() == 0
        metadata = update_metadata(gist, gist.manifest_path, file.file_name, file.cid, 'files', push=push)

        print(f'## DONE: {metadata}')
        print(f'== DONE: {file.path} - {file.cid}')


@shared_task
def upload_zip(*args, **kwargs):
    gist_id = kwargs.get('gist_id')
    filename = kwargs.get('filename')
    gist = Gist.objects.get(id=gist_id)
    repo_path = path.join(CACHE_DIR, gist.uuid)

    current_path = os.getcwd()
    os.chdir(CACHE_DIR)
    shutil.make_archive(gist.uuid, 'zip', repo_path)
    os.chdir(current_path)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }

    with open(f'{repo_path}.zip', 'rb') as f:
        response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
        gist.cid = response.json().get("cid")
        gist.save()
        print(f'== DONE: {gist.sia_path} - {gist.cid}')