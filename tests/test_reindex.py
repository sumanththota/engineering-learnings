"""Tests for scripts/reindex.py's build_index(), the pure seam this rewrite is tested at.

No filesystem/git side effects: every test builds its corpus in a tmp dir.
"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import reindex  # noqa: E402


def write_learning(learnings_dir, filename, *, id, date="2026-01-01", project="test-project",
                    tags=None, type="specific", links=None, superseded_by=None, body="Body."):
    tags = tags if tags is not None else []
    links = links if links is not None else []
    lines = [
        "---",
        f"id: {id}",
        f"date: {date}",
        f"project: {project}",
        f"tags: [{', '.join(tags)}]",
        f"type: {type}",
        f"links: [{', '.join(links)}]",
    ]
    if superseded_by is not None:
        lines.append(f"superseded_by: {superseded_by}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    (learnings_dir / filename).write_text("\n".join(lines) + "\n")


def entries_by_id(entries):
    return {e["id"]: e for e in entries}


class BuildIndexTests(unittest.TestCase):
    def test_valid_linked_pair(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "a.md", id="specific-a", type="specific", links=["principle-a"])
            write_learning(learnings_dir, "b.md", id="principle-a", type="principle", links=[])

            entries, warnings = reindex.build_index(learnings_dir)

            self.assertEqual(warnings, [])
            by_id = entries_by_id(entries)
            self.assertEqual(set(by_id), {"specific-a", "principle-a"})
            self.assertEqual(by_id["specific-a"]["links"], ["principle-a"])

    def test_dangling_link_raises(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "a.md", id="specific-a", links=["does-not-exist"])

            with self.assertRaises(reindex.DanglingLinkError) as ctx:
                reindex.build_index(learnings_dir)

            self.assertIn("a.md", str(ctx.exception))
            self.assertIn("does-not-exist", str(ctx.exception))

    def test_unrecognized_tag_warns_not_fails(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "a.md", id="specific-a", tags=["concurrency"])

            entries, warnings = reindex.build_index(learnings_dir)

            self.assertEqual(len(entries), 1)
            self.assertTrue(any("concurrency" in w and "a.md" in w for w in warnings))

    def test_corroboration_two_specifics_one_principle(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "a.md", id="specific-a", links=["shared-principle"])
            write_learning(learnings_dir, "b.md", id="specific-b", links=["shared-principle"])
            write_learning(learnings_dir, "c.md", id="shared-principle", type="principle", links=[])

            entries, warnings = reindex.build_index(learnings_dir)

            self.assertEqual(warnings, [])
            by_id = entries_by_id(entries)
            self.assertEqual(by_id["shared-principle"]["corroboration"], 2)
            self.assertEqual(by_id["specific-a"]["corroboration"], 0)

    def test_superseded_by_passthrough(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "a.md", id="old-a", superseded_by="new-a")
            write_learning(learnings_dir, "b.md", id="new-a")

            entries, warnings = reindex.build_index(learnings_dir)

            by_id = entries_by_id(entries)
            self.assertEqual(by_id["old-a"]["superseded_by"], "new-a")
            self.assertIsNone(by_id["new-a"]["superseded_by"])

    def test_missing_required_field_warns(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            (learnings_dir / "a.md").write_text(
                "---\nid: specific-a\ntags: []\nlinks: []\n---\n\nBody.\n"
            )

            entries, warnings = reindex.build_index(learnings_dir)

            self.assertEqual(len(entries), 1)
            self.assertTrue(any("a.md" in w and "missing" in w for w in warnings))

    def test_confidence_field_absent_from_output(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "a.md", id="specific-a")

            entries, _ = reindex.build_index(learnings_dir)

            self.assertNotIn("confidence", entries[0])
            self.assertIn("corroboration", entries[0])

    def test_self_link_does_not_inflate_own_corroboration(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            write_learning(learnings_dir, "a.md", id="specific-a", links=["specific-a"])

            entries, _ = reindex.build_index(learnings_dir)

            self.assertEqual(entries[0]["corroboration"], 0)

    def test_read_body_strips_frontmatter(self):
        text = "---\nid: specific-a\ntags: []\nlinks: []\n---\n\nActual body text.\n"

        self.assertEqual(reindex.read_body(text), "Actual body text.")

    def test_read_body_raises_on_missing_frontmatter(self):
        with self.assertRaises(ValueError):
            reindex.read_body("No frontmatter here, just body text.\n")

    def test_read_body_preserves_internal_markdown_structure(self):
        text = (
            "---\nid: specific-a\ntags: []\nlinks: []\n---\n\n"
            "## Heading\n\nFirst paragraph.\n\nSecond paragraph.\n"
        )

        self.assertEqual(
            reindex.read_body(text),
            "## Heading\n\nFirst paragraph.\n\nSecond paragraph.",
        )

    def test_missing_field_warning_preserved_on_dangling_link_failure(self):
        with TemporaryDirectory() as tmp:
            learnings_dir = Path(tmp)
            (learnings_dir / "a.md").write_text(
                "---\nid: specific-a\ntags: []\nlinks: [does-not-exist]\n---\n\nBody.\n"
            )

            with self.assertRaises(reindex.DanglingLinkError) as ctx:
                reindex.build_index(learnings_dir)

            self.assertTrue(any("a.md" in w and "missing" in w for w in ctx.exception.warnings))


if __name__ == "__main__":
    unittest.main()
