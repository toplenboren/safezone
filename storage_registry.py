# Resolves cloud_storages

from cloud_storages.storage import Storage
from cloud_storages.yadisk import YadiskStorage
from cloud_storages.gdrive import GDriveStorage

STORAGES = [
    {
        'name': 'Yandex Disk',
        'synonyms': ['yandex', 'yd', 'yadisk', 'Yandex Disk'],
        'storage': YadiskStorage
    },
    {
        'name': 'Google Drive',
        'synonyms': ['gdrive', 'google_drive', 'google'],
        'storage': GDriveStorage
    }
]

NEW_LINE = '\r\n'


def _storages_as_string() -> str:
    res = []
    for storage in STORAGES:
        storage_str = [storage['name'], ' (', ', '.join(storage['synonyms']), ')']
        res.append(''.join(storage_str))
    return '\r\n'.join(res)


def find_storage_by_synonym(name: str) -> dict:
    """
    Returns the corresponding storage object
    :param name:
    :return:
    """
    for v in STORAGES:
        if name.lower() in v['synonyms']:
            return v

    raise ValueError(
        f'There are no registered storage named {name}{NEW_LINE}'
        f'List of registered cloud_storages is...{NEW_LINE}'
        f'{_storages_as_string()}')


def get_storage_by_name(name: str) -> Storage:
    """
    Returns the storage class or raises the exception if storage not found
    """
    return find_storage_by_synonym(name)['storage']


def get_storage_true_name(name: str) -> str:
    """
    Returns the first name in the synonyms array
    :param name:
    :return: True name of the storage
    """
    return find_storage_by_synonym(name)['name']
