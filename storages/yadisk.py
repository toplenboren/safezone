from typing import List

from .http_shortcuts import *
from models.models import StorageMetaInfo, File
from .storage import Storage


class YadiskStorage(Storage):
    ACCESS_TOKEN = '684404c2a24f4c46a7ea73447888e225'

    def __init__(self, token):
        if token is None:
            print('didnt have token!')
        self.token = token

    def list_items_in_dir(self, dir: str) -> List[File]:
        """
        List all items in directory
        """
        response = get_with_OAuth('https://cloud-api.yandex.net/v1/disk/resources',
                                  params={'path': dir},
                                  token=self.token)
        if response.status_code == 200:
            print(response)
        else:
            raise ValueError("Something went wrong with YD /r/n " + response.json())

    def put_item_to_dir(self, item, dir: str) -> File or None:
        """
        Put an Item to the directory
        """
        pass

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
            raise ValueError(f"Something went wrong with YD: Статус ответа: "
                             f"{str(response.status_code)} — {response.json()['message']}")
