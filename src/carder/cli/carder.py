import typer
from loguru import logger
from carder.cli.commands.download import download_dataset
from carder.cli.commands.match import match_card
from carder.cli.commands.scan import scan


@logger.catch()
def app_factory():
    app = typer.Typer()
    _ = app.command("download")(download_dataset)
    _ = app.command("match")(match_card)
    _ = app.command("scan")(scan)

    return app
