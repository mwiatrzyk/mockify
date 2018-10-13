from mockify.core.mock import MockCall


class TestMockCall:

    def test_string_representation_of_mock_call_with_neither_args_nor_kwargs(self):
        uut = MockCall("foo", tuple(), {})
        assert str(uut) == "foo()"

    def test_string_representation_of_mock_call_with_args_only(self):
        uut = MockCall("foo", (1, 2, "spam"), {})
        assert str(uut) == "foo(1, 2, 'spam')"

    def test_string_representation_of_mock_call_with_args_and_kwargs(self):
        uut = MockCall("foo", (1, 2), {'a': 'spam', 'b': 123})
        assert str(uut) == "foo(1, 2, a='spam', b=123)"
