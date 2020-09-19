from typing import Optional

import typer

app = typer.Typer()


@app.command()
def save(file: str, storage: str):
    """
    Saves a FILE in STORAGE
    """
    typer.echo(f"saved file {file} in {storage}")


@app.command()
def meta(storage: str):
    """
    Shows meta info of STORAGE
    """
    typer.echo(f"show meta info of {storage}")


@app.command()
def list(storage: str, dir: Optional[str] = typer.Argument(None)):
    """
    Lists all files in STORAGE in DIR
    """
    if dir is None:
        dir = '/'
    typer.echo(f"show list of files in {storage} by {dir}")


if __name__ == "__main__":
    app()
