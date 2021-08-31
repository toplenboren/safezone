# Savezone command processor
# Handles savezone related commands, returns raw data, could be used as a library
import os
import base64
import pathlib
from typing import List, Tuple
from datetime import datetime

from settings import BASE_DIRECTORY
from storage_registry import get_storage_by_name
from cloud_storages.storage import Storage
from database.storage import Storage as DBStorage
from models.models import Resource, StorageMetaInfo, Backup


DELIMITER = '-'
ENCODING = 'utf-8'
DATETIME_FORMAT = '%d%m%Y%H%M%S'


# todo (toplenboren) DOES NOT WORK ON WIN
# https://stackoverflow.com/questions/8384737/extract-file-name-from-path-no-matter-what-the-os-path-format
def _encode_resource_id(path: str) -> str:
    abspath = os.path.abspath(path)
    file_name = os.path.basename(abspath)
    return DELIMITER.join([(base64.b32encode(bytes(abspath, ENCODING)).decode(ENCODING)), file_name])


def _decode_resource_id(resource_id: str) -> Tuple[str, str]:
    abspath_b64, file_name = resource_id.split(DELIMITER)
    return base64.b32decode(abspath_b64).decode(ENCODING), file_name


def _get_current_date() -> str:
    now = datetime.now()
    return now.strftime(DATETIME_FORMAT)


def _parse_date(date) -> datetime:
    pass


def _restore_token(storage_name) -> str:
    database = DBStorage()
    token_from_storage = database.get(storage_name)
    if not token_from_storage:
        raise ValueError(f'No auth token was found. Please run: python main.py auth -s {storage_name}')
    return token_from_storage


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


def list(storage_name: str, remote_path: str, token: str or None = None) -> List[Resource]:
    """
    List all files in DIR in STORAGE
    :param token: Access token to the storage
    :param storage_name: Storage name
    :param remote_path: Path to the resource§
    :return: List of File objects
    """

    if not token:
        token = _restore_token(storage_name)

    if remote_path in ['/', '', None]:
        remote_path = BASE_DIRECTORY

    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)
    return storage.list_resources_on_path(remote_path)


def meta(storage_name: str, token: str or None = None) -> StorageMetaInfo:
    """
    Get meta info of the STORAGE (used space + total space)
    :param token: Access token to the storage
    :param storage_name: Storage name
    :return: A StorageMetaInfo object
    """

    if not token:
        token = _restore_token(storage_name)

    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)
    return storage.get_meta_info()


def backup(resource_path: str, remote_path: str, storage_name: str, token: str or None = None,
           overwrite: bool = False) -> Backup:
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
        token = _restore_token(storage_name)

    # If remote path is not specified - then make it!
    # /<BASE>/<ID>/<DATETIME>
    if remote_path in ['/', '']:
        resource_id = _encode_resource_id(resource_path)
        current_date = _get_current_date()
        remote_path = '/'.join([BASE_DIRECTORY, resource_id, current_date])
        print(f'[{__name__}] Calculated resource_id - {resource_id}')
    # If remote path is specified we mount this lad to custom directory
    # todo (toplenboren) learn how to process complex pathes
    else:
        file_name = os.path.basename(resource_path)
        remote_path = BASE_DIRECTORY + '-custom/' + remote_path + '/' + file_name
        print(f'[{__name__}] Saving on external path... {remote_path}. '
              f'Note: You wont be able to fully use this util using -t argument.'
              f' Consider using automatic method instead (leave the -t empty)')

    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)
    resource = Resource(True, resource_path)
    saved_resource = storage.save_resource_to_path(resource, remote_path, overwrite)
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
