# ---------------------------------------------------------------------------
# tests/unit/mock/test_factory.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
import pytest

from mockify.core import MockInfo
from mockify.mock import MockFactory


class TestMockFactory:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.uut = MockFactory()

    def test_root_factory_has_no_parent(self):
        assert MockInfo(self.uut).parent is None

    def test_child_factory_has_parent_of_uut(self):
        child = self.uut.factory("child")
        assert MockInfo(child).parent.target is self.uut

    @pytest.mark.parametrize(
        "factory, expected_name",
        [
            (MockFactory(), None),
            (MockFactory("spam"), "spam"),
        ],
    )
    def test_get_factory_name(self, factory, expected_name):
        assert MockInfo(factory).name == expected_name

    @pytest.mark.parametrize(
        "factory, expected_full_name",
        [
            (MockFactory(), None),
            (MockFactory("spam"), "spam"),
        ],
    )
    def test_get_factory_full_name(self, factory, expected_full_name):
        assert MockInfo(factory).fullname == expected_full_name

    @pytest.mark.parametrize(
        "factory, expected_full_name",
        [
            (MockFactory(), "bar"),
            (MockFactory("foo"), "foo.bar"),
        ],
    )
    def test_get_full_name_of_nested_factory(self, factory, expected_full_name):
        assert MockInfo(factory.factory("bar")).fullname == expected_full_name

    @pytest.mark.parametrize(
        "factory, expected_full_name",
        [
            (MockFactory(), "bar"),
            (MockFactory("foo"), "foo.bar"),
        ],
    )
    def test_get_full_name_of_created_mock(self, factory, expected_full_name):
        assert MockInfo(factory.mock("bar")).fullname == expected_full_name

    def test_mocks_created_by_factory_share_one_session_object(self):
        first = self.uut.mock("first")
        second = self.uut.mock("second")
        assert MockInfo(first).session is MockInfo(second).session

    def test_created_mock_has_same_name_as_given_one(self):
        first = self.uut.mock("first")
        assert MockInfo(first).fullname == "first"

    def test_when_factory_is_created_with_name__it_is_used_as_mock_name_prefix(self):
        self.uut = MockFactory("foo")
        first = self.uut.mock("first")
        assert MockInfo(first).fullname == "foo.first"

    def test_mock_with_same_name_as_existing_mock_cannot_be_created(self):
        self.uut.mock("foo")
        with pytest.raises(TypeError) as excinfo:
            self.uut.mock("foo")
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_create_nested_factory(self):
        nested = self.uut.factory("nested")
        first = nested.mock("first")
        assert MockInfo(first).fullname == "nested.first"

    def test_mock_with_same_name_as_existing_factory_cannot_be_created(self):
        self.uut.factory("foo")
        with pytest.raises(TypeError) as excinfo:
            self.uut.mock("foo")
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_factory_with_same_name_as_existing_factory_cannot_be_created(self):
        self.uut.factory("foo")
        with pytest.raises(TypeError) as excinfo:
            self.uut.factory("foo")
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_factory_with_same_name_as_existing_mock_cannot_be_created(self):
        self.uut.mock("foo")
        with pytest.raises(TypeError) as excinfo:
            self.uut.factory("foo")
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_create_mock_factory_with_custom_session_and_mock_class(self):

        def factory(name, parent=None):
            return name, parent

        self.uut = MockFactory(session="session", mock_class=factory)
        assert self.uut.mock("foo") == ("foo", self.uut)

    def test_newly_created_factory_has_no_children(self):
        assert set(MockInfo(self.uut).children()) == set()

    def test_factory_with_one_created_mock_has_one_children(self):
        first = self.uut.mock("first")
        assert set(x.target for x in MockInfo(self.uut).children()) == set([first])

    def test_factory_with_one_created_mock_and_one_created_nested_factory_has_two_children(self):
        first = self.uut.mock("first")
        second = self.uut.factory("second")
        assert set(x.target for x in MockInfo(self.uut).children()) == {first, second}

    def test_factory_with_one_mock_and_one_nested_factory_containing_another_mock_has_two_children(self):
        first = self.uut.mock("first")
        second = self.uut.factory("second")
        second.mock("third")
        assert set(x.target for x in MockInfo(self.uut).children()) == {first, second}

    def test_factory_with_no_expectations_has_empty_list_of_expectations(self):
        assert set(MockInfo(self.uut).expectations()) == set()

    def test_factory_containing_mock_with_one_expectation__has_one_expectation(self):
        first = self.uut.mock("foo").expect_call()
        assert set(MockInfo(self.uut).expectations()) == set([first])

    def test_factory_containing_two_mocks_each_with_one_expectation__has_two_expectations(self):
        first = self.uut.mock("foo").expect_call()
        second = self.uut.mock("bar").expect_call()
        assert set(MockInfo(self.uut).expectations()) == set([first, second])

    def test_listing_expectations_does_not_include_nested_factories(self):
        first = self.uut.mock("foo").expect_call()
        second = self.uut.mock("bar").expect_call()
        self.uut.factory("baz").mock("spam").expect_call()
        assert set(MockInfo(self.uut).expectations()) == set([first, second])

    def test_recursive_walk_over_children_does_include_all_expectations(self):

        def all_expectations():
            for child_info in MockInfo(self.uut).walk():
                yield from child_info.expectations()

        first = self.uut.mock("foo").expect_call()
        second = self.uut.mock("bar").expect_call()
        third = self.uut.factory("baz").mock("spam").expect_call()
        assert set(all_expectations()) == set([first, second, third])
