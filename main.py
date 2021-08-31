# Handles the input, uses typer as a framework
# https://github.com/tiangolo/typer

import savezone
import os
import typer
import webbrowser

from cloud_storages.yadisk import YadiskStorage
from database.storage import Storage
from models.models import StorageMetaInfo, Resource, Backup
from typing import Optional, List

from oauth_handler.app import launch_oauth_handler_app
from storage_registry import get_storage_true_name, get_storage_by_name
from templates import display_metainfo, display_resource_list, display_exception, display_resource

app = typer.Typer()


@app.command()
def auth(
    storage_name: str = typer.Option('yandex', '-s'),
) -> None:
    # Get request URI
    storage = get_storage_by_name(storage_name)
    request_uri = storage.get_oauth_request_url()
    # Open OAuth request URI
    webbrowser.open(request_uri)
    print('Please continue in web browser')
    # Start flask web server as daemon
    database = Storage()
    launch_oauth_handler_app(database, storage_name)
    exit(0)


@app.command()
def backup(
    resource: str,
    storage_name: str = typer.Option('yandex', '-s'),
    target: str = typer.Option('/', '-t'),
    token: str or None = None,
    overwrite: bool = typer.Option(False, '-o')
) -> None:
    """
    Backs the resource in the storage name \r\n
    :param resource: A path to the resource
    :param storage_name: the name of the storage
    :param target: A path on the remote storage to save to, defaults to '/'
    :param oauth: An access token to the storage
    :return:
    """
    saved_resource: Backup = savezone.backup(resource, target, storage_name, token, overwrite)
    display_resource(saved_resource.resources[0], storage_name)


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
