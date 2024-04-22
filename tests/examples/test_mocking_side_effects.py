# ---------------------------------------------------------------------------
# tests/examples/test_mocking_side_effects.py
#
# Copyright (C) 2019 - 2024 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------
from io import BytesIO

from mockify.actions import Invoke
from mockify.core import satisfied
from mockify.matchers import _
from mockify.mock import Mock


class ImageAdapter:

    def __init__(self, image):
        self._image = image

    def get_payload(self):
        fd = BytesIO()
        self._image.save(fd)
        return fd.getvalue()


def write(payload, fd):
    fd.write(payload)


def test_get_payload():
    image = Mock("image")
    image.save.expect_call(_).will_once(Invoke(write, b"image data"))

    uut = ImageAdapter(image)

    with satisfied(image):
        assert uut.get_payload() == b"image data"
