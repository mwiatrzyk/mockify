class Base:

    def __init__(self, expected):
        self._expected = expected


class Exactly(Base):

    def __str__(self):
        if self._expected == 0:
            return "to be never called"
        elif self._expected == 1:
            return "to be called once"
        elif self._expected == 2:
            return  "to be called twice"
        else:
            return "to be called {} times".format(self._expected)

    def _satisfies_actual(self, actual):
        return self._expected == actual


class AtLeast(Base):

    def __str__(self):
        return "to be called at least twice"

    def _satisfies_actual(self, actual):
        return actual >= self._expected


class AtMost(Base):

    def __str__(self):
        return "to be called at most twice"

    def _satisfies_actual(self, actual):
        return actual <= self._expected


class Between:

    def __init__(self, min_expected, max_allowed):
        self._min_expected = min_expected
        self._max_allowed = max_allowed

    def __str__(self):
        return "to be called at least twice but no more than 3 times"

    def _satisfies_actual(self, actual):
        return self._min_expected <= actual <= self._max_allowed
