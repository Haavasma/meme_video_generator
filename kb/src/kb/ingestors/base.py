"""Ingestor ABC + result record."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class IngestResult:
    """Lightweight summary for a single ingested entry."""

    entry_id: str
    collection: str
    description: str


class BaseIngestor(ABC):
    """Common interface for all ingestors. Concrete subclasses implement `ingest`."""

    @abstractmethod
    def ingest(self) -> list[IngestResult]: ...
