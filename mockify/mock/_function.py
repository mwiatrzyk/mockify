from .. import _utils
from ._base import BaseMock
from .._engine import Session, Call


class FunctionMock(BaseMock):
    """Class for mocking Python functions.

    This is most basic mock class Mockify provides. It can be used as a
    standalone mock, for mocking standalone functions in tests, or to build
    more complex mocks.

    :param name:
        Name of mocked function.

        This must a valid Python identifier or series of valid Python
        identifiers concatenated with a period sign (f.e. ``foo.bar.baz``).

    :param session:
        Instance of :class:`mockify.Session` to be used by this mock.

        Default one will be created if not given, although some of Mockify
        features require sharing a session between several mocks.

    .. versionadded:: 0.8
    """

    def __init__(self, name, session=None):
        _utils.validate_mock_name(name)
        self.__name = name
        self.__session = session or Session()
        self.__m_parent__ = None

    @property
    def __m_name__(self):
        return self.__name

    @property
    def __m_session__(self):
        return self.__session

    def __m_children__(self):
        return
        yield  # Function mock has no children

    def __m_expectations__(self):
        return filter(
            lambda x: x.expected_call.name == self.__m_fullname__,
            self.__session.expectations())

    def __call__(self, *args, **kwargs):
        return self.__m_session__(Call(self.__m_fullname__, *args, **kwargs))

    def expect_call(self, *args, **kwargs):
        return self.__m_session__.expect_call(Call(self.__m_fullname__, *args, **kwargs))
