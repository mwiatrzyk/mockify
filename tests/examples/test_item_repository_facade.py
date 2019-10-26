import pytest

from mockify import satisfies, mock
from mockify.actions import Return


class ItemRepositoryFacade:

    def __init__(self, connection):
        self._connection = connection

    def get_items(self):
        return self._connection.get('/api/items').json()


class TestItemRepositoryFacade:

    def test_invoke_get_items_api_call(self):
        expected_result = [{'id': 1, 'name': 'foo'}]

        connection = mock.Mock('connection')
        response = mock.Mock('response')
        connection.get.expect_call('/api/items').will_once(Return(response))
        response.json.expect_call().will_once(Return(expected_result))

        with satisfies(connection, response):
            assert ItemRepositoryFacade(connection).get_items() == expected_result
