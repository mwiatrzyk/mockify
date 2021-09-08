import typing

from mockify import _utils
from mockify.abc import IExpectation, IMock, ISession

__all__ = export = _utils.ExportList()


@export
class MockInfo:
    """A class for inspecting mocks.

    This class simplifies the use of Mockify-defined special methods and
    properties that must be implemented by :class:`mockify.abc.IMock`
    subclasses. It is like a :func:`getattr` to be used on top of
    :mod:`object.__getattr__` magic method.

    Although this class is basically a 1-1 proxy on top of ``__m_(.*)__``
    properties provided by :class:`mockify.abc.IMock`, some methods
    additionally wrap results with :class:`MockInfo` instances.

    :param target:
        Mock to be inspected
    """

    def __init__(self, target: IMock):
        if not isinstance(target, IMock):
            raise TypeError(
                "__init__() got an invalid value for argument 'target'"
            )
        self._target = target

    def __repr__(self):
        return "<mockify.core.{self.__class__.__qualname__}(target={self._target!r})>".format(
            self=self
        )

    @property
    def mock(self) -> IMock:
        """Target mock that is being inspected.

        .. deprecated:: 0.8
            This is deprecated since version 0.8 and will be dropped in one
            of upcoming releases. Use :attr:`target` instead.
        """
        old = _utils.get_attr_qualname('mockify.core', self.__class__.mock)
        new = _utils.get_attr_qualname('mockify.core', self.__class__.target)
        _utils.warn_renamed(old, new, '0.8')
        return self.target

    @property
    def target(self) -> IMock:
        """Target mock that is being inspected.

        .. versionadded:: 0.8
        """
        return self._target

    @property
    def parent(self) -> 'MockInfo':
        """A proxy to access :attr:`BaseMock.__m_parent__`.

        Returns ``None`` if target has no parent, or parent wrapped with
        :class:`MockInfo` object otherwise.

        .. versionadded:: 0.8
        """
        parent = self._target.__m_parent__
        if parent is None:
            return None
        return self.__class__(parent)

    @property
    def name(self) -> str:
        """Return name of target mock.

        This is equivalent of using :attr:`mockify.abc.IMock.__m_name__`
        attribute on a target mock.

        .. versionchanged:: 0.8
            It is no longer full name; for that purpose use new :attr:`fullname`
        """
        return self._target.__m_name__

    @property
    def fullname(self) -> str:
        """Return full name of target mock.

        This is equivalent of using :attr:`mockify.abc.IMock.__m_fullname__`
        attribute on a target mock.

        .. versionchanged:: (unreleased)
            Now this is not calculating full name, but simply is calling
            :attr:`mockify.abc.IMock.__m_fullname__` on target mock.

        .. versionadded:: 0.8
        """
        return self._target.__m_fullname__

    @property
    def session(self) -> ISession:
        """Return :class:`mockify.abc.ISession` object assigned to target mock.

        This is equivalent of using :attr:`mockify.abc.IMock.__m_session__`
        attribute on a target mock.

        """
        return self._target.__m_session__

    def expectations(self) -> typing.Iterator[IExpectation]:
        """Return iterator over expectation objects created on target mock.

        This is equivalent of using
        :meth:`mockify.abc.IMock.__m_expectations__` method on a target
        mock.
        """
        for expectation in self._target.__m_expectations__():
            yield expectation

    def children(self) -> typing.Iterator['MockInfo']:
        """Return iterator over target mock's direct children.

        This uses :meth:`mockify.abc.IMock.__m_children__` method on a
        target mock behind the scenes, but wraps each returned child with a new
        :class:`MockInfo` object.
        """
        for child in self._target.__m_children__():
            yield self.__class__(child)

    def walk(self) -> typing.Iterator['MockInfo']:
        """Recursively iterate over tree structure of given target mock.

        Behind the scenes this uses :meth:`mockify.abc.IMock.__m_walk__` method
        on a target mock, but wraps each yielded child with a new
        :class:`MockInfo` object.

        It always yields *self* as a first generated item.

        .. versionchanged:: (unreleased)
            Now this is simply calling :meth:`mockify.abc.IMock.__m_walk__`
            behind the scenes.
        """
        for item in self._target.__m_walk__():
            yield self.__class__(item)
