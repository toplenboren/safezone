# Savezone command processor
# Handles savezone related commands, returns raw data, could be used as a library
import os
import shutil
import base64

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
BASE_TEMP_DIRECTORY = 'temp'
BASE_BACKUPS_DIRECTORY = 'restored'


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
    return datetime.strptime(date, DATETIME_FORMAT)


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
    return True


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
    print(f'[{__name__}] Calculating remote file path...')
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

    # Archiving the directory or file in order not to do recursive stuff
    print(f'[{__name__}] Archiving resource...')
    archived_file_path = f'{BASE_TEMP_DIRECTORY}/{resource_id}'
    # https://stackoverflow.com/questions/30049201/how-to-compress-a-file-with-shutil-make-archive-in-python
    if os.path.isfile(resource_path):
        abspath = os.path.abspath(resource_path)
        head, tail = os.path.split(abspath)
        shutil.make_archive(archived_file_path, 'zip', head, tail)
    elif os.path.isdir(resource_path):
        shutil.make_archive(archived_file_path, 'zip', resource_path)
    archived_file_path += '.zip'

    print(f'[{__name__}] Saving archived file on remote file path...')
    try:
        storage_class = get_storage_by_name(storage_name)
        storage: Storage = storage_class(token=token)
        resource = Resource(True, archived_file_path)
        saved_resource = storage.save_resource_to_path(resource, remote_path, overwrite)
    finally:
        print(f'[{__name__}] Deleting temp files...')
        os.unlink(archived_file_path)

    return Backup([saved_resource], storage_name, resource_path)


def restore(backup_path: str, storage_name: str, target: str or None = None, token: str or None = None) -> str:
    """
    Downloads the information from the backup
    :returns path to the file
    """
    if not token:
        token = _restore_token(storage_name)

    print(f'[{__name__}] Getting storage...')
    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)

    # Handle files that were saved on a normal basis
    remote_path_resource_id = backup_path.split('/')[-2]
    _, original_name = _decode_resource_id(remote_path_resource_id)

    # Handle files saved under /custom folder
    # pass

    if target is None:
        print(f'[{__name__}] Calculating local file path...')
        dl_target = f"{BASE_BACKUPS_DIRECTORY}/" + original_name + ".zip"
        target = f"{BASE_BACKUPS_DIRECTORY}/" + original_name
        if os.path.exists(target):
            raise ValueError(f"Path {target} is not empty. Please deal with it, then try to restore file again")
    else:
        raise NotImplementedError()

    print(f'[{__name__}] Downloading file...')
    storage.download_resource(backup_path, dl_target)

    try:
        print(f'[{__name__}] Unpacking file...')
        shutil.unpack_archive(dl_target, target, 'zip')
        return target
    finally:
        os.unlink(dl_target)


def get_backups(storage_name: str, token: str or None = None) -> List[Backup]:
    """
    Gets all backups that are on the storage in human-readable format
    :param storage_name:
    :return:
    """
    if not token:
        token = _restore_token(storage_name)

    print(f'[{__name__}] Getting storage...')
    storage_class = get_storage_by_name(storage_name)
    storage: Storage = storage_class(token=token)

    backups = []
    print(f'[{__name__}] Getting list of remote backups...')

    try:
        remote_resources = storage.list_resources_on_path(BASE_DIRECTORY)
        for remote_resource in remote_resources:
            try:
                local_resource_path, local_resource_name = _decode_resource_id(remote_resource.name)

                remote_resource_versions = storage.list_resources_on_path(remote_resource.path)
                backup = Backup(
                    versions=remote_resource_versions,
                    url=remote_resource.url,
                    storage=storage_name,
                    path=local_resource_path,
                    name=local_resource_name,
                )
                backups.append(backup)

            except Exception as e:
                print(f'[{__name__}] Warning: couldn\'t get backups for {remote_resource.name}. Reason: {e}')
                continue
    except ValueError as e:
        if '404' in e.args:
            print(f'[{__name__}] Can\'t get backups')
            return []

    return backups
