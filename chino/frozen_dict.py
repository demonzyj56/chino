from addict import Dict


class FrozenDict(Dict):
    """FrozenDict extends addict.Dict in a similar way as AttrDict in
    Detectron.  When the dict is frozen, one can no longer access
    non-existent fields.  Moreover, the keys are `frozen` in the sense that
    no new keys can be added."""

    FROZEN = '__frozen__'

    def __init__(self, *args, **kwargs):
        super(FrozenDict, self).__init__(*args, **kwargs)
        self.__dict__[FrozenDict.FROZEN] = False

    def __missing__(self, name):
        """After freezing, raise error for missing fields."""
        if not self.__dict__[FrozenDict.FROZEN]:
            return super(FrozenDict, self).__missing__(name)
        else:
            raise AttributeError("Invalid key '{0}'".format(name))

    def __setitem__(self, name, value):
        """After freezing, disable setting values for invalid fields."""
        if not self.__dict__[FrozenDict.FROZEN]:
            super(FrozenDict, self).__setitem__(name, value)
        else:
            # Check whether name exists
            if name not in self:
                raise KeyError("Non-existent key: '{0}'".format(name))
            # Check whether the field is at end node
            elif isinstance(self[name], FrozenDict):
                raise KeyError("Unable to reset FrozenDict at "
                               "key '{0}'".format(name))
            else:
                super(FrozenDict, self).__setitem__(name, value)

    def is_frozen(self):
        """Check whether the current dict is frozen."""
        return self.__dict__[FrozenDict.FROZEN]

    def freeze(self, set_freeze=True):
        """Freeze (or change the state of freezing) of current dict."""
        self.__dict__[FrozenDict.FROZEN] = set_freeze
        for v in self.values():
            if isinstance(v, FrozenDict):
                v.freeze(set_freeze)


def to_plain_dict(frozen_dict, sep=None):
    """
    Converts an FrozenDict object to a `plain_dict`.
    The term `plain_dict` means that there is no nested dict inside the
    returned dict.  For nested field in input frozen_dict, the attributes
    are joined using a separator.  If `sep` is None, then the default
    separator is `__`.
    For example, cfg.svm.C=100.0 will be converted to
    cfg_plain['svm__C'] = 100.0.
    """
    assert isinstance(frozen_dict, FrozenDict)
    if sep is None:
        sep = '__'
    out = dict()
    for k, v in frozen_dict.items():
        if isinstance(v, FrozenDict):
            # recursively get the dict and join
            vdict = to_plain_dict(v, sep=sep)
            for kk, vv in vdict.items():
                out.update({sep.join([k, kk]): vv})
        else:
            out[k] = v

    return out


def from_plain_dict(plain_dict, sep=None):
    """Converts a converted plain_dict back to FrozenDict.
    If `sep` is None, then the default separator is `__`.
    """
    assert isinstance(plain_dict, dict)
    assert all([not isinstance(v, dict) for v in plain_dict.values()])
    if sep is None:
        sep = '__'
    frozen_dict = FrozenDict()
    for k, v in plain_dict.items():
        all_keys = k.split(sep)
        current = frozen_dict
        for ak in all_keys:
            if ak == all_keys[-1]:  # the last one
                current[ak] = v
            else:
                if not hasattr(current, ak):
                    current[ak] = FrozenDict()
                current = current[ak]

    return frozen_dict
