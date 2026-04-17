"""Asset ingestors — read from a source, build a KB record, upsert via Repository."""

from kb.ingestors.base import BaseIngestor, IngestResult
from kb.ingestors.imgflip import ImgflipIngestor
from kb.ingestors.local_files import LocalFileIngestor
from kb.ingestors.myinstants import MyInstantsIngestor

__all__ = [
    "BaseIngestor",
    "ImgflipIngestor",
    "IngestResult",
    "LocalFileIngestor",
    "MyInstantsIngestor",
]
