import pytest


@pytest.fixture
def registry_mock(mock_factory):

    class Registry:

        def __init__(self, expect_call_mock, call_mock, assert_satisfied_mock):
            self._expect_call_mock = expect_call_mock
            self._call_mock = call_mock
            self._assert_satisfied_mock = assert_satisfied_mock

        def __call__(self, call):
            return self._call_mock(call)

        def expect_call(self, call):
            return self._expect_call_mock(call)

        def assert_satisfied(self, *names):
            return self._assert_satisfied_mock(*names)

    call_mock = mock_factory.function('registry.__call__')
    expect_call_mock = mock_factory.function('registry.expect_call')
    assert_satisfied_mock = mock_factory.function('registry.assert_satisfied')

    Registry.__call__.expect_call = lambda *a, **kw: call_mock.expect_call(*a, **kw)
    Registry.expect_call.expect_call = lambda *a, **kw: expect_call_mock.expect_call(*a, **kw)
    Registry.assert_satisfied.expect_call = lambda *a, **kw: assert_satisfied_mock.expect_call(*a, **kw)

    return Registry(expect_call_mock, call_mock, assert_satisfied_mock)
