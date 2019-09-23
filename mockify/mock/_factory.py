from contextlib import contextmanager

from .. import _utils
from .._engine import satisfies, Context

__all__ = export = _utils.ExportList()


@export
class Factory:
    """Generic mock object factory.

    It is used to create several mocks of one type that share same context
    and can be checked all at once.

    .. versionadded:: 1.0

    :param mock_class:
        Mock class to be used.

        All mocks created by this factory will be instances of this class.

    :param ctx:
        Instance of :class:`mockify.Context` to be used.

        If not given, default one will be created and use for all mocks
        created by this factory. You will find this useful if you need to use
        several mock factories in your test that need to share single context
        object.
    """

    def __init__(self, mock_class, ctx=None):
        self._mock_class = mock_class
        self._ctx = ctx or Context()
        self._created_mocks = []

    def __call__(self, name):
        """Create mock of given name."""
        mock = self._mock_class(name, ctx=self._ctx)
        self._created_mocks.append(mock)
        return mock

    @contextmanager
    def satisfied(self):
        """Context manager to check if all mocks created by this factory are
        satisfied after leaving wrapped scope."""
        with satisfies(*self._created_mocks):
            yield
