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
            return super().__missing__(name)
        else:
            raise AttributeError("Invalid key '{0}'".format(name))

    def __setitem__(self, name, value):
        """After freezing, disable setting values for invalid fields."""
        if not self.__dict__[FrozenDict.FROZEN]:
            super().__setitem__(name, value)
        else:
            # Check whether name exists
            if name not in self:
                raise KeyError("Non-existent key: '{0}'".format(name))
            # Check whether the field is at end node
            elif isinstance(self[name], FrozenDict):
                raise KeyError("Unable to reset FrozenDict at "
                               "key '{0}'".format(name))
            else:
                super().__setitem__(name, value)

    def is_frozen(self):
        """Check whether the current dict is frozen."""
        return self.__dict__[FrozenDict.FROZEN]

    def freeze(self, set_freeze=True):
        """Freeze (or change the state of freezing) of current dict."""
        self.__dict__[FrozenDict.FROZEN] = set_freeze
        for v in self.values():
            if isinstance(v, FrozenDict):
                v.freeze(set_freeze)
