import pytest


@pytest.fixture
def registry_stub():

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
