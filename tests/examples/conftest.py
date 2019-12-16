import pytest

from mockify import Session
from mockify.mock import MockFactory


@pytest.fixture
def mock_session():
    session = Session()
    yield session
    session.done()


@pytest.fixture
def mock_factory(mock_session):
    return MockFactory(mock_session)
