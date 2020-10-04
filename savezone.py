# Savezone command processor
# Handles savezone related commands, returns raw data, could be used as a library
import os
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


def save(resource_path: str, remote_path: str, storage_name: str, token) -> Resource or None:
    """
    Tries to save the resource by PATH in STORAGE
    :param resource_path: A local path to the file to save
    :param remote_path: A path on the remote to save to
    :param token: An access token to the storage
    :param storage_name: Storage name
    :return: saved Resource if everything went OK or raises exception
    """
    if os.path.isfile(resource_path):
        storage_class = get_storage_by_name(storage_name)
        storage: Storage = storage_class(token=token)
        try:
            open(resource_path, 'rb')
        except PermissionError or FileNotFoundError:
            raise ValueError(f'Object on {resource_path} couldn`t be opened')
        resource = Resource(True, resource_path)
        return storage.save_resource_to_path(resource, remote_path)
    else:
        raise ValueError(f'Object on {resource_path} is not file')

