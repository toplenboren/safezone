# Savezone command processor
# Handles savezone related commands, returns raw data, could be used as a library

from typing import List

from storage_registry import get_storage_by_name
from storages.storage import Storage
from models.models import Resource, StorageMetaInfo


def list(storage_name: str, dir: str, token: str or None = None,) -> List[Resource]:
    """
    List all files in DIR in STORAGE
    :param token: Access token to the storage
    :param storage_name: Storage name
    :param dir: Path to the resource
    :return: List of File objects
    """
    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)
    return storage.list_resources_on_path(dir)


def meta(storage_name: str, token: str or None = None) -> StorageMetaInfo:
    """
    Get meta info of the STORAGE (used space + total space)
    :param token: Access token to the storage
    :param storage_name: Storage name
    :return: A StorageMetaInfo object
    """
    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)
    return storage.get_meta_info()


def save(path: str, storage_name: str) -> bool:
    """
    Tries to save the resource by PATH in STORAGE
    :param path: A path of the file or storage
    :param storage_name: Storage name
    :return: True if everything went OK
    """
    pass
