# Handles the input, uses typer as a framework
# https://github.com/tiangolo/typer

import savezone
import typer
import webbrowser

from database.database import Database
from models.models import StorageMetaInfo, Backup
from typing import Optional, List

from oauth_handler.app import launch_oauth_handler_app
from storage_registry import get_storage_true_name, get_storage_by_name
from templates import display_metainfo, display_exception, display_resource, display_backup_list

app = typer.Typer()


@app.command()
def auth(
    storage_name: str = typer.Option('yandex', '-s'),
) -> None:
    # Get request URI
    storage = get_storage_by_name(storage_name)
    # Check if storage has custom auth setup by checking the auth attribute. If no custom auth is specified -> run OAuth
    use_custom_auth = callable(getattr(storage, "auth", None))
    if use_custom_auth:
        database = Database()
        storage.auth(database)
        print('You can start using the utility now...')
        exit(0)
    else:
        # Open OAuth request URI
        webbrowser.open(storage.get_oauth_request_url())
        print('Please continue in web browser')
        # Start flask web server as daemon
        database = Database()
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
    display_resource(saved_resource.versions[0], storage_name)


@app.command()
def restore(
    resource_id: str,
    storage_name: str = typer.Option('yandex', '-s'),
    target: str = typer.Option(None, '-t'),
    token: str or None = None,
) -> None:
    """
    Restores resource from storage \r\n
    :param resource: A path to the resource
    :param storage_name: the name of the storage
    :param target: A path on the local storage to save to, defaults to './restored'
    :param oauth: An access token to the storage
    :return:
    """
    downloaded_file_path = savezone.restore(resource_id, storage_name, target=target, token=token)
    print(f'File was downloaded, please check {downloaded_file_path}')


@app.command()
def meta(storage_name: str = typer.Option('yandex', '-s'), token: str or None = typer.Option(None, '-t')):
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
def list(storage_name: str = typer.Option('yandex', '-s'),
         token: str or None = None,
         remote_path: Optional[str] = typer.Argument(None),
         detailed: Optional[bool] = False):
    """
    Lists all resources in STORAGE in DIR
    """
    backup_list: List[Backup] = savezone.get_backups(storage_name, token=token)
    storage = get_storage_true_name(storage_name)
    display_backup_list(backup_list, storage)


if __name__ == "__main__":
    app()
