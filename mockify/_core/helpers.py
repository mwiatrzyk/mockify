from contextlib import contextmanager


@contextmanager
def assert_satisfied(*mocks):
    """Context manager ensuring that all mocks given as positional args are
    satisfied once scope is left.

    This is very handy helper when there are two or more mocks to be
    checked.
    """
    yield
    for mock in mocks:
        mock.assert_satisfied()
