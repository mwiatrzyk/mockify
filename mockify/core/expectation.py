import collections

from .. import _utils
from ..cardinality import Base as CardinalityBase, Exactly, AtLeast


class Expectation:

    def __init__(self, mock_call, filename, lineno):
        self._mock_call = mock_call
        self._filename = filename
        self._lineno = lineno
        self._actions = collections.deque()
        self._repeated_action = None
        self._call_count = Exactly(1)
        self._times_called = False

    def __call__(self, *args, **kwargs):
        self._call_count.update()
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
    def call_count(self):
        return self._call_count

    def is_satisfied(self):
        return self._call_count.is_satisfied()

    def times(self, cardinality):
        if not _utils.is_cardinality_object(cardinality):
            cardinality = Exactly(cardinality)
        self._call_count = cardinality
        self._times_called = True
        return self

    def will_once(self, action):
        self._actions.append(action)
        self._call_count = Exactly(len(self._actions))
        return self

    def will_repeatedly(self, action):
        self._repeated_action = action
        if self._actions:
            self._call_count = AtLeast(len(self._actions))
        elif not self._times_called:
            self._call_count = AtLeast(0)
        return self
