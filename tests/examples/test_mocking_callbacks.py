import pytest

from mockify import ordered, satisfied
from mockify.mock import Mock, MockGroup


class Observable:

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer(self)


class TestObservable:

    @pytest.fixture(autouse=True)
    def make_uut(self):
        self.uut = Observable()

    def test_subscribe_observer_and_notify_once(self):
        observer = Mock('observer')

        self.uut.subscribe(observer)

        observer.expect_call(self.uut)

        with satisfied(observer):
            self.uut.notify()

    def test_when_notify_called_twice__observer_is_triggered_twice(self):
        observer = Mock('observer')
        observer.expect_call(self.uut).times(2)

        self.uut.subscribe(observer)

        with satisfied(observer):
            for _ in range(2):
                self.uut.notify()

    def test_when_subscribed_twice__it_is_notified_only_once(self):
        observer = Mock('observer')

        self.uut.subscribe(observer)
        self.uut.subscribe(observer)

        observer.expect_call(self.uut)

        with satisfied(observer):
            self.uut.notify()

    def test_observers_are_triggered_in_subscribe_order(self):
        group = MockGroup()
        first, second = group.mock('first'), group.mock('second')

        self.uut.subscribe(first)
        self.uut.subscribe(second)

        first.expect_call(self.uut)
        second.expect_call(self.uut)

        with satisfied(group):
            with ordered(group):
                self.uut.notify()
