import pytest

from mockify.cardinality import AtLeast, AtMost, Between, Exactly


class TestExactly:

    def test_do_not_allow_exact_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = Exactly(-1)
        assert str(excinfo.value) == "value of 'expected' must be >= 0"


class TestAtLeast:

    def test_do_not_allow_minimal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = AtLeast(-1)
        assert str(excinfo.value) == "value of 'minimal' must be >= 0"

    def test_when_created_with_zero_as_an_argument__then_expect_it_to_be_always_satisfied(self):
        uut = AtLeast(0)
        assert uut.format_expected() == "to be called zero or more times"
        assert uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()

    def test_when_created_with_three_as_an_argument__then_expect_it_to_be_updated_at_least_three_times(self):
        uut = AtLeast(3)
        assert uut.format_expected() == "to be called at least 3 times"
        assert not uut.is_satisfied()
        for _ in range(2):
            uut.update()
        assert not uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()


class TestAtMost:

    def test_do_not_allow_maximal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = AtMost(-1)
        assert str(excinfo.value) == "value of 'maximal' must be >= 0"

    def test_when_created_with_zero_as_an_argument__then_create_instance_of_exactly_object_instead(self):
        uut = AtMost(0)
        assert isinstance(uut, Exactly)
        assert uut.format_expected() == "to be never called"
        assert uut.is_satisfied()
        uut.update()
        assert not uut.is_satisfied()

    def test_when_created_with_one_as_an_argument__then_expect_it_to_be_updated_at_most_once(self):
        uut = AtMost(1)
        assert uut.format_expected() == "to be called at most once"
        assert uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert not uut.is_satisfied()

    def test_when_created_with_three_as_an_argument__then_expect_it_to_be_updated_at_most_three_times(self):
        uut = AtMost(3)
        assert uut.format_expected() == "to be called at most 3 times"
        for _ in range(3):
            uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert not uut.is_satisfied()


class TestBetween:

    def test_minimal_must_not_be_greater_than_maximal(self):
        with pytest.raises(TypeError) as excinfo:
            uut = Between(1, 0)
        assert str(excinfo.value) == "value of 'minimal' must not be greater than 'maximal'"

    def test_do_not_allow_minimal_count_less_than_zero(self):
        with pytest.raises(TypeError) as excinfo:
            uut = Between(-1, 0)
        assert str(excinfo.value) == "value of 'minimal' must be >= 0"

    def test_when_minimal_is_zero__then_create_instance_of_at_most_object_instead(self):
        uut = Between(0, 1)
        assert isinstance(uut, AtMost)
        assert uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert not uut.is_satisfied()

    def test_when_minimal_and_maximal_are_the_same__then_create_instance_of_exactly_object_instead(self):
        uut = Between(1, 1)
        assert isinstance(uut, Exactly)
        assert not uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()

    def test_when_minimal_is_once_and_maximal_is_twice__then_expect_it_to_be_updated_once_or_twice(self):
        uut = Between(1, 2)
        assert uut.format_expected() == "to be called at least once but no more than twice"
        assert not uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert not uut.is_satisfied()

    def test_when_minimal_is_once_and_maximal_is_three_times__then_expect_it_to_be_updated_at_least_once_and_at_most_three_times(self):
        uut = Between(1, 3)
        assert uut.format_expected() == "to be called at least once but no more than 3 times"
        assert not uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()
        for _ in range(2):
            uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert not uut.is_satisfied()

    def test_when_minimal_is_three_times_and_maximal_is_four_times__then_expect_it_to_be_updated_at_least_three_times_and_at_most_four_times(self):
        uut = Between(3, 4)
        assert uut.format_expected() == "to be called at least 3 times but no more than 4 times"
        assert not uut.is_satisfied()
        for _ in range(3):
            uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert uut.is_satisfied()
        uut.update()
        assert not uut.is_satisfied()
