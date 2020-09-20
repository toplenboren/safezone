# Knows how to resolve storages

from storages.storage import Storage
from storages.yadisk import YadiskStorage

STORAGES = [
    {
        'synonyms': ['yandex', 'yd', 'yadisk', 'Yandex'],
        'storage': YadiskStorage
    }
]


def get_storage_by_name(name: str) -> Storage:
    """
    Returns the storage class or raises the exception if storage not found
    """
    for v in STORAGES:
        if name in v['synonyms']:
            return v['storage']
    raise ValueError(f'There are no registered storage named {name}, list of registered storages is.../r/n' + STORAGES)
