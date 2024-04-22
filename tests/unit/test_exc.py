# ---------------------------------------------------------------------------
# tests/unit/test_exc.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

import pytest

from mockify import _utils, exc
from mockify.actions import Return
from mockify.core import Call, Expectation

ErrorMessageBuilder = _utils.ErrorMessageBuilder


class TestUnexpectedCall:

    def make_expected_message(self, actual_call, expected_calls):
        builder = ErrorMessageBuilder()
        builder.append_line("No matching expectations found for call:")
        builder.append_line("")
        builder.append_location(actual_call.location)
        builder.append_line("Called:")
        builder.append_line("  {}", actual_call)
        builder.append_line("Expected (any of):")
        for call in expected_calls:
            builder.append_line("  {}", call)
        return builder.build()

    @pytest.mark.parametrize(
        "actual_call, expected_calls",
        [(Call("foo", 1, 2, c=3), [Call("foo")]), (Call("foo", 1, 2, c=3), [Call("foo"), Call("foo", 1, 2, 3)])],
    )
    def test_string_representation(self, actual_call, expected_calls):
        uut = exc.UnexpectedCall(actual_call, expected_calls)
        assert uut.actual_call == actual_call
        assert uut.expected_calls == expected_calls
        assert str(uut) == self.make_expected_message(actual_call, expected_calls)


class TestUnexpectedCallOrder:

    def make_expected_message(self, actual_call, expected_call):
        builder = ErrorMessageBuilder()
        builder.append_line("Another mock is expected to be called:")
        builder.append_line("")
        builder.append_location(actual_call.location)
        builder.append_line("Called:")
        builder.append_line("  {}", actual_call)
        builder.append_line("Expected:")
        builder.append_line("  {}", expected_call)
        return builder.build()

    @pytest.mark.parametrize(
        "actual_call, expected_call",
        [(Call("foo", 1, 2, c=3), Call("foo")), (Call("foo", 1, 2, c=3), Call("foo", 1, 2, 3))],
    )
    def test_string_representation(self, actual_call, expected_call):
        uut = exc.UnexpectedCallOrder(actual_call, expected_call)
        assert uut.actual_call == actual_call
        assert uut.expected_call == expected_call
        assert str(uut) == self.make_expected_message(actual_call, expected_call)


class TestUninterestedCall:

    def make_expected_message(self, actual_call):
        builder = ErrorMessageBuilder()
        builder.append_line("No expectations recorded for mock:")
        builder.append_line("")
        builder.append_location(actual_call.location)
        builder.append_line("Called:")
        builder.append_line("  {}", actual_call)
        return builder.build()

    @pytest.mark.parametrize(
        "actual_call",
        [
            Call("foo", 1, 2),
            Call("bar", 1, 2, c=3),
        ],
    )
    def test_string_representation(self, actual_call):
        uut = exc.UninterestedCall(actual_call)
        assert uut.actual_call == actual_call
        assert str(uut) == self.make_expected_message(actual_call)


class TestOversaturatedCall:

    def make_expected_message(self, actual_call, oversaturated_expectation):
        builder = ErrorMessageBuilder()
        builder.append_line("Following expectation was oversaturated:")
        builder.append_line("")
        builder.append_location(oversaturated_expectation.expected_call.location)
        builder.append_line("Pattern:")
        builder.append_line("  {}", oversaturated_expectation.expected_call)
        builder.append_line("Expected:")
        builder.append_line("  {}", oversaturated_expectation.expected_call_count)
        builder.append_line("Actual:")
        builder.append_line("  oversaturated by {} at {} (no more actions)", actual_call, actual_call.location)
        return builder.build()

    @pytest.mark.parametrize(
        "actual_call, oversaturated_expectation",
        [(Call("foo"), Expectation(Call("foo"))), (Call("foo", 1, 2, 3), Expectation(Call("foo", 1, 2, 3)))],
    )
    def test_string_representation(self, actual_call, oversaturated_expectation):
        uut = exc.OversaturatedCall(actual_call, oversaturated_expectation)
        assert uut.actual_call == actual_call
        assert uut.oversaturated_expectation == oversaturated_expectation
        assert str(uut) == self.make_expected_message(actual_call, oversaturated_expectation)


class TestUnsatisfied:
    _expectation_with_action = Expectation(Call("bar", 1, 2))
    _expectation_with_action.will_once(Return(123))

    def make_expected_message(self, unsatisfied_expectations):
        builder = ErrorMessageBuilder()
        self.__append_title(builder, unsatisfied_expectations)
        for expectation in unsatisfied_expectations:
            self.__append_expectation(builder, expectation)
        return builder.build()

    def __append_title(self, builder, unsatisfied_expectations):
        if len(unsatisfied_expectations) > 1:
            builder.append_line("Following {} expectations are not satisfied:", len(unsatisfied_expectations))
        else:
            builder.append_line("Following expectation is not satisfied:")

    def __append_expectation(self, builder, expectation):
        builder.append_line("")
        builder.append_location(expectation.expected_call.location)
        builder.append_line("Pattern:")
        builder.append_line("  {}", expectation.expected_call)
        self.__append_action(builder, expectation)
        builder.append_line("Expected:")
        builder.append_line("  {}", expectation.expected_call_count)
        builder.append_line("Actual:")
        builder.append_line("  {}", expectation.actual_call_count)

    def __append_action(self, builder, expectation):
        action = str(expectation.action) if expectation.action is not None else None
        if action is not None:
            builder.append_line("Action:")
            builder.append_line("  {}", action)

    @pytest.mark.parametrize(
        "unsatisfied_expectations",
        [
            [Expectation(Call("foo"))],
            [Expectation(Call("foo")), Expectation(Call("bar", 1, 2))],
            [Expectation(Call("foo")), _expectation_with_action],
        ],
    )
    def test_string_representation(self, unsatisfied_expectations):
        uut = exc.Unsatisfied(unsatisfied_expectations)
        assert uut.unsatisfied_expectations == unsatisfied_expectations
        assert str(uut) == self.make_expected_message(unsatisfied_expectations)
