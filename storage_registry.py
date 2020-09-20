# Resolves storages

from storages.storage import Storage
from storages.yadisk import YadiskStorage

STORAGES = [
    {
        'name': 'Yandex Disk',
        'synonyms': ['yandex', 'yd', 'yadisk', 'Yandex Disk'],
        'storage': YadiskStorage
    }
]


def find_storage_by_synonym(name: str) -> dict:
    """
    Returns the corresponding storage object
    :param name:
    :return:
    """
    for v in STORAGES:
        if name.lower() in v['synonyms']:
            return v
    raise ValueError(f'There are no registered storage named {name}, list of registered storages is.../r/n' + STORAGES)


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
