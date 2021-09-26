from datetime import datetime
from typing import List

from models.utils import bytes_to_megabytes, kilobytes_to_megabytes


class Size:
    @classmethod
    def kilobytes_to_megabytes(cls, kilobytes: int or float) -> float:
        return kilobytes / 1024

    @classmethod
    def bytes_to_megabytes(cls, bytes: int or float) -> float:
        return bytes / 1024 / 1024

    # todo(toplenboren) add bytes processing
    def __init__(self, size: float or int, units: str = 'b'):
        self.size = size
        self.units = units

    @property
    def mb(self):
        return self.bytes_to_megabytes(self.size)

    def __str__(self):
        return f'{self.mb} {self.units}'


class Resource:
    """A resource model"""

    def __init__(self, is_file: bool, path: str, size: int or None = None, size_units: str = 'b',
                 name: str or None = None, url: str or None = None, update_time: datetime or None = None):
        self.is_file = is_file
        self.path = path
        self.size = Size(size, size_units)
        self.name = name
        if not self.name and len(self.path.split('/')) > 0:
            self.name = self.path.split('/')[-1]
        self.url = url
        self.updated = update_time
        self.md5 = None
        self.children = None

    def __str__(self):
        return f'{self.name}'


class StorageMetaInfo:
    """A storage meta information model"""

    def __init__(self, used_space: int, total_space: int, units: str = 'b'):
        if units == 'b':
            self.used_space = bytes_to_megabytes(used_space)
            self.total_space = bytes_to_megabytes(total_space)
            self.units = 'mb'
        elif units == 'kb':
            self.used_space = kilobytes_to_megabytes(used_space)
            self.total_space = kilobytes_to_megabytes(total_space)
            self.units = 'mb'
        else:
            self.used_space = used_space
            self.total_space = total_space
            self.units = units

    @property
    def available_space(self) -> float:
        return self.total_space - self.used_space

    @property
    def available_space_percentage(self) -> int:
        return int(100 * self.available_space / self.total_space)

    @property
    def used_space_display(self) -> str:
        return str(int(self.used_space)) + ' ' + self.units.capitalize()

    @property
    def total_space_display(self) -> str:
        return str(int(self.total_space)) + ' ' + self.units.capitalize()

    @property
    def available_space_display(self) -> str:
        return str(int(self.available_space)) + ' ' + self.units.capitalize()

    def __str__(self):
        return f'{self.used_space_display} / {self.total_space_display}'


class Backup:
    """A backup model"""

    def __init__(
            self,
            versions: List[Resource],
            storage: str,
            path: str,
            url: str or None = None,
            name: str or None = None
    ):
        """
        :param resource: A list of all resource versions that have been backed up
        :param storage: A name of the storage that was responsible for the backup
        :param name A name of the resource that was backed up
        :param path A path to the resource that was backed up
        :param url: A url to the remote resource
        """
        self.versions = versions
        self.storage = storage
        self.name = name
        self.path = path
        self.url = url

    def _toJson(self) -> str:
        """Serializes the object to JSON"""
        pass
