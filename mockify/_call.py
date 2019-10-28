import os
import keyword
import itertools
import traceback

_mockify_root_dir = os.path.dirname(__file__)


class Call:
    """An object representing mock call.

    Instances of this class are created when expectations are recorded or
    when mock is called. The role of this class is to keep mock name and its
    call params as a single object for easier comparison between expected and
    actual mock calls.

    This class also provides some basic stack info to be used for error
    reporting (f.e. to display where failed expectation was defined).
    """

    def __init__(self, *args, **kwargs):
        if not args:
            raise TypeError("__init__() missing 1 required positional argument: 'name'")
        self._name = args[0]
        self._args = args[1:]
        self._kwargs = kwargs
        self._location = self.__extract_fileinfo_from_traceback()
        self.__validate_name()

    def __extract_fileinfo_from_traceback(self):
        stack = traceback.extract_stack()
        for frame in reversed(stack):
            if not frame.filename.startswith(_mockify_root_dir) and\
               not frame.filename.startswith('/usr/lib'):  # TODO: make this better
                return frame.filename, frame.lineno

    def __validate_name(self):
        parts = self._name.split('.') if isinstance(self._name, str) else [self._name]
        for part in parts:
            if not self.__is_identifier(part):
                raise exc.InvalidMockName(invalid_name=self._name)

    def __is_identifier(self, name):
        return isinstance(name, str) and\
            name.isidentifier() and\
            not keyword.iskeyword(name)

    def __str__(self):
        return f"{self._name}({self._format_params(*self._args, **self._kwargs)})"

    def __repr__(self):
        return f"<mockify.{self.__class__.__name__}({self._format_params(self._name, *self._args, **self._kwargs)})>"

    def __eq__(self, other):
        return self._name == other._name and\
            self._args == other._args and\
            self._kwargs == other._kwargs

    def __ne__(self, other):
        return not self.__eq__(other)

    def _format_params(self, *args, **kwargs):
        args_gen = (repr(x) for x in args)
        kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted(kwargs.items()))
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return ', '.join(all_gen)

    @property
    def name(self):
        """Mock name."""
        return self._name

    @property
    def args(self):
        """Mock positional args."""
        return self._args

    @property
    def kwargs(self):
        """Mock named args."""
        return self._kwargs

    @property
    def location(self):
        """Location (a tuple containing file name and line number) where this
        call object was created.

        .. versionadded:: 1.0

        This is used to display where failed expectation was declared or
        where failed call was orinally made.
        """
        return self._location
