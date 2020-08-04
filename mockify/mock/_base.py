import abc
import weakref

from .. import _utils


class IMockInfoTarget(abc.ABC):
    """An interface to be implemented by mock classes and other mocking
    utilities (like mock factories) that can be inspected with a
    :class:`MockInfo` class.

    .. versionadded:: 0.8
    """

    @property
    @abc.abstractmethod
    def __m_name__(self):
        """Mock name.

        This must be a name of target that is being inspected, f.e. the name
        that was set when mock object was created.
        """

    @property
    @abc.abstractmethod
    def __m_fullname__(self):
        """Full mock name.

        It should be composed by concatenating target's parent's
        :attr:`__m_fullname__` with target's name using period sign. If
        target has no parent, this should the same as :attr:`__m_name__`.
        """

    @property
    @abc.abstractmethod
    def __m_session__(self):
        """Instance of :class:`mockify.Session` used by target."""

    @abc.abstractmethod
    def __m_expectations__(self):
        """Iterator over :class:`mockify.Expectation` objects, each
        representing single expectation recorded on target.

        This should not include expectations recorded on target's children
        (if any).
        """

    @abc.abstractmethod
    def __m_children__(self):
        """Iterator over target's direct children.

        We say that target has children if f.e. it is an object mock, and it
        has methods inside. Then this iterator should iterate over object's
        mocked methods.

        This should not include target's grandchildren. If target has no
        children, then this should yield nothing.
        """


class MockInfo:
    """An object used to inspect mocks and mock factories.

    This class provides a sort of public interface on top of underlying
    :class:`IMockInfoTarget` instance (that is implemented by mocks and mock
    factories), that due to their specific nature has no methods or
    properties publicly available.

    :param target:
        Instance of :class:`IMockInfoTarget` object to be inspected
    """

    def __init__(self, target):
        self._target = target

    def __repr__(self):
        return "<{}.{}({!r})>".format(self.__module__, self.__class__.__name__, self._target)

    @property
    def mock(self):
        """Target mock that is being inspected.

        .. deprecated:: 0.8
            This is deprecated since version 0.8 and will be dropped in one
            of upcoming releases. Use :attr:`target` instead.
        """
        return self._target

    @property
    def target(self):
        """Reference to inspected target.

        .. versionadded:: 0.8
        """
        return self._target

    @property
    def name(self):
        """Target's name.

        .. versionchanged:: 0.8
            It is no longer full name; for that purpose use new :attr:`fullname`
        """
        return self._target.__m_name__

    @property
    def fullname(self):
        """Target's full name.

        .. versionadded:: 0.8
        """
        return self._target.__m_fullname__

    @property
    def session(self):
        """Instance of :class:`mockify.Session` used by target."""
        return self._target.__m_session__

    def expectations(self):
        """Iterator over :class:`mockify.Expectation` objects, each
        representing single expectation recorded on target.

        If there are no expectations recorded for target, then this will
        yield nothing. Note that this method does not include expectations
        recorded on target's children. To get all expectations you need to
        combine this method with :meth:`walk`.
        """
        return self._target.__m_expectations__()

    def children(self):
        """Iterator over target's children.

        It yields :class:`MockInfo` object for each target's children.
        """
        return map(lambda x: self.__class__(x), self._target.__m_children__())

    def walk(self):
        """Recursively iterate over target's children.

        It always yields this mock info object as first element. If target
        has no children, then single element (this one) will be returned.
        This method is a handy helper used f.e. to get all expectations
        recorded on given mock.
        """

        def walk(mock_info):
            yield mock_info
            for child_info in mock_info.children():
                yield from walk(child_info)

        yield from walk(self)


class BaseMock(IMockInfoTarget):
    """Base class for all mocks.

    :param name:
        Name of this mock

    :param session:
        Instance of :class:`mockify.Session` to be used by this mock.

    :param parent:
        Parent for this mock.

        This must be instance of :class:`BaseMock`

    .. versionadded:: 0.8
    """

    def __init__(self, name, session, parent=None):
        _utils.validate_mock_name(name)
        self.__name = name
        self.__session = session
        self.__m_parent__ = parent

    def __repr__(self):
        return "<{}.{}({!r})>".format(self.__module__, self.__class__.__name__, self.__m_fullname__)

    @property
    def __m_parent__(self):
        if self.__parent is not None:
            return self.__parent()

    @__m_parent__.setter
    def __m_parent__(self, value):
        if value is None:
            self.__parent = value
        else:
            self.__parent = weakref.ref(value)

    @property
    def __m_name__(self):
        return self.__name

    @property
    def __m_fullname__(self):
        parent = self.__m_parent__
        if parent is None:
            return self.__m_name__
        else:
            return "{}.{}".format(parent.__m_fullname__, self.__m_name__)

    @property
    def __m_session__(self):
        return self.__session
