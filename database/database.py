from typing import Any

import pickledb


class Database:
    """A abstraction over KV storage"""

    def __init__(self, db_path: str = 'storage.db'):
        """
        Initializes the database
        :param db_path: string, a path to database
        """
        self.db = pickledb.load(db_path, False)

    def get(self, key: str) -> Any:
        """
        Get item by key from storage
        :param key: string
        :return: item
        """
        return self.db.get(key)

    def set(self, key: str, val: Any) -> None:
        """
        Set
        :param key:
        :param val:
        """
        self.db.set(key, val)
        self.db.dump()

    def delete(self, key: str) -> None:
        """
        Removes the key from the the database
        """
        self.db.rem(key)
        self.db.dump()

    def flush(self) -> None:
        """
        Flushes the database
        """
        self.db.deldb()
        self.db.dump()
