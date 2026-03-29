from __future__ import annotations

from pathlib import Path

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
    return Document(
        name=path.stem,
        title=title,
        path=path.resolve(),
        doc_type=doc_type,
        format="org" if path.suffix.lower() == ".org" else "markdown",
        content=content,
        blocks=parse_blocks(content, path),
        is_journal=(doc_type == "journal"),
    )


def list_pages(graph: Graph) -> list[Document]:
    return [build_document(path, "page") for path in iter_documents(graph.pages_dir)]


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
            return Document(
                name=path.stem,
                title=title,
                path=path.resolve(),
                doc_type="page",
                format="org" if path.suffix.lower() == ".org" else "markdown",
                content=content,
                blocks=parse_blocks(content, path),
            )

    raise LogseqCliError(
        code="PAGE_NOT_FOUND",
        message=f"Page '{page_name}' not found",
        exit_code=ExitCodes.PAGE_NOT_FOUND,
    )
