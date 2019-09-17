import functools

import pytest


@pytest.fixture
def registry_mock(mock_factory):

    class Registry:

        class _ExpectationQuery:

            class _QueryResult:

                def __init__(self, registry, items):
                    self._registry = registry
                    self._items = items

                def exists(self):
                    return next(self._items, None) is not None

                def assert_satisfied(self):
                    self._registry._checked_mock_names.extend([x.name for x in self._items])

            def __init__(self, registry):
                self._registry = registry

            def by_name(self, name):
                items = filter(lambda x: x.name == name, self._registry._expected_calls)
                return self._QueryResult(self._registry, items)

            def by_name_prefix(self, name_prefix):
                items = filter(lambda x: x.name.startswith(name_prefix), self._registry._expected_calls)
                return self._QueryResult(self._registry, items)

            def by_call(self, call):
                items = filter(lambda x: x == call, self._registry._expected_calls)
                return self._QueryResult(self._registry, items)

        def __init__(self):
            self._calls = []
            self._expected_calls = []
            self._checked_mock_names = []

            self.on_call = None

        def __call__(self, call):
            self._calls.append(call)
            if self.on_call is not None:
                return self.on_call(call)

        def expect_call(self, call):
            self._expected_calls.append(call)

        @property
        def expectations(self):
            return self._ExpectationQuery(self)

        # Assertion checking interface

        @property
        def calls(self):
            return self._calls

        @property
        def expected_calls(self):
            return self._expected_calls

        @property
        def checked_mock_names(self):
            return self._checked_mock_names

    return Registry()



"""
    assert_satisfied_name = 'registry.ExpectationFilter.FilterResult.assert_satisfied'

    def make_expect_call(name):
        getattr(Registry, name).expect_call =\
            lambda *args, **kwargs: mocks[name].expect_call(*args, **kwargs)

    class Registry:

        class ExpectationFilter:

            class FilterResult:

                def __init__(self, filtered_expectations):
                    self._filtered_expectations = filtered_expectations

                def exists(self):
                    return next(self._filtered_expectations, None) is not None

                def assert_satisfied(self):
                    mocks[assert_satisfied_name](*self._filtered_expectations)

            def __init__(self, expectations):
                self._expectations = expectations

            def by_name(self, name):
                return self.FilterResult(
                    filter(lambda x: x.name == name, self._expectations))

            def by_name_prefix(self, name_prefix):
                return self.FilterResult(
                    filter(lambda x: x.name.startswith(name_prefix), self._expectations))

            def by_call(self, call):
                return self.FilterResult(
                    filter(lambda x: x == call, self._expectations))

        def __init__(self, mocks):
            self._mocks = mocks
            self._expected_calls = []

        def __call__(self, call):
            return self._mocks['__call__'](call)

        def expect_call(self, call):
            self._expected_calls.append(call)
            return self._mocks['expect_call'](call)

        #def assert_satisfied(self, *args, **kwargs):
        #    return self._mocks['assert_satisfied'](*args, **kwargs)

        @property
        def expectations(self):
            return self.ExpectationFilter(self._expected_calls)

    mocked_methods = (
        '__call__', 'expect_call',
    )

    mocks = {}
    for name in mocked_methods:
        mocks[name] = mock_factory.function(f"registry.{name}")
        make_expect_call(name)

    mocks[assert_satisfied_name] = mock_factory.function(assert_satisfied_name)
    Registry.ExpectationFilter.FilterResult.assert_satisfied.expect_call =\
        lambda *args: mocks[assert_satisfied_name].expect_call(*args)

    return Registry(mocks)
"""
