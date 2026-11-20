"""Contract tests for `rationals` (§2.3.1)."""
from __future__ import annotations

import unittest
from fractions import Fraction

from lint_assessment import rationals


class ParseTest(unittest.TestCase):
    def test_accepts_canonical_forms(self) -> None:
        self.assertEqual(rationals.parse("0"), Fraction(0))
        self.assertEqual(rationals.parse("5"), Fraction(5))
        self.assertEqual(rationals.parse("19/4"), Fraction(19, 4))
        self.assertEqual(rationals.parse("2/3"), Fraction(2, 3))

    def test_rejects_non_canonical_forms(self) -> None:
        for text in ("5/1", "2/4", "05", "4.5", "", "1/0", "-3", " 5", "5/2/1"):
            with self.subTest(text=text):
                self.assertIsNone(rationals.parse(text))


class FormatTest(unittest.TestCase):
    def test_formats_exactly(self) -> None:
        self.assertEqual(rationals.format(Fraction(0)), "0")
        self.assertEqual(rationals.format(Fraction(6, 2)), "3")
        self.assertEqual(rationals.format(Fraction(9, 2)), "9/2")
        self.assertEqual(rationals.format(Fraction(19, 4)), "19/4")

    def test_round_trips(self) -> None:
        for text in ("0", "1", "7", "1/2", "9/2", "19/4"):
            with self.subTest(text=text):
                value = rationals.parse(text)
                if value is None:
                    self.fail(f"parse rejected the canonical form {text!r}")
                self.assertEqual(rationals.format(value), text)


class CanonicalityTest(unittest.TestCase):
    def test_agrees_with_parse(self) -> None:
        # a pure pattern match cannot decide lowest terms, so the two must agree
        for text in ("5", "5/1", "2/4", "1/3", "0", "10"):
            with self.subTest(text=text):
                self.assertEqual(rationals.is_canonical(text), rationals.parse(text) is not None)


class ParseManyTest(unittest.TestCase):
    def test_all_or_nothing(self) -> None:
        self.assertEqual(rationals.parse_many(["5", "2"]), (Fraction(5), Fraction(2)))
        self.assertIsNone(rationals.parse_many(["5", "2/4"]))


if __name__ == "__main__":
    unittest.main()
