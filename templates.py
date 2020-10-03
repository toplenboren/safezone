from typing import List

import typer
from tabulate import tabulate

from models.models import StorageMetaInfo, Resource, Size
from storage_registry import get_storage_true_name


def _to_fixed(num: int or float, digits=2):
    return f"{num:.{digits}f}"


def _display_storage(storage_name: str) -> None:
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
            return typer.colors.BRIGHT_GREEN
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


def display_resource_list(resource_list: List[Resource], storage_name: str, detailed: bool = False) -> None:
    def _get_color_by_type(is_file: bool = False):
        if not is_file:
            return typer.colors.BRIGHT_RED

    def _get_size(size: Size or None, **kwargs) -> str:
        if size is not None:
            return typer.style(f'{_to_fixed(size.mb)} Mb', bold=True, **kwargs)
        return typer.style('-', bold=True, **kwargs)

    def _get_type(is_file: bool = False, **kwargs) -> str:
        title = 'file' if is_file else 'dir'
        return typer.style(title, **kwargs)

    def _get_name(name: str, **kwargs) -> str:
        return typer.style(name, **kwargs)

    _display_storage(storage_name)

    if not detailed:
        for resource in resource_list:
            typer.secho(resource.name, fg=_get_color_by_type(resource.is_file))

    headers = [
        'Name',
        'Type',
        'Size',
    ]

    table = []

    for resource in resource_list:
        override_styles = {'fg': _get_color_by_type(resource.is_file)}

        table.append([
            _get_name(resource.name, **override_styles),
            _get_type(resource.is_file, **override_styles),
            _get_size(resource.size, **override_styles)]
        )

    typer.echo(tabulate(table, headers))


def _display_exception(e: Exception) -> None:
    typer.echo(':(')
    typer.secho(' '.join(e.args), fg=typer.colors.RED)