import itertools


class Call:
    """Container that binds mock function name with args, kwargs, file name and
    line number.

    Objects of this class are created when mock is called or when expectation
    is recorded on the mock. Later, these two instances are compared between to
    find a match.

    :param name:
        Mock's name

    :param filename:
        File name where mock call (or expectation) is located

    :param lineno:
        Line number in file where mock call (or expectation) is located
    """

    def __init__(self, name, filename=None, lineno=None, args=None, kwargs=None):
        self._name = name
        self._args = args or tuple()
        self._kwargs = kwargs or {}
        self._filename = filename
        self._lineno = lineno

    def __str__(self):
        args_gen = (repr(x) for x in self._args)
        kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted(self._kwargs.items()))
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return "{}({})".format(self._name, ", ".join(all_gen))

    def __eq__(self, other):
        return self._name == other._name and\
            self._args == other._args and\
            self._kwargs == other._kwargs

    @property
    def name(self):
        """Mock function name."""
        return self._name

    @property
    def args(self):
        """Mock function args."""
        return self._args

    @property
    def kwargs(self):
        """Mock function keyword args."""
        return self._kwargs

    @property
    def filename(self):
        """Name of file where mock was called or where expectation was
        registered."""
        return self._filename

    @property
    def lineno(self):
        """Line number inside file name given by :attr:`filename`."""
        return self._lineno

    def bind(self, *args, **kwargs):
        """Assigns ``args`` and ``kwargs`` to this call object.

        This is made as separate method for ease of use. When this method is
        not called, call represents mock call with no args.
        """
        self._args = args
        self._kwargs = kwargs
        return self
