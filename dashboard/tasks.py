import os
import shutil
from os import path

from celery import shared_task
from gister.settings import SIA_CACHE_DIR, SIA_REMOTE
from dashboard.models import Gist, File
from dashboard.utils import sia_upload_options

if SIA_REMOTE:
    from siaskynet import Skynet
else:
    from dashboard.utils import SkynetClient as Skynet

@shared_task
def upload_file(*args, **kwargs):
    gist_id = kwargs.get('gist_id')
    file_id = kwargs.get('file_id')
    filename = kwargs.get('filename')
    options = sia_upload_options(filename)

    file = File.objects.get(id=file_id, gist_id=gist_id)
    skylink = Skynet.upload_file(path.join(SIA_CACHE_DIR, file.sia_path), options)
    file.skynet_url = skylink
    file.save()
    print(f'== DONE: {file.sia_path} - {skylink}')

@shared_task
def upload_zip(*args, **kwargs):
    gist_id = kwargs.get('gist_id')
    filename = kwargs.get('filename')
    gist = Gist.objects.get(id=gist_id)
    repo_path = path.join(SIA_CACHE_DIR, gist.uuid)
    options = sia_upload_options(filename)

    current_path = os.getcwd()
    os.chdir(SIA_CACHE_DIR)
    shutil.make_archive(gist.uuid, 'zip', repo_path)
    os.chdir(current_path)

    skylink = Skynet.upload_file(f'{repo_path}.zip', options)
    gist.skynet_url = skylink
    gist.save()
    print(f'== DONE: {gist.sia_path} - {skylink}')