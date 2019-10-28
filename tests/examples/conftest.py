import pytest

from mockify import MockFactory


@pytest.fixture
def mock_factory():
    factory = MockFactory()
    yield factory
    factory.done()
