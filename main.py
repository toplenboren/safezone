# Handles the input, uses typer as a framework
# https://github.com/tiangolo/typer

from typing import Optional
import savezone

import typer

from models.models import StorageMetaInfo

app = typer.Typer()


@app.command()
def save(file: str, storage: str, token: str or None = None):
    """
    Saves a FILE in STORAGE
    """
    typer.echo(f"saved file {file} in {storage}")


@app.command()
def meta(storage: str, token: str or None = None):
    """
    Shows meta info of STORAGE
    """
    metainfo: StorageMetaInfo = savezone.meta(storage, token)
    typer.echo(metainfo)


@app.command()
def list(storage: str, token: str or None = None, dir: Optional[str] = typer.Argument(None)):
    """
    Lists all files in STORAGE in DIR
    """
    if dir is None:
        dir = '/'
    typer.echo(f"show list of files in {storage} by {dir}")


if __name__ == "__main__":
    app()
