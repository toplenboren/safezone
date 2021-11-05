from __future__ import print_function

import json
from typing import List
from functools import lru_cache

from cloud_storages.http_shortcuts import *
from database.database import Database
from models.models import StorageMetaInfo, Resource, Size
from cloud_storages.storage import Storage
from client_config import GOOGLE_DRIVE_CONFIG

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

GOOGLE_DRIVE = 'gdrive'
SAVEZONE_FOLDER_ID = '1fs-iwWCNzQ1R5mGYgHLw6ZqUTA6vRben'


class GDriveStorage(Storage):

    def __init__(self, token):
        self.token = token

    @lru_cache(maxsize=None)
    def _get_folder_id_by_name(self, name: str) -> str:
        """
        Google drive has a quirk - you can't really use normal os-like paths - first you need to get an ID of the folder
        This function searches for folders with specified name
        """

        response = get_with_OAuth(
            f"https://www.googleapis.com/drive/v3/files",
            params={
                'fields': '*',
                'q': f"name = '{name}' and mimeType = 'application/vnd.google-apps.folder'"
            },
            token=self.token
        )

        if response.status_code == 200:
            response_as_json = response.json()
            try:
                result = response_as_json['files'][0]['id']
                return result
            except IndexError as e:
                raise ValueError(f"Something went wrong with GD: Error: {e}")
        else:
            raise ValueError(f"Something went wrong with GD: Response: "
                             f"{str(response.status_code)} — {response.json()}")

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
            if 'folder' in json['mimeType']:
                is_file = False
            # You don't have pathes in google drive, instead -- you have an id
            path = json['id']
        except KeyError:
            return None
        res = Resource(is_file, path)
        res.size = Size(json.get('size'), 'b') if json.get('size') else None
        res.name = json.get('name')
        res.url = json.get('webContentLink')
        res.updated = json.get('modifiedTime')
        res.md5 = json.get('md5Checksum')
        return res

    def list_resources_on_path(self, remote_path: str) -> List[Resource]:
        """
        List all items in directory
        :param path: path to the resource
        """

        folder_id = self._get_folder_id_by_name(remote_path)

        response = get_with_OAuth(
            f"https://www.googleapis.com/drive/v3/files",
            params={
                'fields': '*',
                'q': f"'{folder_id}' in parents"
            },
            token=self.token
        )

        if response.status_code == 200:
            result = []
            response_as_json = response.json()
            files = response_as_json['files']

            for resource in files:
                res: Resource or None = self._deserialize_resource(resource)
                if res is not None:
                    result.append(res)

            return result
        else:
            raise ValueError(f"Something went wrong with YD: Response: "
                             f"{str(response.status_code)} — {response.json()['message']}")

    def get_meta_info(self) -> StorageMetaInfo:
        response = get_with_OAuth('https://www.googleapis.com/drive/v3/about?fields=*', token=self.token)
        if response.status_code == 200:
            response_read = response.json()
            used_space = response_read.get('storageQuota', {}).get('usage')
            total_space = response_read.get('storageQuota', {}).get('limit')
            return StorageMetaInfo(int(used_space), int(total_space))
        else:
            raise ValueError(f"Something went wrong with GD: Response: "
                             f"{str(response.status_code)} — {response.json()['message']}")

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
    'https://www.googleapis.com/auth/drive'
]


def main():
    storage = GDriveStorage(None)
    db = Database('../storage.db')
    storage.auth(db)

    authed_storage = GDriveStorage(json.loads(db.get(GOOGLE_DRIVE))['token'])
    result = authed_storage.list_resources_on_path('savezone')

    print(result)


if __name__ == '__main__':
    main()