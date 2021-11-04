from __future__ import print_function

import json
from typing import List

from cloud_storages.http_shortcuts import *
from database.database import Database
from models.models import StorageMetaInfo, Resource, Size
from cloud_storages.storage import Storage
from client_config import GOOGLE_DRIVE_CONFIG

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

GOOGLE_DRIVE = 'gdrive'


class GDriveStorage(Storage):

    def __init__(self, token):
        self.token = token

    @classmethod
    # todo (toplenboren) remove databaase argument dependency :(
    def auth(cls, db: Database):
        creds = None
        creds_from_db = db.get(GOOGLE_DRIVE)
        if creds_from_db:
            creds = Credentials.from_authorized_user_info(json.loads(creds_from_db), SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(GOOGLE_DRIVE_CONFIG, SCOPES)
                creds = flow.run_local_server(port=0)
            db.set(GOOGLE_DRIVE, creds.to_json())

    @classmethod
    def _deserialize_resource(cls, json: dict) -> Resource or None:
        """
        Tries to parse Resource from YD to Resource object
        :param json:
        :return:
        """
        try:
            is_file = True
            if json['type'] == 'dir':
                is_file = False
            path = json['path']
        except KeyError:
            return None
        res = Resource(is_file, path)
        res.size = Size(json.get('size'), 'b') if json.get('size') else None
        res.name = json.get('name')
        res.url = json.get('file')
        res.updated = json.get('modified')
        res.md5 = json.get('md5')
        return res

    def list_resources_on_path(self, remote_path: str) -> List[Resource]:
        """
        List all items in directory
        :param path: path to the resource
        """

        response = get_with_OAuth('https://cloud-api.yandex.net/v1/disk/resources',
                                  params={'path': remote_path},
                                  token=self.token)
        if response.status_code == 200:
            result = []
            response_as_json = response.json()
            _embedded_objects = response_as_json['_embedded']['items']

            for resource in _embedded_objects:
                res: Resource or None = self._deserialize_resource(resource)
                if res is not None:
                    result.append(res)

            return result
        else:
            raise ValueError(f"Something went wrong with YD: Response: "
                             f"{str(response.status_code)} — {response.json()['message']}")

    def get_meta_info(self) -> StorageMetaInfo:


    def create_path(self, remote_path: List[str]) -> None:
        """
        Creates the remote path on yandex disk
        """
        print(f'[{__name__}] Trying to create directory {"/".join(remote_path)} on remote...')

        dir_to_create = []

        for dir in remote_path:
            dir_to_create.append(dir)
            path_to_create = '/'.join(dir_to_create)
            response = put_with_OAuth(f'https://cloud-api.yandex.net/v1/disk/resources?path={path_to_create}',
                                      token=self.token)
            if 199 < response.status_code < 401:
                print(f'[{__name__}] Created directory {path_to_create}')
                continue
            elif response.status_code == 409 and 'уже существует' in response.json().get('message', ''):
                continue
        return

    def save_resource_to_path(self, resource: Resource, remote_path: str, overwrite: bool, _rec_call:bool = False) -> Resource or None:
        """
        Put an Item to the directory
        :param resource: resource on the local fs
        :param remote_path: string, path to resource on remote fs
        :param _rec_call: bool, a system parameter, whether or not this function was called as a recursive call
        :return: saved resource or raises exception
        """

        upload_successful_flag = False

        response = get_with_OAuth(
            f'https://cloud-api.yandex.net/v1/disk/resources/upload?path={remote_path}&overwrite=${overwrite}',
            token=self.token
        )
        if response.status_code == 200:
            response_read = response.json()
            upload_link = response_read['href']

            with open(resource.path, 'rb') as f:
                files = f
                response = put_with_OAuth(upload_link, data=files)
                if 199 < response.status_code < 401:
                    upload_successful_flag = True

            response = get_with_OAuth(f'https://cloud-api.yandex.net/v1/disk/resources?path={remote_path}',
                                      token=self.token)
            resource_metainfo = self._deserialize_resource(response.json())
            if 199 < response.status_code < 401:
                return resource_metainfo
            elif upload_successful_flag:
                return resource

        # This dir is not present in the storage
        # We use _rec_call to tell that the next call was made as recursive call, so we don't cause SO
        elif response.status_code == 409 and not _rec_call:
            # We don't need to create a folder with the name equal to the filename, so we do [:-1]
            self.create_path(remote_path.split('/')[:-1])
            return self.save_resource_to_path(resource, remote_path, overwrite, _rec_call=True)

        raise ValueError(f"Something went wrong with YD: Response: "
                         f"{str(response.status_code)} — {response.json().get('message', '')}")

    def download_resource(self, remote_path, local_path) -> str:

        response = get_with_OAuth(
            f'https://cloud-api.yandex.net/v1/disk/resources/download?path={remote_path}',
            token=self.token
        )
        if response.status_code == 200:
            response_read = response.json()
            dl_url = response_read.get('href')
        else:
            raise ValueError(f"[{__name__}] Something went wrong with YD: Response: "
                             f"{str(response.status_code)} — {response.json()['message']}")

        file = requests.get(dl_url)
        open(local_path, 'wb').write(file.content)

        return local_path


# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]


def main():
    storage = GDriveStorage(None)
    db = Database('../storage.db')
    storage.auth(db)

    authed_storage = GDriveStorage(json.loads(db.get(GOOGLE_DRIVE))['token'])
    meta = authed_storage.get_meta_info()

    print(meta)

    #
    # creds = json.loads(db.get(GOOGLE_DRIVE))
    #
    # service = build('drive', 'v3', credentials=creds)
    #
    # # Call the Drive v3 API
    # results = service.files().list(
    #     pageSize=10, fields="nextPageToken, files(id, name)"
    # ).execute()
    # items = results.get('files', [])
    #
    # if not items:
    #     print('No files found.')
    # else:
    #     print('Files:')
    #     for item in items:
    #         print(u'{0} ({1})'.format(item['name'], item['id']))


if __name__ == '__main__':
    main()