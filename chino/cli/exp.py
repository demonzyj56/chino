import json
import os
import random
import shutil
from string import ascii_lowercase, digits
from typing import Optional, Dict

import click

from chino.cli.utils import touch
from chino.io.fileio import load
from chino.io.lineio import read_lines


# entry point
@click.group()
def exp():
    """Experiment management."""
    pass


@exp.command()
@click.option('--name', '-n', type=str, default=None)
@click.option('--author', '-a', default='Yijie Zeng', help='Author of the file.')
@click.option('--email', '-e', default='yijie.zeng@outlook.com',
              help='Email of the author.')
def init(name: str, author: str, email: str) -> None:
    """Initialize the current folder as an experiment project folder."""
    if name is None:
        name = 'Awesome-{0}'.format(''.join([random.choice(ascii_lowercase+digits) for _ in range(8)]))
    else:
        name = name.replace(' ', '-')
    root_folder = os.path.join(os.getcwd(), '.chino-exp')
    if os.path.isdir(root_folder):
        click.echo('Cannot initialize project with name {0}.'.format(name))
    else:
        try:
            os.makedirs(root_folder)
        except FileExistsError as e:
            click.echo(e)
            return
        info_path = os.path.join(root_folder, 'experiments.json')
        info = dict(name=name, author=author, email=email, exps=[], path=info_path)
        with open(info_path, 'w') as f:
            json.dump(info, f)
        click.echo('Initialized experiment folder for project {0}'.format(name))


@exp.command(name='list')
def list_cli():
    """List experiments in current project."""
    info = get_project_info()
    if info is None:
        click.echo('Experiment project folder not initialized or corrupted.')
        return
    if len(info['exps']) == 0:
        click.echo('Unable to find any experiments.')
        return
    exps = sorted(info['exps'], key=lambda item: item['name'])
    for e in exps:
        click.echo('{0}: {1}'.format(e['name'], e['desc']))


@exp.command()
@click.option('--annotation', '-a', type=str, prompt=True,
              help='Anno to help explain the purpose the of the experiment.')
@click.option('--desc', '-d', type=str, prompt=True,
              help='Descriptions of the experiment.')
@click.option('--entrypoint', '-e', type=str, default='run.sh')
def new(annotation: str, desc: str, entrypoint: str) -> None:
    """Add an experiment."""
    info = get_project_info()
    if info is None:
        click.echo('Experiment project folder not initialized or corrupted.')
        return
    exp_name = 'E{:02d}'.format(len(info['exps'])+1)
    if len(annotation) > 0:
        exp_name += '-{}'.format(annotation.replace(' ', '-'))
    entry_file = os.path.join(os.getcwd(), exp_name, entrypoint)
    touch(entry_file,
          author=info['author'],
          email=info['email'],
          desc=desc,
          record_create_datetime=True,
          create_dir=True,
          executable=True)
    info['exps'].append({'name': exp_name, 'desc': desc, 'entrypoint': entry_file})
    with open(info['path'], 'w') as f:
        json.dump(info, f)
    click.echo('Initialized experiment {0}'.format(exp_name))


@exp.command()
def pop():
    """Remove the latest experiment."""
    info = get_project_info()
    if info is None:
        click.echo('Experiment project folder not initialized or corrupted.')
        return
    if len(info['exps']) == 0:
        click.echo('No experiments are currently set up.')
        return
    exp_name = info['exps'][-1]['name']
    exp_path = os.path.join(os.getcwd(), exp_name)
    if click.confirm('Remove {0}?'.format(exp_path), abort=True):
        shutil.rmtree(exp_path)
        info['exps'].pop()
        with open(info['path'], 'w') as f:
            json.dump(info, f)
        click.echo('Removed experiment {0} from {1}.'.format(exp_name, exp_path))


def get_project_info(folder: str = None) -> Optional[Dict]:
    if folder is None:
        folder = os.getcwd()
    try:
        info = load(os.path.join(os.getcwd(), '.chino-exp', 'experiments.json'))
    except:
        return None
    return info
