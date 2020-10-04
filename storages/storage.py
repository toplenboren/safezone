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

    def save_resource_to_path(self, resource: Resource, remote_path: str) -> Resource or None:
        """
        Put a resource to the directory
        """
        pass
