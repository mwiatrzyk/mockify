from contextlib import contextmanager


@contextmanager
def assert_satisfied(*mocks):
    """Context manager for verifying multiple mocks at once.

    It ensures, that all mocks are not satisfied before entering scope, and all
    are satisfied after leaving scope. This allows to have more clean tests.

    This is very handy helper when there are two or more mocks to be checked.
    """
    for mock in mocks:
        mock.assert_not_satisfied()
    yield
    for mock in mocks:
        mock.assert_satisfied()
