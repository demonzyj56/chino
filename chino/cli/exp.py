import json
import os
import random
import re
import shutil
from string import ascii_lowercase, digits
from typing import Optional, Dict

import click

from chino.cli.utils import touch
from chino.io.fileio import load


PAT = re.compile(r'^E(\d\d)(-.*|$)')  # match Exx or Exx-xxxxx


# entry point
@click.group()
def exp():
    """Experiment management."""
    pass


@exp.command()
@click.option('--name', '-n', type=str, default=None)
@click.option('--author', '-a', default=None, help='Author of the file.')
@click.option('--email', '-e', default=None, help='Email of the author.')
def init(name: str, author: str, email: str) -> None:
    """Initialize the current folder as an experiment project folder."""
    if name is None:
        name = 'Awesome-{0}'.format(''.join([random.choice(ascii_lowercase+digits) for _ in range(8)]))
    else:
        name = name.replace(' ', '-')
    try:
        personal_info = json.load(open(os.path.join(os.path.expanduser('~'), '.chino', 'settings.json'), 'r'))
    except FileNotFoundError:
        personal_info = None
    if author is None and personal_info is not None:
        author = personal_info.get('name', None)
    if email is None and personal_info is not None:
        email = personal_info.get('email', None)
    root_folder = os.path.join(os.getcwd(), '.chino-exp')
    if os.path.isdir(root_folder):
        click.echo('Cannot initialize project with name {0}.'.format(name))
        return
    else:
        try:
            os.makedirs(root_folder)
        except FileExistsError as e:
            click.echo(e)
            return
        info_path = os.path.join(root_folder, 'experiments.json')
        info = dict(name=name, author=author, email=email, exps=[], path=info_path)
    # catch existing experiments
    exist_exps = []
    for folder in os.listdir(os.getcwd()):
        if not os.path.isdir(folder):
            continue
        m = PAT.search(folder)
        if m is not None:
            exist_exps.append(m.group(0))
    if len(exist_exps) > 0 and click.confirm(
            "Found existing experiments:\n\n{}\n\nAdd to current project?".format('\n'.join(exist_exps))
    ):
        for exp_name in exist_exps:
            info['exps'].append({'name': exp_name, 'desc': None, 'entrypoint': None, 'commit_id': None})
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
        click.echo('{0} ({1}): {2}'.format(e['name'], e['commit_id'], e['desc']))


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
    cur_exp_names = [PAT.search(item['name']) for item in info['exps']]
    idx = [int(m.group(1)) for m in cur_exp_names if m is not None]
    max_idx = max(idx) if len(idx) > 0 else 0
    exp_name = 'E{:02d}'.format(max_idx + 1)
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
    info['exps'].append({'name': exp_name, 'desc': desc, 'entrypoint': entry_file, 'commit_id': None})
    with open(info['path'], 'w') as f:
        json.dump(info, f)
    click.echo('Initialized experiment {0}'.format(exp_name))


@exp.command()
@click.option('--name', '-n', type=str, default=None,
              help='Name of the experiment.')
@click.option('--commit_id', '-c', type=str, default=None)
def update(name: str, commit_id: str) -> None:
    """Update information of one experiment. The exp_name should match at least
    one experiment. Currently supported information includes commit_id."""
    # first match the name
    info = get_project_info()
    if info is None:
        click.echo('Experiment project folder not initialized or corrupted.')
        return
    if name is None:
        name = click.prompt('name')
    exp_name = None
    for e in info['exps']:
        if re.search(name, e['name']) is not None:
            exp_name = e['name']
            exp_info = e
            break
    if exp_name is None:
        click.echo('Unable to find any experiment matching {0}. Exiting.'.format(name))
        return
    if commit_id is None:
        commit_id = click.prompt('commit_id for {}'.format(exp_name))
    old_id = exp_info.get('commit_id', None)
    exp_info['commit_id'] = commit_id
    with open(info['path'], 'w') as f:
        json.dump(info, f)
    click.echo('Updated commit_id {0} -> {1} for {2}.'.format(old_id, commit_id, exp_name))


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
