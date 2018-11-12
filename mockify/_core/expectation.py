import collections

from .._utils import is_cardinality_object, format_call_count
from ..cardinality import Exactly, AtLeast


class Expectation:
    """Represents recorded expectation.

    :param expected_call:
        Instance of :class:`mockify.Call` class representing expected call.
    """

    def __init__(self, expected_call):
        self._expected_call = expected_call
        self._subexpect = _DefaultSubexpect()

    def __repr__(self):
        return "<Expectation: call={}, expected={!r}, actual={!r}>".\
            format(self.expected_call, self.format_expected(), self.format_actual())

    def __call__(self, call):
        return self._next_subexpect._consume(call)

    @property
    def _next_subexpect(self):
        subexpect = self._subexpect
        while subexpect._is_satisfied() and\
              getattr(subexpect, '_subexpect', None) is not None:
            subexpect = subexpect._subexpect
        return subexpect

    @property
    def expected_call(self):
        """Instance of :class:`mockify.Call` representing expected call."""
        return self._expected_call

    def format_action(self):
        """Return string representation of action to be executed next or
        ``None`` if expectation has no actions defined."""
        next_subexpect = self._next_subexpect
        if hasattr(next_subexpect, '_format_action'):
            return self._next_subexpect._format_action()

    def format_expected(self):
        """Return string representation how many times this expectation is
        expected to be consumed."""
        return self._next_subexpect._format_expected()

    def format_actual(self):
        """Return string representation of how many times this expectation was
        consumed so far."""
        return self._next_subexpect._format_actual()

    def is_satisfied(self):
        """Check if this expectation is already satisfied."""
        return self._next_subexpect._is_satisfied()

    def times(self, cardinality):
        """Set call cardinality for this expectation.

        :param cardinality:
            Call count cardinality.

            This can be either integer number (exact number of calls is
            expected) or instance of one of the classes specified in
            :mod:`mockify.cardinality` module.
        """
        self._subexpect = tmp = _TimesSubexpect(cardinality)
        return tmp

    def will_once(self, action):
        """Set action to be once executed when expectation is consumed.

        This method returns special proxy object that allows calling another
        ``will_once`` (or :meth:`will_repeatedly`) method to record action
        sequence. These actions will later be executed in same order as were
        declared. Expectation with ``will_once`` will not be satisfied unless
        all actions are executed.

        :param action:
            Action to be executed once.

            This is instance of one of the classes defined inside
            :mod:`mockify.actions` module.
        """
        self._subexpect = tmp = _WillOnceSubexpect(action)
        return tmp

    def will_repeatedly(self, action):
        """Set action to be executed repeatedly.

        This method returns special proxy method that has :meth:`times`
        allowing setting cardinality for repeated action. By default, repeated
        action can be executed any times (including zero). This must be last
        action in the chain.

        :param action:
            Action to be executed repeatedly.

            This is instance of one of the classes defined inside
            :mod:`mockify.actions` module.
        """
        self._subexpect = tmp = _WillRepeatedlySubexpect(action)
        return tmp


class _DefaultSubexpect:

    def __init__(self):
        self._call_count = 0

    def _consume(self, call):
        self._call_count += 1

    def _is_satisfied(self):
        return self._call_count == 1

    def _format_expected(self):
        return 'to be called once'

    def _format_actual(self):
        if self._call_count == 0:
            return 'never called'
        else:
            return "called {}".format(format_call_count(self._call_count))


class _TimesSubexpect:

    def __init__(self, cardinality):
        if not is_cardinality_object(cardinality):
            self._cardinality = Exactly(cardinality)
        else:
            self._cardinality = cardinality

    def __repr__(self):
        return "<Times: expected={!r}, actual={!r}>".\
            format(self._format_expected(), self._format_actual())

    def _consume(self, call):
        self._cardinality.update()

    def _is_satisfied(self):
        return self._cardinality.is_satisfied()

    def _format_expected(self):
        return self._cardinality.format_expected()

    def _format_actual(self):
        return self._cardinality.format_actual()


class _WillOnceSubexpect:

    def __init__(self, action):
        self._action = action
        self._call_count = 0
        self._subexpect = None

    def _consume(self, call):
        self._call_count += 1
        return self._action(*call.args, **call.kwargs)

    def _is_satisfied(self):
        return self._call_count == 1

    def _format_action(self):
        return str(self._action)

    def _format_expected(self):
        return 'to be called once'

    def _format_actual(self):
        if self._call_count == 0:
            return 'never called'
        else:
            return "called {}".format(format_call_count(self._call_count))

    def will_once(self, action):
        self._subexpect = tmp = self.__class__(action)
        return tmp

    def will_repeatedly(self, action):
        self._subexpect = tmp = _WillRepeatedlySubexpect(action)
        return tmp


class _WillRepeatedlySubexpect:

    def __init__(self, action):
        self._action = action
        self._subexpect = None
        self._cardinality = None

    def _consume(self, call):
        if self._cardinality is not None:
            self._cardinality.update()
        return self._action(*call.args, **call.kwargs)

    def _is_satisfied(self):
        return self._cardinality is None or\
            self._cardinality.is_satisfied()

    def _format_action(self):
        return str(self._action)

    def _format_expected(self):
        return self._cardinality.format_expected()

    def _format_actual(self):
        return self._cardinality.format_actual()

    def times(self, cardinality):
        if is_cardinality_object(cardinality):
            self._cardinality = cardinality
        else:
            self._cardinality = Exactly(cardinality)
