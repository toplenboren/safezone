from typing import List

import typer

from models.models import StorageMetaInfo, Resource
from storage_registry import get_storage_true_name


def _display_storage(storage_name) -> None:
    typer.echo('')
    if storage_name == 'Yandex Disk':
        typer.echo(f'Storage Name: {typer.style("Y", fg=typer.colors.RED)}andex Disk')
    else:
        typer.echo(f'Storage Name: {get_storage_true_name(storage_name)}')
    typer.echo('')


def display_metainfo(metainfo: StorageMetaInfo, storage_name: str) -> None:
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
        return typer.colors.RED

    _display_storage(storage_name)
    typer.secho(f'Available space: {metainfo.available_space_display}',
                fg=_get_percentage_color(metainfo.available_space_percentage),
                bold=True)
    typer.secho(f"That's {metainfo.available_space_percentage}%")
    typer.echo('')
    typer.echo(f'Used space: {metainfo.used_space_display}')
    typer.echo(f'Total space: {metainfo.total_space_display}')


def display_resource_list(resource_list: List[Resource], storage_name: str) -> None:
    def _get_color_by_type(is_file: bool = False):
        if not is_file:
            return typer.colors.BRIGHT_RED

    _display_storage(storage_name)
    for resource in resource_list:
        typer.secho(resource.name, fg=_get_color_by_type(resource.is_file))


def _display_exception(e: Exception) -> None:
    typer.echo(':(')
    typer.secho(' '.join(e.args), fg=typer.colors.RED)
