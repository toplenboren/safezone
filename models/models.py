from models.utils import bytes_to_megabytes, kilobytes_to_megabytes


class Resource:
    """A resource model"""

    def __init__(self, is_file: bool, path: str, size: int or None = None, name: str or None = None, url: str or None = None):
        self.is_file = is_file
        self.path = path
        self.size = size
        self.name = name
        if not self.name and len(self.path.split('/')) > 0:
            self.name = self.path.split('/')[-1]
        self.url = url
        self.created = None
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
