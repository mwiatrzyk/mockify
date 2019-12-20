from io import BytesIO

from mockify import satisfied
from mockify.mock import Mock
from mockify.actions import Invoke
from mockify.matchers import _


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
    image = Mock('image')
    image.save.expect_call(_).will_once(Invoke(write, b'image data'))

    uut = ImageAdapter(image)

    with satisfied(image):
        assert uut.get_payload() == b'image data'
