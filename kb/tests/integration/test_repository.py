"""Integration tests for the Repository layer against real (ephemeral) ChromaDB."""

from __future__ import annotations

import pytest

from kb.constants import COLLECTION_SOUNDS, COLLECTION_TEMPLATES
from kb.models import Sound, Template
from kb.store import Repository


def _sound(id: str, description: str) -> Sound:
    return Sound(
        id=id,
        description=description,
        local_path=f"/tmp/{id}.mp3",
        source_url=f"https://x.test/{id}",
        duration_sec=1.0,
        tags=["t1", "t2"],
        format="mp3",
        file_size_bytes=100,
    )


def _template(id: str, description: str) -> Template:
    return Template(
        id=id,
        description=description,
        local_path=f"/tmp/{id}.jpg",
        source_url=f"https://x.test/{id}",
        tags=["meme"],
        media_type="jpg",
        width=1000,
        height=1000,
        file_size_bytes=2000,
    )


class TestRepositorySounds:
    @pytest.mark.integration
    def test_add_and_query_returns_nearest(self, repo: Repository) -> None:
        repo.add_sound(_sound("a", "dramatic reveal dun dun dun"))
        repo.add_sound(_sound("b", "puppy barking"))
        repo.add_sound(_sound("c", "sad trombone wah wah"))
        results = repo.query(COLLECTION_SOUNDS, query_text="dramatic reveal dun dun dun", top_k=1)
        assert len(results) == 1
        assert results[0]["id"] == "a"

    @pytest.mark.integration
    def test_query_respects_top_k(self, repo: Repository) -> None:
        for i in range(5):
            repo.add_sound(_sound(f"s{i}", f"sound number {i}"))
        results = repo.query(COLLECTION_SOUNDS, query_text="number 2", top_k=3)
        assert len(results) == 3

    @pytest.mark.integration
    def test_delete_removes_entry(self, repo: Repository) -> None:
        repo.add_sound(_sound("a", "alpha"))
        repo.add_sound(_sound("b", "beta"))
        repo.delete(COLLECTION_SOUNDS, "a")
        ids = {r["id"] for r in repo.list_all(COLLECTION_SOUNDS, limit=100)}
        assert ids == {"b"}

    @pytest.mark.integration
    def test_reset_empties_collection(self, repo: Repository) -> None:
        repo.add_sound(_sound("a", "x"))
        repo.add_sound(_sound("b", "y"))
        repo.reset(COLLECTION_SOUNDS)
        assert repo.stats()[COLLECTION_SOUNDS] == 0

    @pytest.mark.integration
    def test_stats_counts(self, repo: Repository) -> None:
        repo.add_sound(_sound("a", "x"))
        repo.add_template(_template("t", "y"))
        stats = repo.stats()
        assert stats[COLLECTION_SOUNDS] == 1
        assert stats[COLLECTION_TEMPLATES] == 1

    @pytest.mark.integration
    def test_list_all_returns_metadata(self, repo: Repository) -> None:
        repo.add_sound(_sound("snd_a", "vine boom"))
        rows = repo.list_all(COLLECTION_SOUNDS, limit=10)
        assert len(rows) == 1
        assert rows[0]["id"] == "snd_a"
        assert rows[0]["description"] == "vine boom"
        assert rows[0]["metadata"]["local_path"] == "/tmp/snd_a.mp3"

    @pytest.mark.integration
    def test_add_duplicate_id_is_upsert(self, repo: Repository) -> None:
        repo.add_sound(_sound("a", "version one"))
        repo.add_sound(_sound("a", "version two"))
        rows = repo.list_all(COLLECTION_SOUNDS, limit=10)
        assert len(rows) == 1
        assert rows[0]["description"] == "version two"


class TestRepositoryTemplates:
    @pytest.mark.integration
    def test_add_template_and_query(self, repo: Repository) -> None:
        # FakeEmbedder is hash-based (not semantic), so query must be an exact document
        # match to be deterministically nearest. Real semantic ranking is covered in
        # the marked integration tests for SentenceTransformerEmbedder.
        drake_desc = "Drake prefers A rejects B format"
        repo.add_template(_template("drake", drake_desc))
        repo.add_template(_template("pooh", "fancy Pooh bear tuxedo meme"))
        results = repo.query(COLLECTION_TEMPLATES, query_text=drake_desc, top_k=1)
        assert results[0]["id"] == "drake"

    @pytest.mark.integration
    def test_unknown_collection_rejected(self, repo: Repository) -> None:
        with pytest.raises(ValueError):
            repo.query("nonexistent", query_text="x", top_k=1)
