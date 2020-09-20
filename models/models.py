class File:
    """A file model"""

    def __init__(self, path: str):
        self.path = path

    def __str__(self):
        return self.path


class StorageMetaInfo:
    """A storage meta information model"""

    @classmethod
    def _kb_to_mb(cls, kb):
        return kb / 1024

    @classmethod
    def _b_to_mb(cls, b):
        return b / 1024 / 1024

    def __init__(self, used_space: int, total_space: int, units: str = 'b'):
        if units == 'b':
            self.used_space = self._b_to_mb(used_space)
            self.total_space = self._b_to_mb(total_space)
            self.units = 'mb'
        elif units == 'kb':
            self.used_space = self._kb_to_mb(used_space)
            self.total_space = self._kb_to_mb(total_space)
            self.units = 'mb'
        else:
            self.used_space = used_space
            self.total_space = total_space
            self.units = units

    def __str__(self):
        return f'{str(int(self.used_space))} {self.units.capitalize()} ' \
               f'/ {str(int(self.total_space))} {self.units.capitalize()}'
