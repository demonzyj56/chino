"""IO for reading and writing files."""
import os
from typing import Sequence

from chino.io.lineio import read_lines


def create_text_file(filename: str,
                     lines: Sequence[str] = None,
                     create_dir: bool = False,
                     force: bool = False,
                     mode: int = 0o664) -> None:
    """
    Create a text file with filename. If lines are not None, then also write
    contents into the file.
    """
    if not force and os.path.exists(filename):
        raise FileExistsError('{0} already exists.'.format(filename))
    dirname = os.path.dirname(filename)
    if create_dir and len(dirname) > 0 and not os.path.isdir(dirname):
        os.makedirs(dirname)
    with open(filename, 'w', encoding='utf-8') as f:
        if lines is not None:
            for line in lines:
                f.write(line.strip() + '\n')
    os.chmod(filename, mode)


def load(filename: str, **kwargs):
    """Universal load function, depending on the filetype of filename.
    The kwargs are dispatched to corresponding loader."""
    if not os.path.isfile(filename):
        raise FileNotFoundError('{0} does not exist.'.format(filename))
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext == '.json':
        import json
        with open(filename, 'r') as f:
            data = json.load(f)
    elif ext in ('.yml', '.yaml'):
        import yaml
        with open(filename, 'r') as f:
            data = yaml.load(f)
    elif ext in ('.jpg', '.jpeg', '.png'):
        import cv2
        data = cv2.imread(filename)
    elif ext == '.list':
        data = read_lines(filename)
    elif ext == '.tsv':
        if 'as_plain_text' in kwargs:
            as_plain_text = kwargs.pop('as_plain_text')
        else:
            as_plain_text = False
        if as_plain_text:
            lines = read_lines(filename)
            data = [line.split('\t') for line in lines]
        else:
            import pandas as pd
            defaults = {'sep': '\t', 'header': None}
            defaults.update(kwargs)
            data = pd.read_csv(filename, **defaults)
    return data

