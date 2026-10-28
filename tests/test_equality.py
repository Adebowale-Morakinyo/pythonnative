"""Tests for the snapshot equality rule in pythonnative.equality."""

from __future__ import annotations

from pythonnative.equality import equal


def test_equal_returns_bool_for_equal_and_unequal_values() -> None:
    assert equal(1, 1) is True
    assert equal(1, 2) is False
    assert equal([1, {"a": 2}], [1, {"a": 2}]) is True
    assert equal({"a": [1]}, {"a": [2]}) is False


def test_equal_same_object_does_not_call_eq() -> None:
    class ExplodingEq:
        def __eq__(self, other: object) -> bool:
            raise AssertionError("__eq__ should not be called")

    value = ExplodingEq()

    assert equal(value, value) is True


def test_equal_returns_false_when_comparison_raises() -> None:
    class ExplodingEq:
        def __eq__(self, other: object) -> bool:
            raise RuntimeError("comparison failed")

    left = ExplodingEq()
    right = ExplodingEq()

    assert equal(left, right) is False


def test_equal_returns_false_for_nonboolean_comparison_result() -> None:
    class ComparisonResult:
        def __bool__(self) -> bool:
            raise AssertionError("__bool__ should not be called")

    class ReturnsNonBool:
        def __eq__(self, other: object) -> ComparisonResult:  # type: ignore[override]
            return ComparisonResult()

    left = ReturnsNonBool()
    right = ReturnsNonBool()

    assert equal(left, right) is False


def test_equal_does_not_treat_truthy_nonbool_as_true() -> None:
    class ReturnsOne:
        def __eq__(self, other: object) -> int:  # type: ignore[override]
            return 1

    left = ReturnsOne()
    right = ReturnsOne()

    assert equal(left, right) is False


def test_equal_same_mutable_object_after_in_place_mutation() -> None:
    value: list[str] = []

    value.append("changed")

    assert equal(value, value) is True
