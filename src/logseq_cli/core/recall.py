from __future__ import annotations

from collections import Counter
from datetime import date

from logseq_cli.core.graph import Graph, iter_documents
from logseq_cli.core.models import Document
from logseq_cli.core.pages import build_document, normalize_page_name


def parse_date_window(*, since: str | None = None, until: str | None = None) -> tuple[date | None, date | None]:
    since_date = date.fromisoformat(since) if since else None
    until_date = date.fromisoformat(until) if until else None
    if since_date and until_date and since_date > until_date:
        raise ValueError("--since must be earlier than or equal to --until.")
    return since_date, until_date


def recall_topic(
    graph: Graph,
    topic: str,
    *,
    since: date | None = None,
    until: date | None = None,
    limit: int = 10,
) -> dict[str, object]:
    normalized_topic = topic.strip().lstrip("#").casefold()
    normalized_page = normalize_page_name(topic)

    matches: list[dict[str, object]] = []
    source_counts: Counter[str] = Counter()
    source_records: dict[str, dict[str, object]] = {}
    related_tags: Counter[str] = Counter()
    related_page_refs: Counter[str] = Counter()
    task_states: Counter[str] = Counter()
    journal_dates: list[date] = []

    for document in _iter_all_documents(graph):
        if document.doc_type == "journal" and not _journal_in_window(document, since=since, until=until):
            continue

        for block in document.blocks:
            match_kinds = _match_kinds(block.text, block.tags, block.page_refs, normalized_topic, normalized_page)
            if not match_kinds:
                continue

            score = _score_match(match_kinds, has_todo=block.todo_state is not None)
            match = {
                "title": document.title,
                "path": str(document.path),
                "doc_type": document.doc_type,
                "line_no": block.line_no,
                "text": block.text,
                "journal_date": document.journal_date.isoformat() if document.journal_date else None,
                "match_kinds": match_kinds,
                "score": score,
            }
            matches.append(match)

            source_key = str(document.path)
            source_counts[source_key] += 1
            source_records[source_key] = {
                "title": document.title,
                "path": str(document.path),
                "doc_type": document.doc_type,
                "journal_date": document.journal_date.isoformat() if document.journal_date else None,
            }

            for tag in block.tags:
                if tag.casefold() != normalized_topic:
                    related_tags[tag] += 1
            for ref in block.page_refs:
                if normalize_page_name(ref) != normalized_page:
                    related_page_refs[ref] += 1
            if block.todo_state:
                task_states.update([block.todo_state])
            if document.journal_date is not None:
                journal_dates.append(document.journal_date)

    matches.sort(key=_match_sort_key, reverse=True)
    top_matches = matches[:limit]

    sources = []
    for path, record in source_records.items():
        enriched = dict(record)
        enriched["match_count"] = source_counts[path]
        sources.append(enriched)
    sources.sort(key=lambda item: (_source_sort_date(item), item["path"]), reverse=True)

    return {
        "recall_type": "topic",
        "topic": topic,
        "normalized_topic": normalized_topic,
        "date_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else None,
        },
        "source_count": len(sources),
        "page_source_count": sum(1 for item in sources if item["doc_type"] == "page"),
        "journal_source_count": sum(1 for item in sources if item["doc_type"] == "journal"),
        "match_count": len(matches),
        "task_count": sum(task_states.values()),
        "task_states": dict(sorted(task_states.items())),
        "first_journal_date": min(journal_dates).isoformat() if journal_dates else None,
        "last_journal_date": max(journal_dates).isoformat() if journal_dates else None,
        "sources": sources,
        "top_matches": top_matches,
        "top_match_count": len(top_matches),
        "related_tags": _counter_rows(related_tags, key_name="tag"),
        "related_page_refs": _counter_rows(related_page_refs, key_name="page"),
    }


def timeline_topic(
    graph: Graph,
    topic: str,
    *,
    since: date | None = None,
    until: date | None = None,
    limit: int = 50,
) -> dict[str, object]:
    normalized_topic = topic.strip().lstrip("#").casefold()
    normalized_page = normalize_page_name(topic)

    entries: list[dict[str, object]] = []
    date_counts: Counter[str] = Counter()
    related_tags: Counter[str] = Counter()
    related_page_refs: Counter[str] = Counter()
    task_states: Counter[str] = Counter()

    for document in _iter_all_documents(graph):
        if document.doc_type != "journal" or not _journal_in_window(document, since=since, until=until):
            continue

        for block in document.blocks:
            match_kinds = _match_kinds(block.text, block.tags, block.page_refs, normalized_topic, normalized_page)
            if not match_kinds:
                continue

            journal_date = document.journal_date.isoformat() if document.journal_date else None
            date_counts.update([journal_date or ""])
            for tag in block.tags:
                if tag.casefold() != normalized_topic:
                    related_tags[tag] += 1
            for ref in block.page_refs:
                if normalize_page_name(ref) != normalized_page:
                    related_page_refs[ref] += 1
            if block.todo_state:
                task_states.update([block.todo_state])

            entries.append(
                {
                    "date": journal_date,
                    "title": document.title,
                    "path": str(document.path),
                    "line_no": block.line_no,
                    "text": block.text,
                    "match_kinds": match_kinds,
                    "score": _score_match(match_kinds, has_todo=block.todo_state is not None),
                }
            )

    entries.sort(key=lambda item: (str(item["date"]), int(item["score"]), int(item["line_no"])))

    return {
        "timeline_type": "topic",
        "topic": topic,
        "normalized_topic": normalized_topic,
        "date_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else None,
        },
        "entry_count": len(entries),
        "journal_count": len([key for key in date_counts if key]),
        "first_date": entries[0]["date"] if entries else None,
        "last_date": entries[-1]["date"] if entries else None,
        "entries": entries[:limit],
        "returned_entry_count": min(len(entries), limit),
        "dates": [
            {"date": key, "count": count}
            for key, count in sorted(date_counts.items(), key=lambda item: item[0])
            if key
        ],
        "task_count": sum(task_states.values()),
        "task_states": dict(sorted(task_states.items())),
        "related_tags": _counter_rows(related_tags, key_name="tag"),
        "related_page_refs": _counter_rows(related_page_refs, key_name="page"),
    }


def _iter_all_documents(graph: Graph) -> list[Document]:
    documents: list[Document] = []
    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        for path in iter_documents(directory):
            document = build_document(path, doc_type)
            if doc_type == "journal":
                try:
                    journal_date = date.fromisoformat(path.stem.replace("_", "-"))
                except ValueError:
                    journal_date = None
                if journal_date is not None:
                    document.journal_date = journal_date
                    document.title = journal_date.isoformat()
            documents.append(document)
    return documents


def _journal_in_window(document: Document, *, since: date | None, until: date | None) -> bool:
    if document.journal_date is None:
        return True
    if since and document.journal_date < since:
        return False
    if until and document.journal_date > until:
        return False
    return True


def _match_kinds(
    text: str,
    tags: list[str],
    page_refs: list[str],
    normalized_topic: str,
    normalized_page: str,
) -> list[str]:
    kinds: list[str] = []
    if normalized_topic in text.casefold():
        kinds.append("text")
    if normalized_topic in {tag.casefold() for tag in tags}:
        kinds.append("tag")
    if normalized_page in {normalize_page_name(ref) for ref in page_refs}:
        kinds.append("page_ref")
    return kinds


def _score_match(match_kinds: list[str], *, has_todo: bool) -> int:
    score = 0
    if "page_ref" in match_kinds:
        score += 4
    if "tag" in match_kinds:
        score += 3
    if "text" in match_kinds:
        score += 2
    if has_todo:
        score += 1
    return score


def _match_sort_key(match: dict[str, object]) -> tuple[int, str, str, int]:
    journal_date = str(match["journal_date"] or "")
    return (
        int(match["score"]),
        journal_date,
        str(match["path"]),
        int(match["line_no"]),
    )


def _source_sort_date(source: dict[str, object]) -> str:
    return str(source["journal_date"] or "")


def _counter_rows(counter: Counter[str], *, key_name: str) -> list[dict[str, object]]:
    rows = [
        {key_name: key, "count": count}
        for key, count in sorted(counter.items(), key=lambda item: (-item[1], item[0].casefold()))
    ]
    return rows
