import os

import click
from .utils import touch


# entry point
@click.group()
def exp():
    """Experiment management."""
    pass


@exp.command()
@click.option('--name', '-n', type=str, default=None)
def init(name: str) -> None:
    """Initialize the current folder as an experiment project folder."""
    root_folder = os.path.join(os.getcwd(), '.chino-exp')
    if os.path.isdir(root_folder):
        click.echo('Cannot initialize project with name {0}.'.format(name))
    else:
        try:
            os.makedirs(root_folder)
        except FileExistsError as e:
            click.echo(e)
            return
        touch(os.path.join(root_folder, 'experiments'),
              desc='project {0}'.format(name),
              create_dir=False,
              executable=False)


@exp.command(name='list')
def list_cli():
    """List experiments in current project."""
    pass
