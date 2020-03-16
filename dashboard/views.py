import json
import uuid
from os import path

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from git import Repo


from dashboard.models import Gist, File
from gister.settings import SIA_CACHE_DIR, SIA_REMOTE, HOST_URL
from dashboard.tasks import upload_zip, upload_file
from dashboard.utils import sia_upload_options

if SIA_REMOTE:
    from siaskynet import Skynet
else:
    from dashboard.utils import SkynetClient as Skynet


def write_files(directory, files, metadata):
    filenames = []
    filepath_metadata = path.join(directory, 'metadata.json')

    for file in files:
        filepath = path.join(directory, file['name'])
        with open(path.join(SIA_CACHE_DIR, filepath), 'w') as file_manager:
            file_manager.write(file['content'])
        filenames.append(filepath)

    with open(path.join(SIA_CACHE_DIR, filepath_metadata), 'w') as file_manager:
        file_manager.write(json.dumps(metadata))

    return filenames, filepath_metadata


# Create your views here.
def new_gist(request):
    return render(request, 'gist_new.html')


# Create your views here.
def gist_details(request, gist):
    return render(request, 'gist_details.html')

@csrf_exempt
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def create_gist(request):

    gist_id = uuid.uuid1().hex

    files = request.data.get('files')
    raw_metadata = request.data.get('metadata')
    repo_path = path.join(SIA_CACHE_DIR, gist_id)
    repo = Repo.init(repo_path)

    parent = raw_metadata.get('parent', None),
    parent_gist = None
    if parent:
        gist = Gist.objects.filter(sia_path=parent)
        if gist.exists():
            parent_gist = gist.first()

    metadata = {
        'visibility': raw_metadata.get('visibility', 'public'),
        'parent': parent_gist,
        'sia_path': f'{gist_id}.zip',
        'skynet_url': '',
        'description': raw_metadata.get('description', ''),
        'expiration': raw_metadata.get('expiration', 'never'),
        'categories': raw_metadata.get('categories', []),
        'user_address': raw_metadata.get('address', ''),
        'uuid': gist_id
    }

    new_gist = Gist.objects.create(**metadata)

    [filepaths, metadata_path] = write_files(gist_id, files, metadata)
    paths = [path.join(SIA_CACHE_DIR, filepath) for filepath in filepaths]
    repo.index.add([path.join(SIA_CACHE_DIR, metadata_path)] + paths)
    repo.index.commit('Initial revision')

    for filepath in filepaths:
        filename = filepath.strip(f'/{gist_id}')
        print(f'======= {filepath}')
        file = File.objects.create(sia_path=filepath, skynet_url='', file_name=filename, gist=new_gist)
        upload_file.delay(gist_id=new_gist.id, file_id=file.id, filename=filename)

    upload_zip.delay(gist_id=new_gist.id, filename=f'{gist_id}.zip')

    return Response({
        'id': gist_id,
        'url': f'{HOST_URL}/gist/{gist_id}'
    })