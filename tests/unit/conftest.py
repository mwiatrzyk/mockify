import pytest


@pytest.fixture
def assert_that():
    """A placeholder for common helper assertions."""

    class AssertThat:

        def object_attr_match(self, obj, **attrs):
            for name, expected_value in attrs.items():
                assert getattr(obj, name) == expected_value

    return AssertThat()
