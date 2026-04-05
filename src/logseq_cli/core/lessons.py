from __future__ import annotations

from datetime import date
import re

from logseq_cli.core.graph import Graph, iter_documents
from logseq_cli.core.models import Block
from logseq_cli.core.pages import build_document, normalize_page_name
from logseq_cli.core.search import parse_scope

LESSON_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\blesson learned\b",
        r"\blearned that\b",
        r"\bwe learned\b",
        r"\bturns out\b",
        r"\bbest practice\b",
        r"\bgotcha\b",
        r"\bpitfall\b",
        r"\bwatch out\b",
        r"\bbe careful\b",
        r"\bavoid\b",
        r"\bremember to\b",
        r"\bnote to self\b",
        r"\btip:\b",
        r"\bkeep in mind\b",
        r"\bshould always\b",
        r"经验",
        r"教训",
        r"踩坑",
        r"最佳实践",
        r"注意",
        r"记住",
        r"避免",
        r"小心",
        r"坑",
    )
]

TAKEAWAY_INLINE_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\blesson learned\b[:：]?\s*(.+)",
        r"\blearned that\b(.+)",
        r"\bbest practice\b[:：]?\s*(.+)",
        r"\bgotcha\b[:：]?\s*(.+)",
        r"\btip\b[:：]?\s*(.+)",
        r"\bremember to\b(.+)",
        r"\bavoid\b(.+)",
        r"经验[:：](.+)",
        r"教训[:：](.+)",
        r"注意[:：](.+)",
        r"记住[:：](.+)",
        r"避免[:：](.+)",
        r"最佳实践[:：](.+)",
    )
]

TAKEAWAY_BLOCK_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bwhy\b",
        r"\bso that\b",
        r"\bthis means\b",
        r"\botherwise\b",
        r"\bavoid\b",
        r"\bremember\b",
        r"\bcareful\b",
        r"因为",
        r"所以",
        r"否则",
        r"避免",
        r"注意",
        r"记住",
    )
]


def list_lessons(
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
    lessons: list[dict[str, object]] = []

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
                if not _looks_like_lesson(block.text):
                    continue
                if normalized_query and not _matches_query(block, normalized_query):
                    continue

                takeaway_snippets = _extract_takeaways(block, children_by_parent.get(block.line_no, []))
                lessons.append(
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
                        "takeaway_snippets": takeaway_snippets,
                        "takeaway_count": len(takeaway_snippets),
                    }
                )

    lessons.sort(key=_lesson_sort_key, reverse=True)
    top = lessons[:limit]

    return {
        "query": query,
        "scope": sorted(selected_scopes),
        "date_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else None,
        },
        "count": len(lessons),
        "returned_count": len(top),
        "lessons": top,
    }


def _looks_like_lesson(text: str) -> bool:
    return any(pattern.search(text) for pattern in LESSON_PATTERNS)


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


def _extract_takeaways(block: Block, child_blocks: list[Block]) -> list[str]:
    takeaways: list[str] = []

    for pattern in TAKEAWAY_INLINE_PATTERNS:
        match = pattern.search(block.text)
        if match:
            snippet = match.group(1).strip(" :.-")
            if snippet:
                takeaways.append(snippet)

    for child in child_blocks:
        if any(pattern.search(child.text) for pattern in TAKEAWAY_BLOCK_PATTERNS):
            takeaways.append(child.text)

    if not takeaways:
        for child in child_blocks[:2]:
            if child.text not in takeaways:
                takeaways.append(child.text)

    unique: list[str] = []
    seen: set[str] = set()
    for takeaway in takeaways:
        key = takeaway.casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(takeaway)
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


def _lesson_sort_key(item: dict[str, object]) -> tuple[str, int, int, str]:
    return (
        str(item["journal_date"] or ""),
        int(item["takeaway_count"]),
        1 if item["doc_type"] == "journal" else 0,
        str(item["path"]),
    )
