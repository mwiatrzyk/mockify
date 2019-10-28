import pytest

from mockify import ordered


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
    def make_uut(self, mock_factory):
        self.uut = Observable()
        self.mock_factory = mock_factory

    def test_subscribe_observer_and_notify_once(self):
        observer = self.mock_factory('observer')

        self.uut.subscribe(observer)

        observer.expect_call(self.uut)

        self.uut.notify()

    def test_when_notify_called_twice__observer_is_triggered_twice(self):
        observer = self.mock_factory('observer')
        observer.expect_call(self.uut).times(2)

        self.uut.subscribe(observer)

        for _ in range(2):
            self.uut.notify()

    def test_when_subscribed_twice__it_is_notified_only_once(self):
        observer = self.mock_factory('observer')

        self.uut.subscribe(observer)
        self.uut.subscribe(observer)

        observer.expect_call(self.uut)

        self.uut.notify()

    def test_observers_are_triggered_in_subscribe_order(self):
        first, second = self.mock_factory('first'), self.mock_factory('second')

        self.uut.subscribe(first)
        self.uut.subscribe(second)

        first.expect_call(self.uut)
        second.expect_call(self.uut)

        with ordered(first, second):
            self.uut.notify()
