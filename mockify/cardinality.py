from ._utils import format_call_count


class Base:

    def __init__(self):
        self._actual = 0

    def format_actual(self):
        if self._actual == 0:
            return "never called"
        else:
            return "called {}".format(format_call_count(self._actual))

    def update(self):
        self._actual += 1


class Exactly(Base):

    def __init__(self, expected):
        if expected < 0:
            raise TypeError("value of 'expected' must be >= 0")
        super().__init__()
        self._expected = expected

    def format_expected(self):
        if self._expected == 0:
            return "to be never called"
        else:
            return "to be called {}".format(format_call_count(self._expected))

    def is_satisfied(self):
        return self._expected == self._actual


class AtLeast(Base):

    def __init__(self, minimal):
        if minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        super().__init__()
        self._minimal = minimal

    def format_expected(self):
        return "to be called at least {}".format(format_call_count(self._minimal))

    def is_satisfied(self):
        return self._minimal <= self._actual


class AtMost(Base):

    def __new__(cls, maximal):
        if maximal < 0:
            raise TypeError("value of 'maximal' must be >= 0")
        elif maximal == 0:
            return Exactly(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, maximal):
        super().__init__()
        self._maximal = maximal

    def format_expected(self):
        return "to be called at most {}".format(format_call_count(self._maximal))

    def is_satisfied(self):
        return self._maximal >= self._actual


class Between(Base):

    def __new__(cls, minimal, maximal):
        if minimal > maximal:
            raise TypeError("value of 'minimal' must not be greater than 'maximal'")
        elif minimal < 0:
            raise TypeError("value of 'minimal' must be >= 0")
        elif minimal == maximal:
            return Exactly(maximal)
        elif minimal == 0:
            return AtMost(maximal)
        else:
            return super().__new__(cls)

    def __init__(self, minimal, maximal):
        super().__init__()
        self._minimal = minimal
        self._maximal = maximal

    def format_expected(self):
        return "to be called at least {} but no more than {}".\
            format(format_call_count(self._minimal), format_call_count(self._maximal))

    def is_satisfied(self):
        return self._minimal <= self._actual <= self._maximal
