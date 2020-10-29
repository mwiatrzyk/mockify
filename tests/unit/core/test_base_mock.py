# ---------------------------------------------------------------------------
# tests/unit/mock/test_base.py
#
# Copyright (C) 2018 - 2020 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify.core import BaseMock, MockInfo


class StubMock(BaseMock):

    def __init__(self, name, session=None, parent=None):
        super().__init__(name, session=session, parent=parent)
        self._children = []
        self._expectations = []
        if parent is not None:
            parent._children.append(self)

    def set_expectations(self, *expectations):
        self._expectations.extend(expectations)

    def __m_children__(self):
        yield from self._children

    def __m_expectations__(self):
        yield from self._expectations


class TestBaseMock:

    def test_mock_repr(self):
        assert repr(
            StubMock('dummy')
        ) == "<tests.unit.core.test_base_mock.StubMock('dummy')>"


class TestMockInfo:
    _dummy_session = 'session'

    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock = StubMock('mock', session=self._dummy_session)

    def test_cannot_set_both_session_and_parent(self):
        with pytest.raises(TypeError) as excinfo:
            StubMock('mock', session=self._dummy_session, parent=self.mock)

    def test_mock_info_repr(self):
        assert repr(
            MockInfo(self.mock)
        ) == "<mockify.core._base_mock.MockInfo: <tests.unit.core.test_base_mock.StubMock('mock')>>"

    def test_if_invalid_object_type_given__then_fail_with_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            MockInfo(123)
        assert str(
            excinfo.value
        ) == "__init__() got an invalid value for argument 'target'"

    def test_target_is_the_same_as_given_mock(self):
        assert MockInfo(self.mock).target is self.mock

    def test_obtain_mock_name(self):
        assert MockInfo(self.mock).name == 'mock'

    def test_obtain_mock_fullname(self):
        assert MockInfo(self.mock).fullname == 'mock'

    def test_obtain_mock_fullname_for_mock_having_parent(self):
        child = StubMock('child', parent=self.mock)
        assert MockInfo(child).fullname == 'mock.child'

    def test_obtain_mock_session(self):
        assert MockInfo(self.mock).session is self._dummy_session

    def test_obtain_expectations_from_target_mock(self):
        self.mock.set_expectations('one', 'two', 'three')
        assert list(MockInfo(self.mock).expectations()
                    ) == ['one', 'two', 'three']

    def test_obtain_direct_children_of_target_mock(self):
        first = StubMock('first', parent=self.mock)
        second = StubMock('second', parent=self.mock)
        assert [x.target
                for x in MockInfo(self.mock).children()] == [first, second]

    def test_walk_generates_all_mock_children(self):
        child = StubMock('child', parent=self.mock)
        grandchild = StubMock('grandchild', parent=child)
        grandgrandchild = StubMock('grandgrandchild', parent=grandchild)
        assert [x.target for x in MockInfo(self.mock).walk()
                ] == [self.mock, child, grandchild, grandgrandchild]
