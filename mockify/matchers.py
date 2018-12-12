# ---------------------------------------------------------------------------
# mockify/matchers.py
#
# Copyright (C) 2018 Maciej Wiatrzyk
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE.txt for details.
# ---------------------------------------------------------------------------


class Any:

    def __repr__(self):
        return "_"

    def __eq__(self, other):
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


_ = Any()
