from .. import exc

from .mock import Mock, MockCall
from .expectation import Expectation


class Context:

    def __init__(self, ordered=True, mock_class=Mock, expectation_class=Expectation):
        self._ordered = ordered
        self._mock_class = mock_class
        self._expectation_class = expectation_class
        self._expectations = []

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.assert_satisfied()

    def __call__(self, name, args, kwargs):
        mock_call = MockCall(name, args, kwargs)
        expectation = self.__find_expectation_for(mock_call)
        return expectation(*args, **kwargs)

    def expect_call(self, name, args, kwargs, filename, lineno):
        mock_call = MockCall(name, args, kwargs)
        expectation = self._expectation_class(mock_call, filename, lineno)
        self._expectations.append(expectation)
        return expectation

    def make_mock(self, name):
        return self._mock_class(self, name)

    def make_mocks(self, *names):
        return tuple(self.make_mock(name) for name in names)

    def assert_satisfied(self):
        for expectation in self._expectations:
            if not expectation.is_satisfied():
                raise exc.Unsatisfied(self._expectations)

    def __find_expectation_for(self, mock_call):
        all_matching = self.__find_all_for(mock_call)
        if not all_matching:
            raise exc.UninterestedMockCall(mock_call)
        if self._ordered:
            return self.__find_ordered(all_matching, mock_call)
        else:
            return self.__find_unordered(all_matching)

    def __find_ordered(self, matching, mock_call):
        next_expected = self.__find_next_expected()
        for expectation in matching:
            if not expectation.is_satisfied() and (next_expected is None or expectation is next_expected):
                return expectation
        if next_expected is not None and matching[-1] is not next_expected:
            raise exc.UnexpectedMockCall(next_expected, mock_call)
        return matching[-1]

    def __find_unordered(self, matching):
        for expectation in matching:
            if not expectation.is_satisfied():
                return expectation
        return matching[-1]

    def __find_all_for(self, mock_call):
        return list(filter(lambda x: x.mock_call == mock_call, self._expectations))

    def __find_next_expected(self):
        return next(filter(lambda x: not x.is_satisfied(), self._expectations), None)
