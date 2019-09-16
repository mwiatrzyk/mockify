# ---------------------------------------------------------------------------
# tests/test_actions.py
#
# Copyright (C) 2018 - 2019 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from _mockify.actions import Return, Raise, Invoke


class TestReturn:

    def setup_method(self):
        self.uut = Return(123)

    ### Tests

    def test_string_representation(self):
        assert str(self.uut) == 'Return(123)'

    def test_when_called_without_args__then_return_given_value(self):
        assert self.uut() == 123

    def test_when_called_with_positional_and_named_args__then_return_given_value(self):
        assert self.uut(1, 2, c=3) == 123


class TestRaise:

    def setup_method(self):
        self.exc = Exception('an error')
        self.uut = Raise(self.exc)

    ### Tests

    @pytest.mark.skip('This test may fail depending on Python version - to be skipped for now')
    def test_string_representation(self):
        assert str(self.uut) == "Raise(Exception('an error'))"

    def test_when_called_without_args__then_raise_given_exception(self):
        with pytest.raises(Exception) as excinfo:
            self.uut()
        assert excinfo.value is self.exc

    def test_when_called_with_args_and_kwargs__then_raise_given_exception(self):
        with pytest.raises(Exception) as excinfo:
            self.uut(1, 2, c=3)
        assert excinfo.value is self.exc


class TestInvoke:

    def setup_method(self):

        def func(*args, **kwargs):
            self.called_with.append((args, kwargs))
            return self.return_value

        self.func = func
        self.uut = Invoke(self.func)
        self.called_with = []
        self.return_value = 123

    ### Tests

    def test_string_representation(self):
        assert str(self.uut) == "Invoke(<function func>)"

    def test_when_called_without_params__then_trigger_func_without_params(self):
        assert self.uut() == self.return_value
        assert self.called_with == [(tuple(), {})]

    def test_when_called_with_args_and_kwargs__then_trigger_func_with_same_args_and_kwargs(self):
        assert self.uut(1, 2, c=3) == self.return_value
        assert self.called_with == [((1, 2), {'c': 3})]
