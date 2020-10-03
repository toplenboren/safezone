# Handles the input, uses typer as a framework
# https://github.com/tiangolo/typer

from typing import Optional, List
import savezone

import typer

from models.models import StorageMetaInfo, Resource
from storage_registry import get_storage_true_name
from templates import display_metainfo, display_resource_list, _display_exception

app = typer.Typer()


@app.command()
def save(file: str, storage: str, token: str or None = None):
    """
    Saves a FILE in STORAGE
    """
    typer.echo(f"saved file {file} in {storage}")


@app.command()
def meta(storage_name: str, token: str or None = None):
    """
    Shows meta info of STORAGE
    """

    try:
        metainfo: StorageMetaInfo = savezone.meta(storage_name, token)
    except KeyError as e:
        _display_exception(e)
        return
    storage_name = get_storage_true_name(storage_name)
    display_metainfo(storage_name, metainfo)


@app.command()
def list(storage_name: str, token: str or None = None, dir: Optional[str] = typer.Argument(None)):
    """
    Lists all resources in STORAGE in DIR
    """
    if dir is None:
        dir = '/'
    resource_list: List[Resource] = savezone.list(storage_name, dir, token=token)
    typer.echo(f"show list of files in {storage_name} by {dir}")
    storage_name = get_storage_true_name(storage_name)
    display_resource_list(resource_list, storage_name)


if __name__ == "__main__":
    app()
