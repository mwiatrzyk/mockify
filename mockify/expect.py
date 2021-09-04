# ---------------------------------------------------------------------------
# mockify/expect.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
from .abc import IExpectation, IMock


def expect_call(
    __mock__: IMock,
    *args,
    **kwargs
) -> IExpectation:
    """Function used to record *call* expectation on given mock.

    :param __mock__:
        Mock object to record expectation on

    :param __attr__:
        Optional mock object attribute.

        When given, and supported by ``__mock__``, then expectation will be
        recorded on a given mock attribute (or nested attribute) instead of a
        given root mock object. If not given, then ``__mock__`` will simply be
        treated as a function mock.

    :param ``*args``:
        Positional args the mock is expected to be called with

    :param ``**kwargs``:
        Named args the mock is expected to be called with
    """
    return __mock__.expect_call(*args, **kwargs)
