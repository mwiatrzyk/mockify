import collections

from .. import _utils
from ..cardinality import Exactly, AtLeast


class Expectation:

    def __init__(self, mock_call, filename, lineno):
        self._mock_call = mock_call
        self._filename = filename
        self._lineno = lineno
        self._actual_calls = 0
        self._actions = collections.deque()
        self._repeated_action = None
        self.__expected_calls = None

    def __call__(self, *args, **kwargs):
        self._actual_calls += 1
        action = self.__get_action()
        if action is not None:
            return action(*args, **kwargs)

    def __get_action(self):
        if self._actions:
            return self._actions.popleft()
        elif self._repeated_action is not None:
            return self._repeated_action

    @property
    def mock_call(self):
        return self._mock_call

    @property
    def filename(self):
        return self._filename

    @property
    def lineno(self):
        return self._lineno

    @property
    def expected_calls(self):
        return self.__expected_calls or Exactly(1)

    @expected_calls.setter
    def expected_calls(self, value):
        self.__expected_calls = value

    @property
    def actual_calls(self):
        return self._actual_calls

    def is_satisfied(self):
        return self.expected_calls._satisfies_actual(self._actual_calls)

    def times(self, cardinality):
        if not _utils.is_cardinality_object(cardinality):
            cardinality = Exactly(cardinality)
        self.expected_calls = cardinality
        return self

    def will_once(self, action):
        self._actions.append(action)
        self.expected_calls = Exactly(len(self._actions))
        return self

    def will_repeatedly(self, action):
        self._repeated_action = action
        if self._actions:
            self.expected_calls = AtLeast(len(self._actions))
        elif self.__expected_calls is None:
            self.expected_calls = AtLeast(0)
        return self
