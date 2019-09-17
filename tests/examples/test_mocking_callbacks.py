import pytest

from _mockify import satisfies
from _mockify.mock import Mock


class Observable:

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
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
        observer.expect_call(self.uut)

        self.uut.subscribe(observer)

        with satisfies(observer):
            self.uut.notify()

    def test_when_notify_called_twice__observer_is_triggered_twice(self):
        observer = Mock('observer')
        observer.expect_call(self.uut).times(2)

        self.uut.subscribe(observer)

        with satisfies(observer):
            for _ in range(2):
                self.uut.notify()
