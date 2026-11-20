"""Contract tests for `jsonview`: every accessor is total, and `true` is not an integer."""
from __future__ import annotations

import unittest

from lint_assessment import jsonview


class ObjectTest(unittest.TestCase):
    def test_as_object(self) -> None:
        self.assertEqual(jsonview.as_object({"a": 1}), {"a": 1})
        self.assertIsNone(jsonview.as_object([1]))
        self.assertIsNone(jsonview.as_object("x"))
        self.assertIsNone(jsonview.as_object(None))


class IntTest(unittest.TestCase):
    def test_booleans_are_not_integers(self) -> None:
        # a JSON `true` is not a count: choose_n: true must not pass as 1
        self.assertIsNone(jsonview.as_int(True))
        self.assertIsNone(jsonview.as_int(False))

    def test_ints_and_others(self) -> None:
        self.assertEqual(jsonview.as_int(3), 3)
        self.assertEqual(jsonview.as_int(0), 0)
        self.assertIsNone(jsonview.as_int(3.0))
        self.assertIsNone(jsonview.as_int("3"))


class GetTest(unittest.TestCase):
    def test_missing_and_wrong_typed_members(self) -> None:
        obj = {"s": "x", "n": 1, "l": [1], "o": {"k": 1}}
        self.assertEqual(jsonview.get_str(obj, "s"), "x")
        self.assertIsNone(jsonview.get_str(obj, "n"))
        self.assertIsNone(jsonview.get_str(obj, "absent"))
        self.assertEqual(jsonview.get_int(obj, "n"), 1)
        self.assertEqual(jsonview.get_array(obj, "l"), [1])
        self.assertIsNone(jsonview.get_array(obj, "s"))
        self.assertEqual(jsonview.get_object(obj, "o"), {"k": 1})
        self.assertIsNone(jsonview.get_object(obj, "l"))

    def test_get_is_total(self) -> None:
        self.assertIsNone(jsonview.get({}, "absent"))


class ObjectsTest(unittest.TestCase):
    def test_drops_non_objects_in_order(self) -> None:
        items: list[object] = [{"a": 1}, 5, {"b": 2}, None, [1]]
        # the array is `JsonArray` by contract; the cast is the test's, not the code's
        from typing import cast

        from lint_assessment.jsonview import JsonArray

        self.assertEqual(jsonview.objects(cast(JsonArray, items)), ({"a": 1}, {"b": 2}))


if __name__ == "__main__":
    unittest.main()
