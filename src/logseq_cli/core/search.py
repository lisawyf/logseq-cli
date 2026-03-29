from __future__ import annotations

from logseq_cli.core.documents import load_document
from logseq_cli.core.errors import ExitCodes, LogseqCliError
from logseq_cli.core.graph import iter_documents
from logseq_cli.core.models import Graph, SearchHit
from logseq_cli.core.pages import normalize_page_name

VALID_SCOPES = {"pages", "journals"}


def parse_scope(scope: str) -> set[str]:
    selected = {item.strip().lower() for item in scope.split(",") if item.strip()}
    selected = selected or {"pages", "journals"}
    invalid = sorted(selected - VALID_SCOPES)
    if invalid:
        raise LogseqCliError(
            code="INVALID_SCOPE",
            message=f"Unsupported scope value(s): {', '.join(invalid)}",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )
    return selected


def search_text(
    graph: Graph,
    query: str,
    *,
    scope: str = "pages,journals",
    limit: int = 20,
    case_sensitive: bool = False,
) -> list[SearchHit]:
    selected = parse_scope(scope)
    query_text = query if case_sensitive else query.lower()
    hits: list[SearchHit] = []

    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        scope_name = f"{doc_type}s"
        if scope_name not in selected:
            continue

        for path in iter_documents(directory):
            document = load_document(path, doc_type)
            for line_no, line in enumerate(document.content.splitlines(), start=1):
                haystack = line if case_sensitive else line.lower()
                if query_text in haystack:
                    hits.append(
                        SearchHit(
                            path=document.path,
                            title=document.title,
                            doc_type=doc_type,
                            line_no=line_no,
                            snippet=line.strip(),
                            match_text=query,
                        )
                    )
                    if len(hits) >= limit:
                        return hits

    return hits


def search_links(
    graph: Graph,
    target: str,
    *,
    scope: str = "pages,journals",
    limit: int = 20,
) -> list[dict[str, object]]:
    if not target.strip():
        raise LogseqCliError(
            code="INVALID_QUERY",
            message="Search query must not be empty.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )

    selected = parse_scope(scope)
    normalized_target = normalize_page_name(target)
    hits: list[dict[str, object]] = []

    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        scope_name = f"{doc_type}s"
        if scope_name not in selected:
            continue

        for path in iter_documents(directory):
            document = load_document(path, doc_type)
            for block in document.blocks:
                matched_refs = [ref for ref in block.page_refs if normalize_page_name(ref) == normalized_target]
                if not matched_refs:
                    continue
                hits.append(
                    {
                        "path": str(document.path),
                        "title": document.title,
                        "doc_type": document.doc_type,
                        "line_no": block.line_no,
                        "snippet": block.text,
                        "matched_refs": matched_refs,
                    }
                )
                if len(hits) >= limit:
                    return hits

    return hits


def search_tags(
    graph: Graph,
    tag: str,
    *,
    scope: str = "pages,journals",
    limit: int = 20,
) -> list[dict[str, object]]:
    normalized_tag = tag.strip().lstrip("#").casefold()
    if not normalized_tag:
        raise LogseqCliError(
            code="INVALID_QUERY",
            message="Search query must not be empty.",
            exit_code=ExitCodes.INVALID_ARGUMENTS,
        )

    selected = parse_scope(scope)
    hits: list[dict[str, object]] = []

    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        scope_name = f"{doc_type}s"
        if scope_name not in selected:
            continue

        for path in iter_documents(directory):
            document = load_document(path, doc_type)
            for block in document.blocks:
                matched_tags = [item for item in block.tags if item.casefold() == normalized_tag]
                if not matched_tags:
                    continue
                hits.append(
                    {
                        "path": str(document.path),
                        "title": document.title,
                        "doc_type": document.doc_type,
                        "line_no": block.line_no,
                        "snippet": block.text,
                        "matched_tags": matched_tags,
                    }
                )
                if len(hits) >= limit:
                    return hits

    return hits
