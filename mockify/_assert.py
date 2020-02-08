from . import exc
from .mock import MockInfo


def assert_satisfied(*mocks):
    """Check if all given mocks are **satisfied**.

    This function collects all expectations from given mock for which
    :meth:`Expectation.is_satisfied` evaluates to ``False``. Finally, if at
    least one **unsatisfied** expectation is found, this method raises
    :exc:`mockify.exc.Unsatisfied` exception.

    See :ref:`recording-and-validating-expectations` tutorial for more
    details.
    """

    def iter_unsatisfied_expectations(mocks):
        for mock in mocks:
            for mock_info in MockInfo(mock).walk():
                yield from (x for x in mock_info.expectations() if not x.is_satisfied())

    unsatisfied_expectations = list(iter_unsatisfied_expectations(mocks))
    if unsatisfied_expectations:
        raise exc.Unsatisfied(unsatisfied_expectations)
