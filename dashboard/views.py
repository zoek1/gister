import json
import uuid
from os import path

import requests
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from git import Repo


from dashboard.models import Gist, File
from gister.settings import CACHE_DIR, HOST_URL, WEB3_STORAGE_URL, WEB3_STORAGE_TOKEN
from dashboard.tasks import upload_zip, upload_file


def write_files(directory, files, metadata):
    filenames = []
    filepath_metadata = path.join(directory, 'metadata.json')

    for file in files:
        filepath = path.join(directory, file['name'])
        with open(path.join(CACHE_DIR, filepath), 'w') as file_manager:
            file_manager.write(file['content'])
        filenames.append({'path': filepath, 'syntax': file.get('syntax', 'plaintext')})

    with open(path.join(CACHE_DIR, filepath_metadata), 'w') as file_manager:
        file_manager.write(json.dumps(metadata))

    return filenames, filepath_metadata


def new_gist(request):
    return render(request, 'gist_new.html', context={
        'title': 'Create gist'
    })


def gist_details(request, gist_id):
    gist = Gist.objects.get(uuid=gist_id)
    files = gist.file_set.all()
    context = {
        'gist': gist,
        'files': files,
        'title': gist.description or f'Gist {gist.uuid}'
    }
    return render(request, 'gist_details.html', context=context)


def all_gists(request):

    gists = Gist.objects.filter(active=True, visibility='public')
    try:
        q = request.GET['profile']
        gists = gists.filter(user_address=q)
    except:
        pass
    try:
        q = request.GET['q']
        gists = gists.filter(Q(description__icontains=q) | Q(file__syntax__icontains=q) | Q(categories__icontains=q))
    except:
        pass
    gists = gists.exclude(manifest_cid=None).distinct().order_by('-created')[:10]

    context = {
        'gists': gists,
        'title': 'All gists'
    }
    return render(request, 'gists.html', context=context)


@csrf_exempt
@api_view(['POST'])
@renderer_classes([JSONRenderer])
def create_gist(request):

    gist_id = uuid.uuid1().hex

    files = request.data.get('files')
    raw_metadata = request.data.get('metadata')
    repo_path = path.join(CACHE_DIR, gist_id)
    repo = Repo.init(repo_path)

    parent = raw_metadata.get('parent', None),
    parent_gist = None
    if parent:
        gist = Gist.objects.filter(path=parent)
        if gist.exists():
            parent_gist = gist.first()

    base_metadata = {
        'visibility': raw_metadata.get('visibility', 'public'),
        'parent': parent_gist,
        'description': raw_metadata.get('description', ''),
        'expiration': raw_metadata.get('expiration', 'never'),
        'categories': raw_metadata.get('categories', []),
        'user_address': raw_metadata.get('address', ''),
        'uuid': gist_id
    }
    params = base_metadata.copy()
    params['path'] = f'{gist_id}.zip'
    params['cid'] = ''

    new_gist = Gist.objects.create(**params)

    metadata = base_metadata.copy()
    metadata['package_path'] = f'{gist_id}.zip'
    metadata['cid_package'] = ''
    metadata['files'] = {file['name']: {'syntax': file['syntax'], 'cid': ''} for file in files}
    metadata['created'] = timezone.now().isoformat()
    # Write and commit files
    [filepaths, metadata_path] = write_files(gist_id, files, metadata)
    paths = [path.join(CACHE_DIR, filepath['path']) for filepath in filepaths]
    metadata_abs_path = path.join(CACHE_DIR, metadata_path)
    repo.index.add([metadata_abs_path] + paths)
    repo.index.commit('Initial revision')

    # Set manifest
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {WEB3_STORAGE_TOKEN}'
    }
    with open(metadata_abs_path, 'rb') as f:
        response = requests.request("POST", f"{WEB3_STORAGE_URL}/upload", headers=headers, data=f)
        new_gist.manifest_cid = response.json().get("cid")
        new_gist.manifest_path = metadata_path
        new_gist.save()

    # Upload files
    for filepath in filepaths:
        print(f'======= {filepath}')
        filename = filepath['path'].split(f'{gist_id}/')[1]
        print(f'======= {filename}')
        file = File.objects.create(path=filepath['path'], cid='', file_name=filename, gist=new_gist, syntax=filepath['syntax'])
        upload_file(gist_id=new_gist.id, file_id=file.id, filename=filename)

    upload_zip.delay(gist_id=new_gist.id, filename=f'{gist_id}.zip')

    return Response({
        'id': gist_id,
        'url': f'{HOST_URL}/gists/{gist_id}',
        'gist': new_gist.get_default_dict()
    })


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_gist(request, gist_id):
    gist = Gist.objects.get(uuid=gist_id)

    return Response(gist.get_default_dict())