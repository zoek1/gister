import os

import requests
from siaskynet import Skynet

from gister.settings import SIA_API_BASEPATH

headers = {
    'User-Agent': 'Sia-Agent',
    'Content-Type': 'application/octet-stream',
}

def sia_upload_options(custom_filename=''):
    return type('obj', (object,), {
        'portal_url': SIA_API_BASEPATH,
        'portal_upload_path': 'skynet/skyfile',
        'portal_file_fieldname': 'file',
        'portal_directory_file_fieldname': 'files[]',
        'custom_filename': custom_filename
    })


class SkynetClient(Skynet):
    @staticmethod
    def upload_file(path, opts=None):
        resp = SkynetClient.upload_file_request(path, opts).json()
        print(resp)
        return Skynet.uri_skynet_prefix() + resp["skylink"]

    @staticmethod
    def upload_file_request(path, opts=None):

        if opts is None:
            opts = Skynet.default_upload_options()

        with open(os.path.abspath('.apipassword')) as f:
            password = f.read().strip()

        host = opts.portal_url
        portal_path = opts.portal_upload_path
        remote_path = path.split('cache/')[1]
        url = f'{host}/{portal_path}/{remote_path}?filename={opts.custom_filename}'

        with open(path, 'rb') as f:
            r = requests.post(url, headers=headers, data=f.read(), auth=('', password))

        return r