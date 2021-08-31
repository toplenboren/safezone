# Savezone command processor
# Handles savezone related commands, returns raw data, could be used as a library
from datetime import datetime
import os
from typing import List

from storage_registry import get_storage_by_name
from cloud_storages.storage import Storage
from database.storage import Storage as DBStorage
from models.models import Resource, StorageMetaInfo, Backup


# Savezone saves everything to base directory
BASE_DIRECTORY = 'savezone'


def _check_resource(resource_path: str) -> bool:
    """
    Checks if the resource is file and accessible, or checks that all resources in directory are files and accessible
    :param resource_path: A path to the resource
    :return: True if resource is OK to upload, False otherwise
    """
    if os.path.isfile(resource_path):
        try:
            open(resource_path, 'rb')
            return True
        except PermissionError or FileNotFoundError:
            return False
    return False


def list(storage_name: str, dir: str, token: str or None = None, ) -> List[Resource]:
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


def save(resource_path: str, remote_path: str, storage_name: str, token, overwrite: bool) -> Resource or None:
    """
    Tries to save the resource by PATH in STORAGE

    :param resource_path: A local path to the file to save
    :param remote_path: A path on the remote to save to
    :param token: An access token to the storage
    :param storage_name: Storage name

    :return: saved Resource if everything went OK or raises exception
    :raises: ValueError if something went wrong
    """
    if _check_resource(resource_path):
        storage_class = get_storage_by_name(storage_name)
        storage: Storage = storage_class(token=token)
        resource = Resource(True, resource_path)
        return storage.save_resource_to_path(resource, remote_path)
    else:
        raise ValueError(f'Object on {resource_path} couldn`t be opened')


def backup(resource_path: str, remote_path: str, storage_name: str,  token: str or None = None) -> Backup:
    """
    Saves resource from resource_path to the cloud. Resolves access token and provides additional business logic

    :param resource_path: A local path to the file to save
    :param remote_path: A path on the remote to save to
    :param token: An access token to the storage
    :param storage_name: Storage name

    :return: saved Resource if everything went OK or raises exception
    :raises: ValueError if something went wrong
    """

    if not _check_resource(resource_path):
        raise ValueError(f'Object on {resource_path} couldn`t be opened')

    if not token:
        database = DBStorage()
        token_from_storage = database.get(storage_name)
        if not token_from_storage:
            raise ValueError(f'No auth token was found. Please run: python main.py auth -s {storage_name}')
        token = token_from_storage

    # If remote path is not specified - then make it!
    if remote_path in ['/', '']:
        resource_name = resource_path.split('/')[-1]
        remote_path = '/'.join([BASE_DIRECTORY, resource_name])
    else:
        remote_path = BASE_DIRECTORY + '/' + remote_path

    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)
    resource = Resource(True, resource_path)
    print(resource, remote_path)
    saved_resource = storage.save_resource_to_path(resource, remote_path)
    return Backup(datetime.now(), [saved_resource], storage_name, remote_path)


def restore(backup_id: str, path_to_restore: str) -> None:
    """
    Downloads the information from the backup
    :param backup_id: Backup ID contains the storage_name info and the date. Might be partial or might be a keyword:
        available keywords are 'last' and 'first'
    :return:
    """
    pass


def get_backups(storage_name: str or None = None) -> None:
    """
    Gets all backups, so you are able to restore the specific one
    :param storage_name:
    :return:
    """
    pass
