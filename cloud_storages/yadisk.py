from typing import List

from settings import BASE_DIRECTORY
from .http_shortcuts import *
from models.models import StorageMetaInfo, Resource, Size
from .storage import Storage


class YadiskStorage(Storage):

    def __init__(self, token):
        self.token = token

    @classmethod
    def get_oauth_request_url(cls):
        app_id = '684404c2a24f4c46a7ea73447888e225'
        token_url = f'https://oauth.yandex.ru/authorize?response_type=token&client_id={app_id}'
        return token_url


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
        res.created = json.get('created')
        res.md5 = json.get('md5')
        return res

    def list_resources_on_path(self, path: str) -> List[Resource]:
        """
        List all items in directory
        :param path: path to the resource
        """

        response = get_with_OAuth('https://cloud-api.yandex.net/v1/disk/resources',
                                  params={'path': path},
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
        """
        Gets meta info of storage
        """
        response = get_with_OAuth('https://cloud-api.yandex.net/v1/disk/', token=self.token)
        if response.status_code == 200:
            response_read = response.json()
            used_space = response_read['used_space']
            total_space = response_read['total_space']
            return StorageMetaInfo(int(used_space), int(total_space))
        else:
            raise ValueError(f"Something went wrong with YD: Response: "
                             f"{str(response.status_code)} — {response.json()['message']}")

    def create_path(self, remote_path: str) -> None:
        """
        Creates the remote path on yandex disk recursively
        """
        path = remote_path.split('/')

        if len(path) == 0:
            return

        path_to_create = path[0]
        response = put_with_OAuth(f'https://cloud-api.yandex.net/v1/disk/resources?path={path_to_create}',
                                  token=self.token)
        if 199 < response.status_code < 401:
            self.create_path('/'.join(path[1::]))

    def save_resource_to_path(self, resource: Resource, remote_path: str, overwrite: bool) -> Resource or None:
        """
        Put an Item to the directory
        :param resource: resource on the local fs
        :param remote_path: string, path to resource on remote fs
        :return: saved resource or raises exception
        """

        upload_successful_flag = False

        response = get_with_OAuth(f'https://cloud-api.yandex.net/v1/disk/resources/upload?path={remote_path}&overwrite=${overwrite}',
                                  token=self.token)
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
        # There are no base directory folder
        elif response.status_code == 409:
            print(f'$[{__name__}]: Directory does not exist on YDisk, creating...')
            response = put_with_OAuth(f'https://cloud-api.yandex.net/v1/disk/resources?path={BASE_DIRECTORY}', token=self.token)
            if 199 < response.status_code < 401:
                return self.save_resource_to_path(resource, remote_path, overwrite)

        raise ValueError(f"Something went wrong with YD: Response: "
                         f"{str(response.status_code)} — {response.json().get('message', '')}")
