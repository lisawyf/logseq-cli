from __future__ import annotations

from datetime import date
from pathlib import Path
import tempfile

from logseq_cli.core.errors import ExitCodes, LogseqCliError
from logseq_cli.core.models import Document, Graph
from logseq_cli.core.pages import build_document


def journal_filename(target_date: date, suffix: str = ".md") -> str:
    return f"{target_date.strftime('%Y_%m_%d')}{suffix}"


def parse_target_date(*, target_date: str | None, today: bool) -> date:
    if today and target_date:
        raise LogseqCliError(
            code="INVALID_DATE_OPTIONS",
            message="Use either --today or --date, not both.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )
    if today:
        return date.today()
    if target_date:
        try:
            return date.fromisoformat(target_date)
        except ValueError as exc:
            raise LogseqCliError(
                code="INVALID_DATE",
                message=f"Invalid date '{target_date}'. Use YYYY-MM-DD.",
                exit_code=ExitCodes.INVALID_ARGUMENTS,
            ) from exc
    return date.today()


def resolve_journal_path(graph: Graph, journal_date: date) -> Path | None:
    for suffix in (".md", ".org"):
        path = graph.journals_dir / journal_filename(journal_date, suffix)
        if path.exists():
            return path
    return None


def read_journal(graph: Graph, journal_date: date) -> Document:
    path = resolve_journal_path(graph, journal_date)
    if path is None:
        raise LogseqCliError(
            code="PAGE_NOT_FOUND",
            message=f"Journal '{journal_date.isoformat()}' not found",
            exit_code=ExitCodes.PAGE_NOT_FOUND,
        )

    document = build_document(path, "journal")
    document.is_journal = True
    document.journal_date = journal_date
    return document


def append_to_journal(
    graph: Graph,
    journal_date: date,
    text: str,
    *,
    dry_run: bool = False,
) -> dict[str, object]:
    if not text.strip():
        raise LogseqCliError(
            code="EMPTY_TEXT",
            message="--text must not be empty.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )

    graph.journals_dir.mkdir(parents=True, exist_ok=True)
    path = resolve_journal_path(graph, journal_date)
    created = False
    if path is None:
        path = graph.journals_dir / journal_filename(journal_date, ".md")
        created = True

    append_line = f"- {text.strip()}\n"
    existing = path.read_text(encoding="utf-8") if path.exists() else ""

    if existing and not existing.endswith("\n"):
        append_text = f"\n{append_line}"
    else:
        append_text = append_line

    if not dry_run:
        updated_content = f"{existing}{append_text}"
        _atomic_write(path, updated_content)

    return {
        "path": str(path.resolve()),
        "date": journal_date.isoformat(),
        "created": created,
        "dry_run": dry_run,
        "appended_text": append_text,
    }


def _atomic_write(path: Path, content: str) -> None:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        delete=False,
    ) as handle:
        handle.write(content)
        temp_path = Path(handle.name)
    temp_path.replace(path)
