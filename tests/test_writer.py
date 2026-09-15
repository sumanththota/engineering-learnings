"""Tests for mcp_server/writer.py's add_learning(), the pure seam add_learning tests at.

No filesystem/git side effects beyond a tmp dir: every test writes into a
fresh TemporaryDirectory standing in for learnings/.
"""
import sys
import unittest
import warnings
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcp_server.writer import add_learning  # noqa: E402
from scripts import reindex  # noqa: E402
from tests.test_reindex import write_learning  # noqa: E402


class AddLearningTests(unittest.TestCase):
    def test_valid_write(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)

            path = add_learning(
                learnings_dir,
                id="new-learning",
                date="2026-09-15",
                project="widget-service",
                tags=["debugging"],
                type="specific",
                links=[],
                body="## Context\n\nSomething happened.\n",
            )

            self.assertEqual(path, learnings_dir / "new-learning.md")
            self.assertTrue(path.exists())
            text = path.read_text()
            self.assertIn("id: new-learning", text)
            self.assertIn("tags: [debugging]", text)
            self.assertNotIn("confidence", text)
            self.assertIn("Something happened.", text)

    def test_collision_on_existing_id_fails_and_does_not_overwrite(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "existing-id.md", id="existing-id", body="original body")
            original_text = (learnings_dir / "existing-id.md").read_text()

            with self.assertRaises(FileExistsError):
                add_learning(
                    learnings_dir,
                    id="existing-id",
                    date="2026-09-15",
                    project="p",
                    tags=[],
                    type="specific",
                    links=[],
                    body="overwritten body",
                )

            # The existing file must be untouched -- collision must fail before
            # any write, never truncate-then-fail.
            self.assertEqual((learnings_dir / "existing-id.md").read_text(), original_text)
            self.assertNotIn("overwritten body", (learnings_dir / "existing-id.md").read_text())

    def test_dangling_link_fails_and_does_not_write(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)

            with self.assertRaises(reindex.DanglingLinkError) as ctx:
                add_learning(
                    learnings_dir,
                    id="new-learning",
                    date="2026-09-15",
                    project="p",
                    tags=[],
                    type="specific",
                    links=["does-not-exist"],
                    body="Body.",
                )

            self.assertIn("does-not-exist", str(ctx.exception))
            self.assertFalse((learnings_dir / "new-learning.md").exists())

    def test_links_to_existing_corpus_entry_succeeds(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "principle.md", id="shared-principle", type="principle")

            path = add_learning(
                learnings_dir,
                id="new-specific",
                date="2026-09-15",
                project="p",
                tags=[],
                type="specific",
                links=["shared-principle"],
                body="Body.",
            )

            self.assertTrue(path.exists())

    def test_principle_and_specific_share_required_fields(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)

            for kind in ("specific", "principle"):
                path = add_learning(
                    learnings_dir,
                    id=f"a-{kind}",
                    date="2026-09-15",
                    project="p",
                    tags=[],
                    type=kind,
                    links=[],
                    body="Body.",
                )
                self.assertTrue(path.exists())

    def test_unrecognized_tag_warns_but_succeeds(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)

            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                path = add_learning(
                    learnings_dir,
                    id="new-learning",
                    date="2026-09-15",
                    project="p",
                    tags=["concurrency"],  # not in reindex.CANONICAL_TAGS
                    type="specific",
                    links=[],
                    body="Body.",
                )

            self.assertTrue(path.exists())
            self.assertTrue(any("concurrency" in str(w.message) for w in caught))

    def test_round_trip_through_reindex_parser(self):
        """Write via add_learning, then confirm reindex.py's own parser reads
        it back with matching fields -- the two must never diverge on shape."""
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)

            add_learning(
                learnings_dir,
                id="round-trip-id",
                date="2026-09-15",
                project="widget-service",
                tags=["testing", "verification"],
                type="principle",
                links=[],
                body="## Learning\n\nRound-trips cleanly.\n",
            )

            parsed, warns = reindex.parse_learnings(learnings_dir)
            self.assertEqual(warns, [])
            self.assertEqual(len(parsed), 1)
            path, fields = parsed[0]
            self.assertEqual(fields["id"], "round-trip-id")
            self.assertEqual(fields["date"], "2026-09-15")
            self.assertEqual(fields["project"], "widget-service")
            self.assertEqual(fields["tags"], ["testing", "verification"])
            self.assertEqual(fields["type"], "principle")
            self.assertEqual(fields["links"], [])
            self.assertNotIn("confidence", fields)

            # And build_index (the full pipeline) accepts it without error.
            entries, build_warnings = reindex.build_index(learnings_dir)
            self.assertEqual(build_warnings, [])
            self.assertEqual(entries[0]["id"], "round-trip-id")


if __name__ == "__main__":
    unittest.main()
