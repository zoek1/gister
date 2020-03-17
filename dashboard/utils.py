import os

import requests
from siaskynet import Skynet

from gister.settings import SIA_API_BASEPATH

headers = {
    'User-Agent': 'Sia-Agent',
    'Content-Type': 'application/octet-stream',
}


def sia_upload_options(custom_filename='', portal=None):
    options = Skynet.default_upload_options()
    if portal:
        options.portal_url = SIA_API_BASEPATH
        options.custom = True
    else:
        options.custom = False
    options.custom_filename = custom_filename
    return options


class SkynetClient(Skynet):
    @staticmethod
    def upload_file(path, custom_filename='', portal=None, force=False):
        opts = sia_upload_options(custom_filename, portal)
        resp = SkynetClient.upload_file_request(path, opts, force).json()
        print(resp)
        return Skynet.uri_skynet_prefix() + resp["skylink"]

    @staticmethod
    def upload_file_request(path, opts=None, force=False):
        if opts.custom:
            with open(os.path.abspath('.apipassword')) as f:
                password = f.read().strip()

            host = opts.portal_url
            portal_path = opts.portal_upload_path
            remote_path = path.split('cache/')[1]
            url = f'{host}/{portal_path}/{remote_path}?filename={opts.custom_filename}'
            if force:
                url += '&force=true'

            with open(path, 'rb') as f:
                r = requests.post(url, headers=headers, data=f.read(), auth=('', password))

            return r

        return Skynet.upload_file_request(path, opts)