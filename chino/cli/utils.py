import os
import stat
from datetime import datetime

import click

from chino.io.fileio import create_text_file


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
        touch(filename, author, email, desc, True, True, executable, force)
    except Exception as e:
        click.echo('Cannot create file `{0}`, reason: {1}'.format(filename, e))


def touch(filename: str,
          author: str = None,
          email: str = None,
          desc: str = None,
          record_create_datetime: bool = False,
          create_dir: bool = False,
          executable: bool = False,
          force: bool = False):
    """
    Create a text file with given information.
    """
    headers = []
    if executable:
        _, ext = os.path.splitext(os.path.basename(filename))
        # NOTE: I only use python and bash, so adding more interpreters
        # is not my consideration.
        if ext == '.py':  # a python file, use python3 always, also add utf-8
            headers.append('#!/usr/bin/env python3')
            headers.append('# -*- coding: utf-8 -*-')
        elif ext == '.sh':
            # https://stackoverflow.com/a/10383546
            headers.append('#!/usr/bin/env bash')
    if author is not None:
        author_info = '# Author: {0}'.format(author)
        if email is not None:
            author_info += ' ({0})'.format(email)
        headers.append(author_info)
    if record_create_datetime:
        headers.append('# Date: {0}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    if desc is not None:
        headers.append('# Description: {0}'.format(desc))
    create_text_file(filename, headers, create_dir, force)
    if executable:
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IXUSR)
