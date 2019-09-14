import pytest


@pytest.fixture
def registry_mock(mock_factory):

    def make_expect_call(name):
        getattr(Registry, name).expect_call =\
            lambda *args, **kwargs: mocks[name].expect_call(*args, **kwargs)

    class Registry:

        def __init__(self, mocks):
            self._mocks = mocks
            self._expected_calls = []

        def __call__(self, call):
            return self._mocks['__call__'](call)

        def expect_call(self, call):
            self._expected_calls.append(call)
            return self._mocks['expect_call'](call)

        def assert_satisfied(self, *args, **kwargs):
            return self._mocks['assert_satisfied'](*args, **kwargs)

        def matching_expectations(self, call):
            for expected_call in self._expected_calls:
                if expected_call == call:
                    yield expected_call

        def has_expectations_for(self, name):
            for expected_call in self._expected_calls:
                if expected_call.name == name:
                    return True
            return False

    mocked_methods = (
        '__call__', 'expect_call', 'assert_satisfied'
    )

    mocks = {}
    for name in mocked_methods:
        mocks[name] = mock_factory.function(f"registry.{name}")
        make_expect_call(name)

    return Registry(mocks)


@pytest.fixture
def expectation_mock(mock_factory):
    return mock_factory.namespace('expectation')
