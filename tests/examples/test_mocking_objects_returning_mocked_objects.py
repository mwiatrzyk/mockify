# ---------------------------------------------------------------------------
# tests/examples/test_mocking_objects_returning_mocked_objects.py
#
# Copyright (C) 2019 - 2021 Maciej Wiatrzyk <maciej.wiatrzyk@gmail.com>
#
# This file is part of Mockify library and is released under the terms of the
# MIT license: http://opensource.org/licenses/mit-license.php.
#
# See LICENSE for details.
# ---------------------------------------------------------------------------

from mockify.actions import Return
from mockify.core import satisfied
from mockify.mock import MockFactory


class ItemRepositoryFacade:

    def __init__(self, connection):
        self._connection = connection

    def get_items(self):
        return self._connection.get("/api/items").json()


class TestItemRepositoryFacade:

    def test_invoke_get_items_api_call(self):
        expected_result = [{"id": 1, "name": "foo"}]

        factory = MockFactory()
        connection = factory.mock("connection")
        response = factory.mock("response")
        connection.get.expect_call("/api/items").will_once(Return(response))
        response.json.expect_call().will_once(Return(expected_result))

        with satisfied(factory):
            assert ItemRepositoryFacade(connection).get_items() == expected_result
