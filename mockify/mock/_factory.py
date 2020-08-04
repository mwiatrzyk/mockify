from ._mock import Mock
from ._base import IMockInfoTarget
from .._engine import Session


class MockFactory(IMockInfoTarget):
    """A factory class used to create groups of related mocks.

    This class allows to create mocks using class given by *mock_class*
    ensuring that:

    * names of created mocks are **unique**,
    * all mocks share one common session object.

    Instances of this class keep track of created mocks. Moreover, functions
    that would accept :class:`Mock` instances will also accept
    :class:`MockFactory` instances, so you can later f.e. check if all
    created mocks are satisfied using just a factory object. That makes it
    easy to manage multiple mocks in large test suites.

    See :ref:`managing-multiple-mocks` for more details.

    .. versionadded:: 0.6

    :param name:
        This is optional.

        Name of this factory to be used as a common prefix for all created
        mocks and nested factories.

    :param session:
        Instance of :class:`mockify.Session` to be used.

        If not given, a default session will be created and shared across all
        mocks created by this factory.

    :param mock_class:
        The class that will be used by this factory to create mocks.

        By default it will use :class:`Mock` class.
    """

    def __init__(self, name=None, session=None, mock_class=None):
        self._name = name
        self._session = session or Session()
        self._mock_class = mock_class or Mock
        self._factories = {}
        self._mocks = {}

    @property
    def __m_name__(self):
        return self._name

    @property
    def __m_fullname__(self):
        return self._name  # FIXME: should include nested factories

    @property
    def __m_session__(self):
        return self._session

    def __m_children__(self):
        yield from self._mocks.values()
        for child_factory in self._factories.values():
            yield from child_factory.__m_children__()

    def __m_expectations__(self):
        for mock in self.__m_children__():
            yield from mock.__m_expectations__()

    def mock(self, name):
        """Create and return mock of given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.
        """
        self._validate_name(name)
        self._mocks[name] = tmp =\
            self._mock_class(self._format_name(name), session=self._session)
        return tmp

    def factory(self, name):
        """Create and return child factory.

        Child factory will use session from its parent, and will prefix all
        mocks and grandchild factories with given *name*.

        This method will raise :exc:`TypeError` if *name* is already used by
        either mock or child factory.

        :rtype: MockFactory
        """
        self._validate_name(name)
        self._factories[name] = tmp = self.__class__(
            self._format_name(name),
            session=self._session,
            mock_class=self._mock_class)
        return tmp

    def _validate_name(self, name):
        if name in self._mocks or name in self._factories:
            raise TypeError("Name {!r} is already in use".format(name))

    def _format_name(self, name):
        if self._name is None:
            return name
        else:
            return "{}.{}".format(self._name, name)
