"""Utilities for parsing lines."""
from typing import Sequence


def read_lines(filename: str) -> Sequence[str]:
    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]
        return lines
