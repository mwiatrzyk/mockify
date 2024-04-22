# ---------------------------------------------------------------------------
# tests/unit/core/test_inspect.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify.api import Mock, MockInfo


class TestMockInfo:

    @pytest.fixture
    def target(self):
        return Mock("target")

    @pytest.fixture
    def uut(self, target):
        return MockInfo(target)

    def test_when_created_with_invalid_argument_then_raise_type_error(self):
        with pytest.raises(TypeError) as excinfo:
            MockInfo(123)
        assert str(excinfo.value) == "__init__() got an invalid value for argument 'target'"

    def test_calling_mock_property_issues_deprecation_warning_and_returns_target_mock(self, uut, target):
        with pytest.warns(DeprecationWarning) as rec:
            assert uut.mock is target
        assert len(rec) == 1
        (first,) = rec
        assert (
            str(first.message) == "'mockify.core.MockInfo.mock' is deprecated since version 0.8 "
            "and will be removed in next major release - please use 'mockify.core.MockInfo.target' instead."
        )
        assert first.filename == __file__

    def test_calling_target_returns_target_mock(self, uut, target):
        assert uut.target is target

    def test_calling_repr_returns_target_representation_wrapped_with_mock_info(self, uut, target):
        assert repr(uut) == "<mockify.core.MockInfo(target=<mockify.mock.Mock('target')>)>"

    def test_if_inspected_mock_has_no_parent_then_return_none_from_parent(self, uut):
        assert uut.parent is None

    def test_if_inspected_mock_has_parent_then_return_its_parent_wrapped_with_another_mock_info_object(self, target):
        target.foo.expect_call()
        parent = MockInfo(target.foo).parent
        assert isinstance(parent, MockInfo)
        assert parent.target is target

    def test_mock_info_name_returns_target_name(self, uut, target):
        assert uut.name == target.__m_name__

    def test_mock_info_fullname_returns_target_fullname(self, uut, target):
        assert uut.fullname == target.__m_fullname__

    def test_mock_info_session_return_target_session(self, uut, target):
        assert uut.session is target.__m_session__

    def test_expectations_method_is_calling_expectations_method_on_target_mock(self, uut, target):
        first = target.expect_call()
        second = target.expect_call()
        third = target.expect_call()
        assert list(uut.expectations()) == [first, second, third]

    def test_children_method_is_calling_children_method_on_target_mock(self, uut, target):
        target.foo.expect_call()
        target.bar.expect_call()
        children = list(uut.children())
        assert len(children) == 2
        first, second = children
        assert isinstance(first, MockInfo)
        assert isinstance(second, MockInfo)
        assert first.target is target.foo
        assert second.target is target.bar

    def test_walk_method_is_calling_walk_method_on_target_mock(self, uut, target):
        target.foo
        target.bar.baz
        children = list(uut.walk())
        assert len(children) == 4
        one, two, three, four = children
        assert one.target is target
        assert two.target is target.foo
        assert three.target is target.bar
        assert four.target is target.bar.baz
