"""A simple timer for timing."""
import logging
import time
from collections import Iterable
from six import string_types

logger = logging.getLogger(__name__)


class TicTocTimer(object):
    """The simplest timer."""

    def __init__(self, log_template=None):
        self.timing = False
        self.start = None
        if log_template is None:
            self.log_template = 'Elapsed time is {:.3f}s.'
        else:
            self.log_template = log_template

    def tic(self):
        """Begin timing."""
        self.timing = True
        self.start = time.time()

    def toc(self):
        """Return elapsed time."""
        if not self.timing:
            return 0.
        return time.time() - self.start

    def __enter__(self):
        self.tic()
        return self

    def __exit__(self, exc_type, exc_value, trackback):
        """When using the context manager, the elapsed time is explicitly
        logged to logger."""
        logger.info(self.log_template.format(self.toc()))


class Timer(TicTocTimer):
    """Timer that supports recording multiple time slots."""

    def __init__(self, log_template=None):
        super(Timer, self).__init__(log_template)
        self.total = 0.
        self.current = 0.
        self.count = 0

    def toc(self, mode='elapsed'):
        """Support multiple modes for timing.
        - `elapsed`:
            Measure the elapsed time since last tic.  Same as TicTocTimer.
            The timer is not stopped.
        - `cumulative`:
            Measure the cumulative time for multiple time slots.  The timer
            is stopped and should be restarted by next tic.
        - `average`:
            Same as `cumulative`, except that average time of all time slots
            are returned instead of total cumulative time.
            The timer is stopped and should be restarted by next tic.
        """
        if not self.timing:
            return self.current
        self.current = time.time() - self.start
        if mode == 'elapsed':
            return self.current
        elif mode == 'cumulative':
            self.total += self.current
            self.count += 1
            self.timing = False
            return self.total
        elif mode == 'avarage':
            self.total += self.current
            self.count += 1
            self.timing = False
            return self.total / self.count
        else:
            raise KeyError('Unknown timer mode: {}'.format(mode))


__GT = {}  # a dict holding global timers


def tic(name='default'):
    """Global timer starts.  Support a list of timer names."""
    if isinstance(name, string_types):
        name = [name]
    elif isinstance(name, Iterable):
        assert all([isinstance(n, string_types) for n in name])
    else:
        raise KeyError('Invalid name or list of names: {}'.format(name))
    for n in name:
        if n not in __GT:
            __GT.update({n: TicTocTimer()})
        __GT[n].tic()


def toc(name='default'):
    """Global timer returns elapsed time."""
    if name in __GT:
        return __GT[name].toc()
    else:
        raise KeyError('Timer {} has not been initialized'.format(name))
