class Base:

    def __init__(self):
        self._actual = 0

    def format_actual(self):
        if self._actual == 0:
            return "never called"
        elif self._actual == 1:
            return "called once"
        elif self._actual == 2:
            return "called twice"
        else:
            return "called {} times".format(self._actual)

    def update(self):
        self._actual += 1


class Exactly(Base):

    def __init__(self, expected):
        super().__init__()
        self._expected = expected

    def format_expected(self):
        if self._expected == 0:
            return "to be never called"
        elif self._expected == 1:
            return "to be called once"
        elif self._expected == 2:
            return  "to be called twice"
        else:
            return "to be called {} times".format(self._expected)

    def is_satisfied(self):
        return self._expected == self._actual


class AtLeast(Base):

    def __init__(self, minimal):
        super().__init__()
        self._minimal = minimal

    def format_expected(self):
        if self._minimal == 1:
            return "to be called at least once"
        else:
            return "to be called at least twice"

    def is_satisfied(self):
        return self._minimal <= self._actual


class AtMost(Base):

    def __init__(self, maximal):
        super().__init__()
        self._maximal = maximal

    def format_expected(self):
        return "to be called at most twice"

    def is_satisfied(self):
        return self._maximal >= self._actual


class Between(Base):

    def __init__(self, minimal, maximal):
        super().__init__()
        self._minimal = minimal
        self._maximal = maximal

    def format_expected(self):
        return "to be called at least twice but no more than 3 times"

    def is_satisfied(self):
        return self._minimal <= self._actual <= self._maximal
