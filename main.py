# Handles the input, uses typer as a framework
# https://github.com/tiangolo/typer

from typing import Optional
import savezone

import typer

from models.models import StorageMetaInfo
from storage_registry import get_storage_true_name

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

    def _get_percentage_color(p: float):

        p = int(p)

        if p >= 80:
            return typer.colors.BRIGHT_BLUE
        elif p >= 60:
            return typer.colors.GREEN
        elif p >= 40:
            return typer.colors.YELLOW
        elif p >= 20:
            return typer.colors.BRIGHT_RED
        else:
            return typer.colors.RED

    metainfo: StorageMetaInfo = savezone.meta(storage, token)

    typer.echo('')
    if get_storage_true_name(storage) == 'Yandex Disk':
        typer.echo(f'Storage Name: {typer.style("Y", fg=typer.colors.RED)}andex Disk')
    else:
        typer.echo(f'Storage Name: {get_storage_true_name(storage)}')
    typer.echo('')
    typer.secho(f'Available space: {metainfo.available_space_display}',
                fg=_get_percentage_color(metainfo.available_space_percentage),
                bold=True)
    typer.secho(f"That's {metainfo.available_space_percentage}%")
    typer.echo('')
    typer.echo(f'Used space: {metainfo.used_space_display}')
    typer.echo(f'Total space: {metainfo.total_space_display}')


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
