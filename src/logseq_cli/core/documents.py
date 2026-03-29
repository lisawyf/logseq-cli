from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Iterator, Literal

from logseq_cli.core.models import Document
from logseq_cli.core.pages import build_document

SUPPORTED_EXTENSIONS = (".md", ".org")


def iter_document_paths(directory: Path) -> Iterator[Path]:
    """Yield supported documents from a graph directory in stable order."""

    if not directory.exists():
        return
    for path in sorted(directory.rglob("*")):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def load_document(path: Path, kind: Literal["page", "journal"]) -> Document:
    return build_document(path, kind)


def journal_filename(day: date, suffix: str = ".md") -> str:
    """Return the standard Logseq journal filename for a date."""

    return day.strftime("%Y_%m_%d") + suffix


def journal_title_from_path(path: Path) -> str:
    stem = path.stem
    try:
        return date.fromisoformat(stem.replace("_", "-")).isoformat()
    except ValueError:
        return stem
