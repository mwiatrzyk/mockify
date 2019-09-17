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

    def test_subscribe_observer_and_notify_once(self):
        observable = Observable()

        observer = Mock('observer')
        observer.expect_call(observable)

        observable.subscribe(observer)

        with satisfies(observer):
            observable.notify()
