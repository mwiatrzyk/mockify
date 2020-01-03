# ---------------------------------------------------------------------------
# tests/unit/_test_exc.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

from mockify import exc, Call


class ExpectationStub:

    def __init__(self, call, location):
        self.expected_call = call
        self.location = location

    def format_action(self):
        return

    def format_location(self):
        return self.location


class TestUninterestedCall:

    def test_string_representation(self):
        call = Call('foo', 1, 2, c=3)
        uut = exc.UninterestedCall(call)
        assert uut.call is call
        assert str(uut) == 'foo(1, 2, c=3)'


class TestOversaturatedCall:

    def test_string_representation(self):
        call = Call('foo', 1, 2, c=3)
        expectation = ExpectationStub(call, 'foo.py:123')
        uut = exc.OversaturatedCall(expectation, call)
        assert uut.call is call
        assert uut.expectation is expectation
        assert str(uut) == 'at foo.py:123: foo(1, 2, c=3): no more actions recorded for call: foo(1, 2, c=3)'


class TestUnsatisfied:

    def test_string_representation_of_single_unsatisfied_expectation(self):
        call = Call('foo')
        expectation = ExpectationStub(call, 'foo.py:123')
        expectation.format_expected = lambda: "to be called twice"
        expectation.format_actual = lambda: "called once"
        uut = exc.Unsatisfied([expectation])
        assert len(uut.expectations) == 1
        assert uut.expectations[0] is expectation
        assert str(uut) ==\
            'following expectation is not satisfied:\n\n'\
            'at foo.py:123\n'\
            '-------------\n'\
            '    Pattern: foo()\n'\
            '   Expected: to be called twice\n'\
            '     Actual: called once'

    def test_string_representation_of_two_unsatisfied_expectations(self):
        first_call = Call('foo')
        second_call = Call('bar')
        first = ExpectationStub(first_call, 'foo.py:123')
        first.format_expected = lambda: "to be called twice"
        first.format_actual = lambda: "called once"
        second = ExpectationStub(second_call, 'bar.py:456')
        second.format_expected = lambda: "to be called once"
        second.format_actual = lambda: "never called"
        uut = exc.Unsatisfied([first, second])
        assert len(uut.expectations) == 2
        assert uut.expectations[0] is first
        assert uut.expectations[1] is second
        assert str(uut) ==\
            'following 2 expectations are not satisfied:\n\n'\
            'at foo.py:123\n'\
            '-------------\n'\
            '    Pattern: foo()\n'\
            '   Expected: to be called twice\n'\
            '     Actual: called once\n\n'\
            'at bar.py:456\n'\
            '-------------\n'\
            '    Pattern: bar()\n'\
            '   Expected: to be called once\n'\
            '     Actual: never called'
