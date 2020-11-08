# ---------------------------------------------------------------------------
# mockify/core/_config.py
#
# Copyright (C) 2019 - 2020 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import abc
import collections


class Option(abc.ABC):

    def __init__(self, default=None):
        self.default = default

    @abc.abstractmethod
    def parse(self, key, value):
        pass

    @staticmethod
    def fail(key, message):
        raise ValueError(
            "Invalid value for {!r} config option given: {}".format(
                key, message
            )
        )


class Enum(Option):

    def __init__(self, values, **kwargs):
        super().__init__(**kwargs)
        self.values = tuple(values)

    def parse(self, key, value):
        if value not in self.values:
            self.fail(
                key,
                "expected any of {!r}, got {!r}".format(self.values, value)
            )
        return value


class Type(Option):

    def __init__(self, type_, **kwargs):
        super().__init__(**kwargs)
        self.type_ = type_

    def parse(self, key, value):
        if not isinstance(value, self.type_):
            self.fail(
                key,
                "expected instance of {!r}, got {!r}".format(self.type_, value)
            )
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
            raise TypeError("No such option: {}".format(key))
        self._options[key] = self._available_options[key].parse(key, value)

    def __getitem__(self, key):
        if key in self._options:
            return self._options[key]
        if key in self._available_options:
            return self._available_options[key].default
        raise KeyError(key)

    def __delitem__(self, key):
        del self._options[key]  # Will restore default
