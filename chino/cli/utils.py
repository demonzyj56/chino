import os
import stat
from datetime import datetime

import click


@click.command(name='touch')
@click.argument('filename')
@click.option('--author', '-a', default='Yijie Zeng', help='Author of the file.')
@click.option('--email', '-e', default='yijie.zeng@outlook.com',
              help='Email of the author.')
@click.option('--desc', '-d', default=None, help='Descriptions of the file.')
@click.option('--exec/--no-exec', 'executable', default=False,
              help='If specify, then the script is executable. Only applies to py/sh file.')
@click.option('--force/--no-force', default=False,
              help='If specify, then force creating the script regardless of whether it exists.')
def touch_cli(filename, author, email, desc, executable, force):
    """Create a text file with given information."""
    try:
        touch(filename, author, email, desc, True, executable, force)
    except FileExistsError as e:
        click.echo(e)


def touch(filename: str,
          author: str = None,
          email: str = None,
          desc: str = None,
          create_dir: bool = False,
          executable: bool = False,
          force: bool = False):
    """
    Create a text file with given information.

    :param force: If True, then force creating the file regardless whether
        it exists or not.
    :param desc: Description for the text file.
    :param executable: If True, the text file is regarded as an executable
        script. In this case, a shebang is added.
    :param create_dir: If True, then create the directory for filename.
    :param email: Email information (default: yijie.zeng@outlook.com).
    :param filename: Full path of the text file.
    :param author: Author of the file (default: Yijie Zeng).
    :return:
    """
    if not force and os.path.exists(filename):
        raise FileExistsError('{0} already exists.'.format(filename))
    dirname = os.path.dirname(filename)
    if create_dir and len(dirname) > 0 and not os.path.isdir(dirname):
        os.makedirs(dirname)
    if author is None:
        author = 'Yijie Zeng'
    if email is None:
        email = 'yijie.zeng@outlook.com'
    headers = [
        '# Author: {0} ({1})'.format(author, email),
        '# Date: {0}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    ]
    if desc is not None:
        headers.append('# Description: {0}'.format(desc))
    if executable:
        _, ext = os.path.splitext(os.path.basename(filename))
        # NOTE: I only use python and bash, so adding more interpreters
        # is not my consideration.
        if ext == '.py':  # a python file, use python3 always, also add utf-8
            headers.insert(0, '#!/usr/bin/env python3')
            headers.insert(1, '# -*- coding: utf-8 -*-')
        elif ext == '.sh':
            # https://stackoverflow.com/a/10383546
            headers.insert(0, '#!/usr/bin/env bash')
    with open(filename, 'w', encoding='utf-8') as f:
        for line in headers:
            f.write(line + '\n')
    if executable:
        os.chmod(filename, stat.S_IXUSR)
