from __future__ import annotations

from logseq_cli.core.documents import journal_title_from_path
from logseq_cli.core.graph import iter_documents
from logseq_cli.core.models import Graph
from logseq_cli.core.pages import build_document, normalize_page_name, resolve_page


def backlinks(graph: Graph, page_name: str) -> list[dict[str, object]]:
    normalized_target = normalize_page_name(page_name)
    matches: list[dict[str, object]] = []

    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        for path in iter_documents(directory):
            document = build_document(path, doc_type)
            if doc_type == "journal":
                document.title = journal_title_from_path(path)
            for block in document.blocks:
                refs = [ref for ref in block.page_refs if normalize_page_name(ref) == normalized_target]
                if not refs:
                    continue
                matches.append(
                    {
                        "title": document.title,
                        "path": str(document.path),
                        "doc_type": doc_type,
                        "line_no": block.line_no,
                        "text": block.text,
                        "matched_refs": refs,
                    }
                )

    return matches


def outgoing(graph: Graph, page_name: str) -> dict[str, object]:
    document = resolve_page(graph, page_name)
    refs: dict[str, dict[str, object]] = {}
    for block in document.blocks:
        for ref in block.page_refs:
            key = normalize_page_name(ref)
            entry = refs.setdefault(
                key,
                {
                    "page": ref,
                    "count": 0,
                    "lines": [],
                },
            )
            entry["count"] += 1
            entry["lines"].append(block.line_no)

    links = sorted(refs.values(), key=lambda item: normalize_page_name(str(item["page"])))
    return {
        "source_title": document.title,
        "source_path": str(document.path),
        "links": links,
        "count": len(links),
    }
