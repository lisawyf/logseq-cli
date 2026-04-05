from __future__ import annotations

from datetime import date
import re

from logseq_cli.core.graph import Graph, iter_documents
from logseq_cli.core.models import Block
from logseq_cli.core.pages import build_document, normalize_page_name
from logseq_cli.core.search import parse_scope

DECISION_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bdecided to\b",
        r"\bwe decided\b",
        r"\bfinal decision\b",
        r"\bchose to\b",
        r"\bwe chose\b",
        r"\badopt(?:ed)?\b",
        r"\bgo with\b",
        r"\bwent with\b",
        r"\bswitch(?:ed)? to\b",
        r"\bmigrate(?:d)? to\b",
        r"\bstandardi[sz]e(?:d)? on\b",
        r"\bdrop(?:ped)?\b",
        r"\bdeprecat(?:e|ed)\b",
        r"\bwon't\b",
        r"\bwill not\b",
        r"决定",
        r"最终",
        r"改用",
        r"采用",
        r"切换到",
        r"放弃",
        r"不做",
        r"统一用",
    )
]

REASON_INLINE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bbecause\b(.+)",
        r"\bdue to\b(.+)",
        r"\bso that\b(.+)",
        r"\bto avoid\b(.+)",
        r"\bin order to\b(.+)",
        r"因为(.+)",
        r"原因是(.+)",
        r"为了(.+)",
        r"避免(.+)",
        r"这样可以(.+)",
    )
]

REASON_BLOCK_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bbecause\b",
        r"\bdue to\b",
        r"\breason\b",
        r"\btrade[- ]?off\b",
        r"\bto avoid\b",
        r"因为",
        r"原因",
        r"为了",
        r"避免",
        r"权衡",
    )
]


def list_decisions(
    graph: Graph,
    *,
    query: str | None = None,
    scope: str = "pages,journals",
    since: date | None = None,
    until: date | None = None,
    limit: int = 20,
) -> dict[str, object]:
    selected_scopes = parse_scope(scope)
    normalized_query = _normalize_query(query)
    decisions: list[dict[str, object]] = []

    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        scope_name = f"{doc_type}s"
        if scope_name not in selected_scopes:
            continue

        for path in iter_documents(directory):
            document = build_document(path, doc_type)
            if document.doc_type == "journal" and not _journal_in_window(document.journal_date, since=since, until=until):
                continue

            children_by_parent = _children_by_parent(document.blocks)
            for block in document.blocks:
                if not _looks_like_decision(block.text):
                    continue
                if normalized_query and not _matches_query(block, normalized_query):
                    continue

                reason_snippets = _extract_reasons(block, children_by_parent.get(block.line_no, []))
                decisions.append(
                    {
                        "title": document.title,
                        "path": str(document.path),
                        "doc_type": document.doc_type,
                        "line_no": block.line_no,
                        "text": block.text,
                        "journal_date": document.journal_date.isoformat() if document.journal_date else None,
                        "tags": block.tags,
                        "page_refs": block.page_refs,
                        "todo_state": block.todo_state,
                        "reason_snippets": reason_snippets,
                        "reason_count": len(reason_snippets),
                    }
                )

    decisions.sort(key=_decision_sort_key, reverse=True)
    top = decisions[:limit]

    return {
        "query": query,
        "scope": sorted(selected_scopes),
        "date_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else None,
        },
        "count": len(decisions),
        "returned_count": len(top),
        "decisions": top,
    }


def _looks_like_decision(text: str) -> bool:
    return any(pattern.search(text) for pattern in DECISION_PATTERNS)


def _normalize_query(query: str | None) -> str | None:
    if query is None:
        return None
    normalized = query.strip().casefold()
    return normalized or None


def _matches_query(block: Block, normalized_query: str) -> bool:
    if normalized_query in block.text.casefold():
        return True
    if normalized_query in {tag.casefold() for tag in block.tags}:
        return True
    if normalized_query in {normalize_page_name(ref) for ref in block.page_refs}:
        return True
    return False


def _extract_reasons(block: Block, child_blocks: list[Block]) -> list[str]:
    reasons: list[str] = []

    for pattern in REASON_INLINE_PATTERNS:
        match = pattern.search(block.text)
        if match:
            snippet = match.group(1).strip(" :.-")
            if snippet:
                reasons.append(snippet)

    for child in child_blocks:
        if any(pattern.search(child.text) for pattern in REASON_BLOCK_PATTERNS):
            reasons.append(child.text)

    if not reasons:
        for child in child_blocks[:2]:
            if child.text not in reasons:
                reasons.append(child.text)

    unique: list[str] = []
    seen: set[str] = set()
    for reason in reasons:
        key = reason.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(reason)
    return unique[:3]


def _children_by_parent(blocks: list[Block]) -> dict[int, list[Block]]:
    result: dict[int, list[Block]] = {}
    for block in blocks:
        if block.parent_line_no is None:
            continue
        result.setdefault(block.parent_line_no, []).append(block)
    return result


def _journal_in_window(journal_date: date | None, *, since: date | None, until: date | None) -> bool:
    if journal_date is None:
        return True
    if since and journal_date < since:
        return False
    if until and journal_date > until:
        return False
    return True


def _decision_sort_key(item: dict[str, object]) -> tuple[str, int, int, str]:
    return (
        str(item["journal_date"] or ""),
        int(item["reason_count"]),
        1 if item["doc_type"] == "journal" else 0,
        str(item["path"]),
    )
