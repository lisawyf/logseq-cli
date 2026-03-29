from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import tempfile

from logseq_cli.core.errors import ExitCodes, LogseqCliError
from logseq_cli.core.graph import iter_documents
from logseq_cli.core.models import Document, Graph
from logseq_cli.core.parser import extract_title, parse_blocks


def normalize_page_name(value: str) -> str:
    lowered = value.strip().lower()
    return "".join(ch for ch in lowered if ch not in {" ", "_", "-"})


def build_document(path: Path, doc_type: str) -> Document:
    content = path.read_text(encoding="utf-8")
    title = extract_title(content, path)
    journal_date = _journal_date_from_path(path) if doc_type == "journal" else None
    return Document(
        name=path.stem,
        title=journal_date.isoformat() if journal_date else title,
        path=path.resolve(),
        doc_type=doc_type,
        format="org" if path.suffix.lower() == ".org" else "markdown",
        content=content,
        blocks=parse_blocks(content, path),
        is_journal=(doc_type == "journal"),
        journal_date=journal_date,
    )


def list_pages(graph: Graph) -> list[Document]:
    return [build_document(path, "page") for path in iter_documents(graph.pages_dir)]


def create_page(
    graph: Graph,
    page_name: str,
    *,
    text: str = "",
    doc_format: str = "markdown",
    dry_run: bool = False,
) -> dict[str, object]:
    clean_name = page_name.strip()
    if not clean_name:
        raise LogseqCliError(
            code="INVALID_PAGE_NAME",
            message="Page name must not be empty.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )
    if any(sep in clean_name for sep in ("/", "\\")):
        raise LogseqCliError(
            code="INVALID_PAGE_NAME",
            message="Page name must not contain path separators.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )

    extension = _normalize_page_format(doc_format)
    _ensure_page_does_not_exist(graph, clean_name)

    path = graph.pages_dir / f"{clean_name}{extension}"
    content = _build_page_content(clean_name, text, extension)
    result = {
        "path": str(path.resolve()),
        "title": clean_name,
        "created": True,
        "dry_run": dry_run,
        "format": "org" if extension == ".org" else "markdown",
        "content": content,
    }

    if dry_run:
        return result

    graph.pages_dir.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, content)
    return result


def append_to_page(
    graph: Graph,
    page_name: str,
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

    document = resolve_page(graph, page_name)
    existing = document.content
    append_text = text.strip()
    if existing and not existing.endswith("\n"):
        appended = f"\n{append_text}\n"
    elif existing:
        appended = f"{append_text}\n"
    else:
        appended = f"{append_text}\n"
    content = f"{existing}{appended}"
    result = {
        "path": str(document.path),
        "title": document.title,
        "dry_run": dry_run,
        "appended_text": appended,
        "content": content,
    }

    if dry_run:
        return result

    _atomic_write(document.path, content)
    return result


def append_under_heading(
    graph: Graph,
    page_name: str,
    heading: str,
    text: str,
    *,
    dry_run: bool = False,
) -> dict[str, object]:
    if not heading.strip():
        raise LogseqCliError(
            code="INVALID_HEADING",
            message="--heading must not be empty.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )
    if not text.strip():
        raise LogseqCliError(
            code="EMPTY_TEXT",
            message="--text must not be empty.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )

    document = resolve_page(graph, page_name)
    content = _append_under_heading_content(document.content, document.format, heading, text.strip())
    appended = f"{text.strip()}\n"
    result = {
        "path": str(document.path),
        "title": document.title,
        "heading": heading.strip(),
        "dry_run": dry_run,
        "appended_text": appended,
        "content": content,
    }

    if dry_run:
        return result

    _atomic_write(document.path, content)
    return result


def resolve_page(graph: Graph, page_name: str) -> Document:
    pages = list(iter_documents(graph.pages_dir))

    for path in pages:
        if path.stem == page_name:
            return build_document(path, "page")

    for path in pages:
        if path.stem.lower() == page_name.lower():
            return build_document(path, "page")

    normalized_query = normalize_page_name(page_name)
    for path in pages:
        if normalize_page_name(path.stem) == normalized_query:
            return build_document(path, "page")

    for path in pages:
        content = path.read_text(encoding="utf-8")
        title = extract_title(content, path)
        if normalize_page_name(title) == normalized_query:
            return build_document(path, "page")

    raise LogseqCliError(
        code="PAGE_NOT_FOUND",
        message=f"Page '{page_name}' not found",
        exit_code=ExitCodes.PAGE_NOT_FOUND,
    )


def _normalize_page_format(doc_format: str) -> str:
    normalized = doc_format.strip().lower()
    if normalized in {"markdown", "md"}:
        return ".md"
    if normalized in {"org", "orgmode", "org-mode"}:
        return ".org"
    raise LogseqCliError(
        code="INVALID_FORMAT",
        message=f"Unsupported page format '{doc_format}'. Use markdown or org.",
        exit_code=ExitCodes.INVALID_ARGUMENTS,
    )


def _ensure_page_does_not_exist(graph: Graph, page_name: str) -> None:
    normalized_query = normalize_page_name(page_name)
    for path in iter_documents(graph.pages_dir):
        if path.stem == page_name:
            raise _page_exists_error(page_name)
        if path.stem.lower() == page_name.lower():
            raise _page_exists_error(page_name)
        if normalize_page_name(path.stem) == normalized_query:
            raise _page_exists_error(page_name)

        content = path.read_text(encoding="utf-8")
        title = extract_title(content, path)
        if normalize_page_name(title) == normalized_query:
            raise _page_exists_error(page_name)


def _page_exists_error(page_name: str) -> LogseqCliError:
    return LogseqCliError(
        code="PAGE_ALREADY_EXISTS",
        message=f"Page '{page_name}' already exists",
        exit_code=ExitCodes.WRITE_CONFLICT,
    )


def _append_under_heading_content(content: str, doc_format: str, heading: str, text: str) -> str:
    lines = content.splitlines()
    target = _find_heading_index(lines, doc_format, heading)
    if target is None:
        raise LogseqCliError(
            code="HEADING_NOT_FOUND",
            message=f"Heading '{heading}' not found",
            exit_code=ExitCodes.PAGE_NOT_FOUND,
        )

    start_index, start_level = target
    insert_at = len(lines)
    for index in range(start_index + 1, len(lines)):
        heading_info = _parse_heading_line(lines[index], doc_format)
        if heading_info is None:
            continue
        _, level = heading_info
        if level <= start_level:
            insert_at = index
            break

    updated_lines = [*lines[:insert_at], text, *lines[insert_at:]]
    return "\n".join(updated_lines) + "\n"


def _find_heading_index(lines: list[str], doc_format: str, heading: str) -> tuple[int, int] | None:
    normalized_heading = normalize_page_name(heading)
    for index, line in enumerate(lines):
        heading_info = _parse_heading_line(line, doc_format)
        if heading_info is None:
            continue
        title, level = heading_info
        if normalize_page_name(title) == normalized_heading:
            return index, level
    return None


def _parse_heading_line(line: str, doc_format: str) -> tuple[str, int] | None:
    if doc_format == "org":
        match = re.match(r"^(\*+)\s+(.*)$", line)
        if not match:
            return None
        return match.group(2).strip(), len(match.group(1))

    match = re.match(r"^(#{1,6})\s+(.*)$", line)
    if not match:
        return None
    return match.group(2).strip(), len(match.group(1))


def _build_page_content(page_name: str, text: str, extension: str) -> str:
    body = text.strip()
    if extension == ".org":
        heading = f"* {page_name}"
        if not body:
            return f"{heading}\n"
        return f"{heading}\n{body}\n"

    heading = f"# {page_name}"
    if not body:
        return f"{heading}\n"
    return f"{heading}\n\n{body}\n"


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


def _journal_date_from_path(path: Path) -> date | None:
    try:
        return date.fromisoformat(path.stem.replace("_", "-"))
    except ValueError:
        return None
