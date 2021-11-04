from typing import List

from models.models import Resource, StorageMetaInfo


class Storage:
    """A storage abstract class"""

    def list_resources_on_path(self, remote_path: str, ) -> List[Resource]:
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

    def save_resource_to_path(self, resource: Resource, remote_path: str, overwrite: bool) -> Resource or None:
        """
        Put a resource to the directory
        """
        pass

    def download_resource(self, remote_path: str, local_path) -> str:
        """
        Download a resource from path to folder to local_path and return path to the download
        """
        pass
