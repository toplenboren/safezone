from typing import List

from models.models import File, StorageMetaInfo


class Storage:
    """A storage abstract class"""

    def list_items_in_dir(self, dir: str) -> List[File]:
        """
        List all items in directory
        """
        pass

    def get_meta_info(self) -> StorageMetaInfo:
        """
        Gets meta info of storage
        """
        pass

    def put_item_to_dir(self, item, dir: str) -> File or None:
        """
        Put an Item to the directory
        """
        pass
