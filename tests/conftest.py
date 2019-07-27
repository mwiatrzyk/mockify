import functools
import collections

import pytest

from mockify import _utils, Call, Registry


@pytest.fixture
def ctx():
    ctx = Registry()
    yield ctx
    ctx.assert_satisfied()


@pytest.fixture
def context_mock(ctx):

    def mock_method(obj, name):

        def invoke(self, __func_name__, *args, **kwargs):
            call = Call('ctx.' + __func_name__, args or None, kwargs or None)
            return ctx(call)

        def expect_call(__func_name__, *args, **kwargs):
            call = Call('ctx.' + __func_name__, args or None, kwargs or None)
            filename, lineno = _utils.extract_filename_and_lineno_from_stack(-1)
            return ctx.expect_call(call, filename, lineno)

        invoke = functools.partial(invoke, obj, name)
        expect_call = functools.partial(expect_call, name)

        setattr(invoke, 'expect_call', expect_call)
        setattr(obj.__class__, name, invoke)

    class Context:
        pass

    context = Context()
    mock_method(context, '__call__')
    mock_method(context, 'expect_call')
    mock_method(context, 'assert_satisfied')
    return context
