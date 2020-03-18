import json
import os
import shutil
from os import path

from celery import shared_task
from gister.settings import SIA_CACHE_DIR, SIA_REMOTE, SIA_API_BASEPATH
from dashboard.models import Gist, File
from dashboard.utils import SkynetClient as Skynet


def update_metadata(gist, filepath, field, value, type_field, push=False):
    abs_path = path.join(SIA_CACHE_DIR, filepath)
    with open(abs_path, 'r+') as f:
        metadata = json.loads(f.read())
        if type_field == 'files':
            metadata['files'][field]['skynet_url'] = value
        f.seek(0)
        f.write(json.dumps(metadata))
        f.truncate()

    if push:
        skynet_url = Skynet.upload_file(abs_path, custom_filename=f'{gist.uuid}.json', force=True)
        gist.skynet_manifest_url = skynet_url
        gist.save()
        return skynet_url
    return 'No update metadata'


#@shared_task
def upload_file(*args, **kwargs):
    gist_id = kwargs.get('gist_id')
    gist = Gist.objects.get(id=gist_id)
    file_id = kwargs.get('file_id')
    filename = kwargs.get('filename')


    file = File.objects.get(id=file_id, gist_id=gist_id)
    skylink = Skynet.upload_file(path.join(SIA_CACHE_DIR, file.sia_path), custom_filename=filename)

    file.skynet_url = skylink
    file.save()

    push = File.objects.filter(id=file_id, skynet_url='').count() == 0
    metadata = update_metadata(gist, gist.sia_manifest_path, file.file_name, skylink, 'files', push=push)

    print(f'## DONE: {metadata}')
    print(f'== DONE: {file.sia_path} - {skylink}')


@shared_task
def upload_zip(*args, **kwargs):
    gist_id = kwargs.get('gist_id')
    filename = kwargs.get('filename')
    gist = Gist.objects.get(id=gist_id)
    repo_path = path.join(SIA_CACHE_DIR, gist.uuid)

    current_path = os.getcwd()
    os.chdir(SIA_CACHE_DIR)
    shutil.make_archive(gist.uuid, 'zip', repo_path)
    os.chdir(current_path)

    skylink = Skynet.upload_file(f'{repo_path}.zip', custom_filename=filename, portal=SIA_API_BASEPATH)
    gist.skynet_url = skylink
    gist.save()
    print(f'== DONE: {gist.sia_path} - {skylink}')