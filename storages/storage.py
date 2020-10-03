from typing import List

from models.models import Resource, StorageMetaInfo


class Storage:
    """A storage abstract class"""

    def list_resources_on_path(self, dir: str, ) -> List[Resource]:
        """
        List all items in directory
        :param dir: directory
        """
        pass

    def get_meta_info(self) -> StorageMetaInfo:
        """
        Gets meta info of storage
        """
        pass

    def put_resource_to_path(self, item, dir: str) -> Resource or None:
        """
        Put an Item to the directory
        """
        pass
