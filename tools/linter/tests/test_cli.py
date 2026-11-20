"""Contract tests for the command-line boundary: exit status and output shape."""
from __future__ import annotations

import io
import json
import os
import shutil
import tempfile
import unittest

from lint_assessment import cli
from lint_assessment.spec import latest_spec

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def fixture(name: str) -> str:
    return os.path.join(FIXTURES, name)


class ParseArgsTest(unittest.TestCase):
    def test_bundle_only(self) -> None:
        self.assertEqual(
            cli.parse_args(["b.json"]),
            {"bundle": "b.json", "submission": None,
             "spec": cli.DEFAULT_SPEC,
             "submission_spec": cli.DEFAULT_SUBMISSION_SPEC, "json": False},
        )

    def test_a_submission_is_usable_on_its_own(self) -> None:
        # 0.12.0 folded the grading record into the submission: no second document to name
        options = cli.parse_args(["b.json", "--submission", "s.json"])
        self.assertIsNotNone(options)
        assert options is not None
        self.assertEqual(options["submission"], "s.json")

    def test_report_is_not_an_option(self) -> None:
        self.assertIsNone(cli.parse_args(["b.json", "--report", "r.json"]))

    def test_unknown_option_is_unusable(self) -> None:
        self.assertIsNone(cli.parse_args(["b.json", "--nope"]))

    def test_two_positionals_are_unusable(self) -> None:
        self.assertIsNone(cli.parse_args(["b.json", "c.json"]))


class MainTest(unittest.TestCase):
    def test_golden_pair_exits_zero(self) -> None:
        self.assertEqual(
            cli.main([fixture("bundle.json"), "--submission", fixture("submission.json")]),
            0,
        )

    def test_naming_a_report_exits_two_with_a_reason(self) -> None:
        # the flag was removed, not silently ignored: a 0.11.3 habit must fail loudly
        self.assertEqual(
            cli.main([fixture("bundle.json"), "--submission", fixture("submission.json"),
                      "--report", fixture("report.json")]),
            2,
        )

    def test_the_default_spec_is_the_newest_one(self) -> None:
        # the CLI resolves the spec by version; a pinned filename goes stale on every bump
        design = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.assertEqual(cli.DEFAULT_SPEC, latest_spec(design))
        self.assertTrue(cli.DEFAULT_SPEC.endswith(".md"))

    def test_unreadable_file_exits_two(self) -> None:
        self.assertEqual(cli.main([fixture("no-such-file.json")]), 2)

    def test_invalid_json_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "broken.json")
            io.open(path, "w", encoding="utf-8").write("{not json")
            self.assertEqual(cli.main([path]), 2)

    def test_a_defect_exits_one_and_json_output_parses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = json.load(io.open(fixture("bundle.json"), encoding="utf-8"))
            bundle["assessment"]["sections"][0]["questions"][0]["credit"] = "capped"
            path = os.path.join(tmp, "bundle.json")
            io.open(path, "w", encoding="utf-8").write(json.dumps(bundle))
            self.assertEqual(cli.main([path]), 1)
            self.assertEqual(cli.main([path, "--json"]), 1)
            self.assertEqual(cli.format_text(()), "")


if __name__ == "__main__":
    unittest.main()
