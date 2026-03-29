from __future__ import annotations

from logseq_cli.core.errors import ExitCodes, LogseqCliError
from logseq_cli.core.graph import iter_documents
from logseq_cli.core.models import Graph, SearchHit
from logseq_cli.core.parser import extract_title

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
            content = path.read_text(encoding="utf-8")
            title = extract_title(content, path)
            for line_no, line in enumerate(content.splitlines(), start=1):
                haystack = line if case_sensitive else line.lower()
                if query_text in haystack:
                    hits.append(
                        SearchHit(
                            path=path.resolve(),
                            title=title,
                            doc_type=doc_type,
                            line_no=line_no,
                            snippet=line.strip(),
                            match_text=query,
                        )
                    )
                    if len(hits) >= limit:
                        return hits

    return hits
