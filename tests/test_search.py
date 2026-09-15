"""Tests for mcp_server/search.py's search_learnings(), the pure ranking
seam (spec 0002, issue #4). Fixture-based, no filesystem/MCP process
involved -- mirrors tests/test_reindex.py's style for build_index().
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mcp_server.search import search_learnings  # noqa: E402


def make_entry(*, id, date="2026-01-01", project="test-project", tags=None,
                type="specific", links=None, corroboration=0, superseded_by=None,
                embedding=None):
    return {
        "id": id,
        "file": f"learnings/{id}.md",
        "date": date,
        "project": project,
        "tags": tags if tags is not None else [],
        "type": type,
        "links": links if links is not None else [],
        "corroboration": corroboration,
        "superseded_by": superseded_by,
        "embedding": embedding,
    }


class SearchLearningsTests(unittest.TestCase):
    def test_exact_id_match_returned(self):
        entries = [
            make_entry(id="freeze-interface-before-parallel-porting"),
            make_entry(id="contract-before-parallelism"),
        ]

        results = search_learnings(entries, query="contract-before-parallelism")

        self.assertEqual([e["id"] for e in results], ["contract-before-parallelism"])

    def test_exact_id_match_ranks_above_substring_match(self):
        # "debugging" substring-matches the tag of both, but the id-exact
        # match should still win on total score even without tag overlap
        # driving it -- use an id that IS the query vs one that merely
        # contains it.
        entries = [
            make_entry(id="debugging-is-fun", tags=["debugging"]),
            make_entry(id="debugging", tags=["debugging"]),
        ]

        results = search_learnings(entries, query="debugging")

        self.assertEqual(results[0]["id"], "debugging")

    def test_substring_match(self):
        entries = [
            make_entry(id="check-environment-before-blaming-code"),
            make_entry(id="freeze-interface-contract-before-parallel-porting"),
        ]

        results = search_learnings(entries, query="environment")

        self.assertEqual([e["id"] for e in results], ["check-environment-before-blaming-code"])

    def test_tag_filter(self):
        entries = [
            make_entry(id="a", tags=["debugging", "provenance"]),
            make_entry(id="b", tags=["principle"]),
        ]

        results = search_learnings(entries, tags=["provenance"])

        self.assertEqual([e["id"] for e in results], ["a"])

    def test_unrecognized_tag_returns_zero_matches_not_error(self):
        entries = [make_entry(id="a", tags=["debugging"])]

        results = search_learnings(entries, tags=["not-a-real-tag"])

        self.assertEqual(results, [])

    def test_project_filter(self):
        entries = [
            make_entry(id="a", project="pdf-ingestion-migration"),
            make_entry(id="b", project="other-project"),
        ]

        results = search_learnings(entries, project="pdf-ingestion-migration")

        self.assertEqual([e["id"] for e in results], ["a"])

    def test_corroboration_boosts_entry_above_another(self):
        entries = [
            make_entry(id="a", tags=["principle"], corroboration=0),
            make_entry(id="b", tags=["principle"], corroboration=5),
        ]

        results = search_learnings(entries, tags=["principle"])

        self.assertEqual([e["id"] for e in results], ["b", "a"])

    def test_superseded_entry_ranks_below_replacement(self):
        entries = [
            make_entry(id="old-a", tags=["debugging"], superseded_by="new-a"),
            make_entry(id="new-a", tags=["debugging"]),
        ]

        results = search_learnings(entries, tags=["debugging"])

        self.assertEqual([e["id"] for e in results], ["new-a", "old-a"])

    def test_superseded_entry_never_hidden(self):
        entries = [make_entry(id="old-a", tags=["debugging"], superseded_by="new-a")]

        results = search_learnings(entries, tags=["debugging"])

        self.assertEqual([e["id"] for e in results], ["old-a"])

    def test_result_includes_all_index_fields(self):
        entries = [make_entry(id="a", project="p", tags=["git"], corroboration=2)]

        results = search_learnings(entries, query="a")

        self.assertEqual(results[0].keys(), entries[0].keys())
        self.assertEqual(results[0]["file"], "learnings/a.md")

    def test_no_filters_returns_all_entries(self):
        entries = [make_entry(id="a"), make_entry(id="b")]

        results = search_learnings(entries)

        self.assertEqual({e["id"] for e in results}, {"a", "b"})


if __name__ == "__main__":
    unittest.main()
