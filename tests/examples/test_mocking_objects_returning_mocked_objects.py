import pytest

from mockify import satisfied
from mockify.mock import MockGroup
from mockify.actions import Return


class ItemRepositoryFacade:

    def __init__(self, connection):
        self._connection = connection

    def get_items(self):
        return self._connection.get('/api/items').json()


class TestItemRepositoryFacade:

    def test_invoke_get_items_api_call(self):
        expected_result = [{'id': 1, 'name': 'foo'}]

        group = MockGroup()
        connection = group.mock('connection')
        response = group.mock('response')
        connection.get.expect_call('/api/items').will_once(Return(response))
        response.json.expect_call().will_once(Return(expected_result))

        with satisfied(group):
            assert ItemRepositoryFacade(connection).get_items() == expected_result
