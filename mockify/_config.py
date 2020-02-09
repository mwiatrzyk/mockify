import abc
import collections


class Option(abc.ABC):

    def __init__(self, default=None):
        self.default = default

    @abc.abstractmethod
    def parse(self, value):
        return value

    def fail(self, key, message):
        raise ValueError(f"Invalid value for {key!r} config option given: {message}")


class Enum(Option):

    def __init__(self, values, **kwargs):
        super().__init__(**kwargs)
        self.values = tuple(values)

    def parse(self, key, value):
        if value not in self.values:
            self.fail(key, f"expected any of {self.values!r}, got {value!r}")
        return value


class Type(Option):

    def __init__(self, type_, **kwargs):
        super().__init__(**kwargs)
        self.type_ = type_

    def parse(self, key, value):
        if not isinstance(value, self.type_):
            self.fail(key, f"expected instance of {self.type_!r}, got {value!r}")
        return value


class Config(collections.abc.MutableMapping):

    def __init__(self, available_options):
        self._available_options = available_options
        self._options = {}

    def __iter__(self):
        return iter(self._available_options.keys())

    def __len__(self):
        return len(self._available_options)

    def __setitem__(self, key, value):
        if key not in self._available_options:
            raise TypeError(f"No such option: {key}")
        else:
            self._options[key] = self._available_options[key].parse(key, value)

    def __getitem__(self, key):
        if key in self._options:
            return self._options[key]
        elif key in self._available_options:
            return self._available_options[key].default
        else:
            raise KeyError(key)

    def __delitem__(self, key):
        del self._options[key]  # Will restore default
