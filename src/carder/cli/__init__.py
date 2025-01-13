import typer
from loguru import logger
from carder.cli.commands.download import download
from carder.cli.commands.match import match_card
from carder.cli.commands.scan import scan

@logger.catch()
def app_factory():
    app = typer.Typer(add_completion=False)
    _ = app.command("download")(download)
    _ = app.command("match")(match_card)
    _ = app.command("scan")(scan)

    return app


def run():
    app = app_factory()
    app()
