from mockify import _utils


class TestMemoizedProperty:

    class Dummy:

        @_utils.memoized_property
        def foo(self) -> list:
            return []

    def test_getting_memoized_property_via_class_returns_property_object(self):
        assert isinstance(self.Dummy.foo, _utils.memoized_property)

    def test_getting_memoized_property_via_instance_always_returns_same_object(self):
        uut = self.Dummy()
        uut.foo.extend([1, 2, 3])
        assert uut.foo == [1, 2, 3]
        assert uut.foo is uut.foo
