from . import exc
from .mock import MockInfo


def assert_satisfied(*mocks):
    """Check if all given mocks are satisfied."""

    def iter_unsatisfied_expectations(mocks):
        for mock in mocks:
            for mock_info in MockInfo(mock).walk():
                yield from (x for x in mock_info.expectations if not x.is_satisfied())

    unsatisfied_expectations = list(iter_unsatisfied_expectations(mocks))
    if unsatisfied_expectations:
        raise exc.Unsatisfied(unsatisfied_expectations)
