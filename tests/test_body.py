"""Tests for mcp_server/body.py's attach_bodies() -- the IO seam that reads
each search result's full file content, so search_learnings callers get the
actual Why/How-to-apply text instead of having to Read the file themselves
as a second, easy-to-skip step.

Uses real files in a tmp dir (mirrors test_writer.py's style), since this
function's whole job is filesystem IO -- unlike search.py's pure ranking,
there's no meaningful fixture-only version of it.
"""
import sys
import unittest
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcp_server.body import attach_bodies  # noqa: E402
from tests.test_reindex import write_learning  # noqa: E402


class AttachBodiesTests(unittest.TestCase):
    def test_attaches_body_content_for_each_result(self):
        with TemporaryDirectory() as tmp:
            repo_path = Path(tmp)
            (repo_path / "learnings").mkdir()
            write_learning(repo_path / "learnings", "a.md", id="a", body="Full body of a.")

            results = attach_bodies([{"id": "a", "file": "learnings/a.md"}], repo_path)

            self.assertEqual(results[0]["body"], "Full body of a.")

    def test_does_not_mutate_input_results(self):
        with TemporaryDirectory() as tmp:
            repo_path = Path(tmp)
            (repo_path / "learnings").mkdir()
            write_learning(repo_path / "learnings", "a.md", id="a", body="Body.")
            original = {"id": "a", "file": "learnings/a.md"}

            attach_bodies([original], repo_path)

            self.assertNotIn("body", original)

    def test_preserves_original_field_order_and_values(self):
        with TemporaryDirectory() as tmp:
            repo_path = Path(tmp)
            (repo_path / "learnings").mkdir()
            write_learning(repo_path / "learnings", "a.md", id="a", body="Body.")

            results = attach_bodies(
                [{"id": "a", "file": "learnings/a.md", "tags": ["debugging"]}], repo_path
            )

            self.assertEqual(results[0]["id"], "a")
            self.assertEqual(results[0]["tags"], ["debugging"])

    def test_attaches_body_for_multiple_results_independently(self):
        with TemporaryDirectory() as tmp:
            repo_path = Path(tmp)
            (repo_path / "learnings").mkdir()
            write_learning(repo_path / "learnings", "a.md", id="a", body="Body A.")
            write_learning(repo_path / "learnings", "b.md", id="b", body="Body B.")

            results = attach_bodies(
                [
                    {"id": "a", "file": "learnings/a.md"},
                    {"id": "b", "file": "learnings/b.md"},
                ],
                repo_path,
            )

            self.assertEqual(results[0]["body"], "Body A.")
            self.assertEqual(results[1]["body"], "Body B.")

    def test_empty_results_returns_empty(self):
        with TemporaryDirectory() as tmp:
            self.assertEqual(attach_bodies([], Path(tmp)), [])

    def test_missing_file_is_skipped_with_warning_not_raised(self):
        with TemporaryDirectory() as tmp:
            repo_path = Path(tmp)
            (repo_path / "learnings").mkdir()
            write_learning(repo_path / "learnings", "a.md", id="a", body="Body A.")

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                results = attach_bodies(
                    [
                        {"id": "a", "file": "learnings/a.md"},
                        {"id": "missing", "file": "learnings/missing.md"},
                    ],
                    repo_path,
                )

            self.assertEqual([r["id"] for r in results], ["a"])
            self.assertTrue(any("missing.md" in str(w.message) for w in caught))

    def test_malformed_frontmatter_is_skipped_with_warning_not_raised(self):
        with TemporaryDirectory() as tmp:
            repo_path = Path(tmp)
            (repo_path / "learnings").mkdir()
            (repo_path / "learnings" / "broken.md").write_text("No frontmatter here.\n")

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                results = attach_bodies(
                    [{"id": "broken", "file": "learnings/broken.md"}], repo_path
                )

            self.assertEqual(results, [])
            self.assertTrue(any("broken.md" in str(w.message) for w in caught))


if __name__ == "__main__":
    unittest.main()
