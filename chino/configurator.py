"""Build configs, at ease.
We wish something like the cfg used in Detectron: the default values are stored
somewhere in config.py and manually specified parameters are parsed and merged
from a yaml file or command line to the global cfg.
Notice this module is not thread-safe.

Modified from:
    https://github.com/facebookresearch/Detectron/blob/master/detectron/core/config.py
"""
import argparse
import copy
import logging
import numbers
from ast import literal_eval
from collections import Iterable
import six
import numpy as np
import yaml
from .frozen_dict import FrozenDict

logger = logging.getLogger(__name__)
cfg = FrozenDict()  # for importing


def reset_cfg():
    """Clean up and reset the global cfg."""
    globals()['cfg'] = FrozenDict()


def merge_from_yml(file_name, to_cfg=None):
    """Merge from yaml file."""
    with open(file_name, 'rb') as f:
        d = yaml.load(f)
    if to_cfg is None:
        to_cfg = cfg
    assert isinstance(to_cfg, FrozenDict)
    _merge_dict_into_Dict(d, to_cfg)


def cfg_parser(to_cfg=None):
    """Returns a parser with options and default values specified from
    a cfg FrozenDict."""
    if to_cfg is None:
        to_cfg = cfg
    assert isinstance(to_cfg, FrozenDict)
    parser = argparse.ArgumentParser(description='CFG parser.')
    parser = _convert_Dict_to_parser(to_cfg, parser)
    return parser


def _convert_Dict_to_parser(D, parser, prefix=''):
    """Recursively traverse D and put entries into parser."""
    for k, v in D.items():
        arg_name = '--' + prefix + k
        if isinstance(v, FrozenDict):
            parser = _convert_Dict_to_parser(v, parser, k + '.')
        elif isinstance(v, six.string_types):
            parser.add_argument(arg_name, type=str, default=v)
        elif isinstance(v, np.ndarray):
            # NOTE: only 1d array for numpy parser is supported.
            parser.add_argument(arg_name, action=_StoreAsNumpyArray,
                                nargs=v.numel(), type=v.dtype, default=v)
        elif isinstance(v, bool):
            # We don't use store_true/store_false. Always specify True/False.
            parser.add_argument(arg_name, type=_str2bool, default=v)
        elif isinstance(v, numbers.Real):
            parser.add_argument(arg_name, type=type(v), default=v)
        elif isinstance(v, Iterable):
            # Enforce list/tuple to have same length
            parser.add_argument(arg_name, type=type(v[0]), nargs=len(v),
                                default=v)
        else:
            # For types not covered by above, simply setup as the same type.
            parser.add_argument(arg_name, type=type(v), default=v)
    return parser


def _str2bool(v):
    """Parser type utility function."""
    if v.lower() in ('yes', 'true', 't', 'y', 'on', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', 'off', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean type expected. '
                                         'Received {}'.format(v))


class _StoreAsNumpyArray(argparse._StoreAction):
    """Parse the input array as a numpy array."""
    def __call__(self, parser, namespace, values, option_string=None):
        values = np.asarray(values)
        return super(_StoreAsNumpyArray, self).__call__(parser, namespace,
                                                        values, option_string)


def _merge_dict_into_Dict(d, D, stack=None):
    """Merge python dict d to entries in D."""
    assert isinstance(d, dict)
    assert isinstance(D, FrozenDict)

    for k, v_ in d.items():
        full_key = '.'.join(stack) + '.' + k if stack is not None else k
        if k not in D:
            raise KeyError('Non-existent config key: {}'.format(full_key))

        v = copy.deepcopy(v_)

        # do merging
        if isinstance(v, dict):
            stack_push = [k] if stack is None else stack + [k]
            _merge_dict_into_Dict(v, D[k], stack=stack_push)
        else:
            v = _decode_value(v)
            D[k] = _coerce_value(v, D[k], full_key)


def _decode_value(v):
    """Decodes a config value into a python object."""
    if not isinstance(v, six.string_types):
        return v
    try:
        v = literal_eval(v)
    except ValueError:
        pass
    except SyntaxError:
        pass
    return v


def _coerce_value(value_a, value_b, full_key):
    """Coerce value_a to value_b with possible type conversion."""
    type_a, type_b = type(value_a), type(value_b)
    if type_a == type_b:
        return value_a

    # Exceptions
    if isinstance(value_b, np.ndarray):
        value_a = np.asarray(value_a, dtype=value_b.dtype)
    elif isinstance(value_b, six.string_types) and not isinstance(value_a, Iterable):
        value_a = str(value_a)
    elif isinstance(value_b, tuple) and isinstance(value_a, Iterable):
        value_a = tuple(value_a)
    elif isinstance(value_b, list) and isinstance(value_a, Iterable):
        value_a = list(value_a)
    # converting from integers to floats should be mostly allowed
    elif isinstance(value_b, float) and isinstance(value_a, numbers.Integral):
        value_a = float(value_a)
    else:
        raise ValueError(
            'Type mismatch ({} vs. {}) with values ({} vs. {}) for '
            'key {}'.format(type_a, type_b, value_a, value_b, full_key)
        )
    return value_a
