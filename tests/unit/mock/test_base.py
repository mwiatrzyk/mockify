# ---------------------------------------------------------------------------
# tests/unit/mock/test_base.py
#
# Copyright (C) 2019 - 2024 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

from mockify.mock import BaseMock


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
        assert repr(StubMock("dummy")) == "<tests.unit.mock.test_base.StubMock('dummy')>"
