class Return:

    def __init__(self, value):
        self._value = value

    def __call__(self, *args, **kwargs):
        return self._value


class Raise:

    def __init__(self, exc):
        self._exc = exc

    def __call__(self, *args, **kwargs):
        raise self._exc


class Invoke:

    def __init__(self, func):
        self._func = func

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)
