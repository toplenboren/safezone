# Handles the input, uses typer as a framework
# https://github.com/tiangolo/typer

from typing import Optional, List
import savezone

import typer

from models.models import StorageMetaInfo, Resource
from storage_registry import get_storage_true_name
from templates import display_metainfo, display_resource_list, display_exception, display_resource

app = typer.Typer()


@app.command()
def backup(storage_name: str, resource: str, remote: str = '/', token: str or None = None) -> None:
    """
    Backs the resource in the storage name
    :param token: An access token to the storage
    :param remote: A path on the remote storage to save to, defaults to '/'
    :param resource: A path to the resource
    :param storage_name: the name of the storage
    :param path: a path to be backed up
    :return:
    """
    backed_up_resource = savezone.backup(storage_name, resource, remote, token)


@app.command()
def save(storage_name: str, resource: str, remote: str = '/', token: str or None = None):
    """
    Saves a RESOURCE in STORAGE \r\n
    :param resource: A path to the resource
    :param storage_name: A storage name
    :param remote: A path on the remote storage to save to, defaults to '/'
    :param token: An access token to the storage
    """
    # try:
    saved_resource: Resource = savezone.save(resource, remote, storage_name, token)
    display_resource(saved_resource, storage_name)
    # except LookupError as e:
    #    display_exception(e)
    #    return
    # display_saved_resource_report


@app.command()
def meta(storage_name: str, token: str or None = None):
    """
    Shows meta info of STORAGE
    """
    try:
        metainfo: StorageMetaInfo = savezone.meta(storage_name, token)
    except KeyError as e:
        display_exception(e)
        return
    storage_name = get_storage_true_name(storage_name)
    display_metainfo(metainfo, storage_name)


@app.command()
def list(storage_name: str,
         token: str or None = None,
         dir: Optional[str] = typer.Argument(None),
         detailed: Optional[bool] = False):
    """
    Lists all resources in STORAGE in DIR
    """
    if dir is None:
        dir = '/'
    resource_list: List[Resource] = savezone.list(storage_name, dir, token=token)
    typer.echo(f"show list of files in {storage_name} by {dir}")
    storage_name = get_storage_true_name(storage_name)
    display_resource_list(resource_list, storage_name, detailed)


if __name__ == "__main__":
    app()
