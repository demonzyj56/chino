import click

from .exp import exp
from .utils import touch_cli, config


@click.group()
def cli():
    """chino cli toolbox."""
    pass


cli.add_command(exp)
cli.add_command(touch_cli)
cli.add_command(config)
