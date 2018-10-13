import traceback
import itertools

from .expectation import Expectation


class MockCall:

    def __init__(self, name, args, kwargs):
        self._name = name
        self._args = args
        self._kwargs = kwargs

    def __str__(self):
        args_gen = (repr(x) for x in self._args)
        kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted(self._kwargs.items()))
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return "{}({})".format(self._name, ", ".join(all_gen))

    def __eq__(self, other):
        return self._name == other._name and\
            self._args == other._args and\
            self._kwargs == other._kwargs


class Mock:

    def __init__(self, ctx, name):
        self._ctx = ctx
        self._name = name

    def __call__(self, *args, **kwargs):
        return self._ctx(self._name, args, kwargs)

    def expect_call(self, *args, **kwargs):
        stack = traceback.extract_stack()
        frame_summary = stack[-2]
        filename = frame_summary.filename
        lineno = frame_summary.lineno
        return self._ctx.expect_call(self._name, args, kwargs, filename, lineno)
