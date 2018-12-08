# ---------------------------------------------------------------------------
# mockify/_core/expectation.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------

import itertools
import collections

from mockify import exc, _utils
from mockify.times import Exactly, AtLeast


def _wrap_expected_count(expected_count):
    if isinstance(expected_count, int):
        return Exactly(expected_count)
    else:
        return expected_count


class StackInfo:

    def __init__(self, filename, lineno):
        self._filename = filename
        self._lineno = lineno

    def __str__(self):
        return "{}:{}".format(self._filename, self._lineno)


class Call:

    def __init__(self, name, args=None, kwargs=None, stackinfo=None):
        self._name = name
        self._args = args or tuple()
        self._kwargs = kwargs or {}
        self._stackinfo = stackinfo

    def __str__(self):
        args_gen = (repr(x) for x in self._args)
        kwargs_gen = ("{}={!r}".format(k, v) for k, v in sorted(self._kwargs.items()))
        all_gen = itertools.chain(args_gen, kwargs_gen)
        return "{}({})".format(self._name, ", ".join(all_gen))

    def __eq__(self, other):
        return self._name == other._name and\
            self._args == other._args and\
            self._kwargs == other._kwargs

    @property
    def stackinfo(self):
        return self._stackinfo


class Registry:

    def __init__(self):
        self._expects = []

    def __call__(self, call):
        matching_expects = list(filter(lambda x: x.match(call), self._expects))
        if not matching_expects:
            raise exc.UninterestedCall(call)
        for expect in matching_expects:
            if not expect.is_satisfied():
                return expect(call)
        else:
            return matching_expects[-1](call)

    def expect_call(self, call):
        expect = Expectation(call)
        self._expects.append(expect)
        return expect

    def assert_satisfied(self):
        unsatisfied = []
        for expect in self._expects:
            if not expect.is_satisfied():
                unsatisfied.append(expect)
        if unsatisfied:
            raise exc.UnsatisfiedAssertion(unsatisfied)


class Expectation:

    class _DefaultProxy:

        def __init__(self):
            self._call_count = 0

        def __call__(self, call):
            self._call_count += 1

        def is_satisfied(self):
            return self._call_count == 1

    class _TimesProxy:

        def __init__(self, expected_count):
            self._actual_count = 0
            self._expected_count = _wrap_expected_count(expected_count)

        def __call__(self, call):
            self._actual_count += 1

        def is_satisfied(self):
            return self._expected_count == self._actual_count

    class _ActionProxy:

        def __init__(self, action):
            self._actions = collections.deque([action])
            self._expected_count = 1
            self._actual_count = 0
            self._next_proxy = None

        def __call__(self, call):
            if not self.is_satisfied():
                return self.__invoke_action(call)
            elif self._next_proxy is not None:
                return self._next_proxy(call)
            else:
                return self.__invoke_action(call)

        def __invoke_action(self, call):
            self._actual_count += 1
            try:
                return self._actions[0](call)
            finally:
                if len(self._actions) > 1:
                    self._actions.popleft()

        def is_satisfied(self):
            return self._actual_count == self._expected_count

        def will_once(self, action):
            self._actions.append(action)
            self._expected_count += 1

        def will_repeatedly(self, action):
            self._next_proxy = tmp = Expectation._RepeatedActionProxy(action)
            return tmp

    class _RepeatedActionProxy:

        def __init__(self, action):
            self._action = action
            self._expected_count = AtLeast(0)
            self._actual_count = 0
            self._next_proxy = None

        def __call__(self, call):
            if not self.is_satisfied():
                return self.__invoke_action(call)
            elif self._next_proxy is not None:
                return self._next_proxy(call)
            else:
                return self.__invoke_action(call)

        def __invoke_action(self, call):
            self._actual_count += 1
            return self._action(call)

        def is_satisfied(self):
            return self._expected_count == self._actual_count

        def times(self, expected_count):
            self._expected_count = _wrap_expected_count(expected_count)
            return self

        def will_once(self, action):
            self._next_proxy = tmp = Expectation._ActionProxy(action)
            return tmp

        def will_repeatedly(self, action):
            self._next_proxy = tmp = self.__class__(action)
            return self

    def __init__(self, expected_call):
        self._expected_call = expected_call
        self._next_proxy = self._DefaultProxy()

    def __call__(self, call):
        if not self.match(call):
            raise TypeError("expectation can only be called with matching 'Call' object")
        return self._next_proxy(call)

    def match(self, call):
        return self._expected_call == call

    def is_satisfied(self):
        tmp = self._next_proxy
        while tmp is not None:
            if not tmp.is_satisfied():
                return False
            tmp = getattr(tmp, '_next_proxy', None)
        return True

    def times(self, expected_count):
        self._next_proxy = tmp = self._TimesProxy(expected_count)
        return tmp

    def will_once(self, action):
        self._next_proxy = tmp = self._ActionProxy(action)
        return tmp

    def will_repeatedly(self, action):
        self._next_proxy = tmp = self._RepeatedActionProxy(action)
        return tmp
