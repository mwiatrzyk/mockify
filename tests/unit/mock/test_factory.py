import pytest

from mockify.mock import MockFactory, MockInfo


class TestMockFactory:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.uut = MockFactory()

    def test_mocks_created_by_factory_share_one_session_object(self):
        first = self.uut.mock('first')
        second = self.uut.mock('second')
        assert MockInfo(first).session  is MockInfo(second).session

    def test_created_mock_has_same_name_as_given_one(self):
        first = self.uut.mock('first')
        assert MockInfo(first).fullname == 'first'

    def test_when_factory_is_created_with_name__it_is_used_as_mock_name_prefix(self):
        self.uut = MockFactory('foo')
        first = self.uut.mock('first')
        assert MockInfo(first).fullname == 'foo.first'

    def test_mock_with_same_name_as_existing_mock_cannot_be_created(self):
        self.uut.mock('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.mock('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_create_nested_factory(self):
        nested = self.uut.factory('nested')
        first = nested.mock('first')
        assert MockInfo(first).fullname == 'nested.first'

    def test_mock_with_same_name_as_existing_factory_cannot_be_created(self):
        self.uut.factory('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.mock('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_factory_with_same_name_as_existing_factory_cannot_be_created(self):
        self.uut.factory('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.factory('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_factory_with_same_name_as_existing_mock_cannot_be_created(self):
        self.uut.mock('foo')
        with pytest.raises(TypeError) as excinfo:
            self.uut.factory('foo')
        assert str(excinfo.value) == "Name 'foo' is already in use"

    def test_create_mock_factory_with_custom_session_and_mock_class(self):

        def factory(name, session=None):
            return name, session

        self.uut = MockFactory(session='session', mock_class=factory)
        assert self.uut.mock('foo') == ('foo', 'session')

    def test_list_children(self):
        first = self.uut.mock('first')
        second = self.uut.factory('second')
        third = second.mock('third')
        assert list(x.mock for x in MockInfo(self.uut).children()) == [first, third]

    def test_list_expectations(self):
        first = self.uut.mock('first').expect_call()
        second = self.uut.factory('second')
        third = second.mock('third').expect_call()
        assert list(MockInfo(self.uut).expectations()) == [first, third]

