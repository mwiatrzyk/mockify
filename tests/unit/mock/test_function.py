# ---------------------------------------------------------------------------
# tests/unit/mock/test_function.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify import exc
from mockify.core import Session, assert_satisfied, satisfied
from mockify.actions import Return
from mockify.mock import FunctionMock


class TestFunctionMock:
    _valid_names = ['foo', 'bar', 'foo.bar', 'foo.bar.baz']

    @pytest.mark.parametrize(
        'invalid_name', [
            '123',
            [],
            '@#$',
            '123foo',
            'foo..bar',
        ]
    )
    def test_cannot_create_function_mock_with_invalid_name(self, invalid_name):
        with pytest.raises(TypeError) as excinfo:
            FunctionMock(invalid_name)
        assert str(
            excinfo.value
        ) == "Mock name must be a valid Python identifier, got {!r} instead".format(
            invalid_name
        )

    @pytest.mark.parametrize('name', _valid_names)
    def test_get_mock_name(self, name):
        assert FunctionMock(name).__m_name__ == name

    @pytest.mark.parametrize('name', _valid_names)
    def test_get_mock_full_name(self, name):
        assert FunctionMock(name).__m_fullname__ == name

    def test_get_mock_session(self):
        session = Session()
        assert FunctionMock('foo', session=session).__m_session__ is session

    def test_function_mocks_have_no_children(self):
        assert list(FunctionMock('foo').__m_children__()) == []

    def test_list_of_expectations_does_only_contain_expectations_recorded_for_that_mock(
        self
    ):
        session = Session()
        first = FunctionMock('first', session=session)
        one = first.expect_call()
        second = FunctionMock('second', session=session)
        two = second.expect_call()
        three = second.expect_call()
        assert set(first.__m_expectations__()) == set([one])
        assert set(second.__m_expectations__()) == set([two, three])

    @pytest.mark.parametrize(
        'args, kwargs', [
            [tuple(), {}],
            [(1, 2), {}],
            [(1, 2, 3), {
                'a': 4,
                'b': 5
            }],
            [tuple(), {
                'a': 1,
                'b': 2
            }],
        ]
    )
    def test_record_call_expectation_and_check_if_satisfied(self, args, kwargs):
        mock = FunctionMock('foo')
        mock.expect_call(*args, **kwargs).will_once(Return(123))
        with satisfied(mock):
            assert mock(*args, **kwargs) == 123

    def test_when_expectation_is_not_consumed__then_unsatisfied_error_is_raised(
        self
    ):
        mock = FunctionMock('foo')
        one = mock.expect_call()
        mock.expect_call(1, 2)
        mock(1, 2)
        with pytest.raises(exc.Unsatisfied) as excinfo:
            assert_satisfied(mock)
        assert excinfo.value.unsatisfied_expectations == [one]
