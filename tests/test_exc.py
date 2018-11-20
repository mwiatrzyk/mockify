# ---------------------------------------------------------------------------
# tests/test_exc.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

from mockify import exc, Call, Expectation
from mockify.actions import Return


class TestUninterestedCall:

    def test_str(self):
        uut = exc.UninterestedCall(Call('foo', 'foo.py', 123))
        assert str(uut) == 'at foo.py:123: foo()'


class TestUnsatisfiedAssertion:

    def test_str_of_exception_with_one_unsatisfied_expectation(self):
        first = Expectation(Call('foo', filename='foo.py', lineno=1))
        uut = exc.UnsatisfiedAssertion([first])
        assert str(uut) ==\
            "Following expectations have failed:\n\n"\
            "#1 at foo.py:1\n"\
            "--------------\n"\
            "      Mock: foo()\n"\
            "  Expected: to be called once\n"\
            "    Actual: never called"

    def test_str_of_exception_with_one_unsatisfied_expectation_with_action(self):
        first = Expectation(Call('foo', filename='foo.py', lineno=1))
        first.will_once(Return(123))
        uut = exc.UnsatisfiedAssertion([first])
        assert str(uut) ==\
            "Following expectations have failed:\n\n"\
            "#1 at foo.py:1\n"\
            "--------------\n"\
            "      Mock: foo()\n"\
            "    Action: Return(123)\n"\
            "  Expected: to be called once\n"\
            "    Actual: never called"

    def test_str_of_exception_with_two_unsatisfied_expectation(self):
        first = Expectation(Call('foo', filename='foo.py', lineno=1))
        second = Expectation(Call('spam', filename='spam.py', lineno=1))
        uut = exc.UnsatisfiedAssertion([first, second])
        assert str(uut) ==\
            "Following expectations have failed:\n\n"\
            "#1 at foo.py:1\n"\
            "--------------\n"\
            "      Mock: foo()\n"\
            "  Expected: to be called once\n"\
            "    Actual: never called\n\n"\
            "#2 at spam.py:1\n"\
            "---------------\n"\
            "      Mock: spam()\n"\
            "  Expected: to be called once\n"\
            "    Actual: never called"
