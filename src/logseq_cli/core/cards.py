from __future__ import annotations

from datetime import date

from logseq_cli.core.graph import iter_documents
from logseq_cli.core.graph import Graph
from logseq_cli.core.pages import build_document, normalize_page_name, resolve_page
from logseq_cli.core.recall import recall_topic
from logseq_cli.core.tasks import list_tasks

OPEN_TASK_STATES = {"TODO", "DOING", "WAITING", "NOW", "LATER"}


def build_topic_card(
    graph: Graph,
    topic: str,
    *,
    since: date | None = None,
    until: date | None = None,
    evidence_limit: int = 8,
) -> dict[str, object]:
    recall = recall_topic(graph, topic, since=since, until=until, limit=evidence_limit)
    return _build_card_from_recall(recall, target_type="topic", title=topic)


def build_tag_card(
    graph: Graph,
    tag: str,
    *,
    since: date | None = None,
    until: date | None = None,
    evidence_limit: int = 8,
) -> dict[str, object]:
    normalized_tag = tag.lstrip("#")
    recall = recall_topic(graph, normalized_tag, since=since, until=until, limit=evidence_limit)
    return _build_card_from_recall(recall, target_type="tag", title=f"#{normalized_tag}")


def build_project_card(
    graph: Graph,
    project_name: str,
    *,
    since: date | None = None,
    until: date | None = None,
    evidence_limit: int = 8,
) -> dict[str, object]:
    project_document = resolve_page(graph, project_name)
    normalized_project = normalize_page_name(project_document.title)

    evidence: list[dict[str, object]] = []
    source_records: dict[str, dict[str, object]] = {}
    related_tags: list[str] = []
    related_page_refs: list[str] = []
    journal_dates: list[str] = []

    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        for path in iter_documents(directory):
            document = build_document(path, doc_type)
            include_document_blocks = normalize_page_name(document.title) == normalized_project
            if document.doc_type == "journal" and document.journal_date is not None:
                journal_date = document.journal_date
                if since and journal_date < since:
                    continue
                if until and journal_date > until:
                    continue

            for block in document.blocks:
                references_project = any(normalize_page_name(ref) == normalized_project for ref in block.page_refs)
                if not include_document_blocks and not references_project:
                    continue
                if (
                    include_document_blocks
                    and block.type == "heading"
                    and normalize_page_name(block.text) == normalized_project
                ):
                    continue

                evidence.append(
                    {
                        "title": document.title,
                        "path": str(document.path),
                        "doc_type": document.doc_type,
                        "line_no": block.line_no,
                        "text": block.text,
                        "journal_date": document.journal_date.isoformat() if document.journal_date else None,
                        "todo_state": block.todo_state,
                        "match_kinds": _project_match_kinds(include_document_blocks, references_project),
                    }
                )
                source_records[str(document.path)] = {
                    "title": document.title,
                    "path": str(document.path),
                    "doc_type": document.doc_type,
                    "journal_date": document.journal_date.isoformat() if document.journal_date else None,
                }
                if document.journal_date is not None:
                    journal_dates.append(document.journal_date.isoformat())
                related_tags.extend(tag for tag in block.tags if tag not in related_tags)
                for ref in block.page_refs:
                    if normalize_page_name(ref) != normalized_project and ref not in related_page_refs:
                        related_page_refs.append(ref)

    evidence.sort(key=_project_evidence_sort_key, reverse=True)

    open_tasks = []
    for task in list_tasks(graph):
        in_project_page = normalize_page_name(task.title) == normalized_project
        refs_project = any(normalize_page_name(ref) == normalized_project for ref in task.page_refs)
        if not in_project_page and not refs_project:
            continue
        if task.doc_type == "journal":
            journal_date = _date_from_title(task.title)
            if since and journal_date and journal_date < since:
                continue
            if until and journal_date and journal_date > until:
                continue
        if task.state not in OPEN_TASK_STATES:
            continue
        open_tasks.append(
            {
                "title": task.title,
                "path": str(task.path),
                "doc_type": task.doc_type,
                "line_no": task.line_no,
                "state": task.state,
                "text": task.text,
            }
        )

    key_points = _unique_texts(item["text"] for item in evidence if item["doc_type"] == "page")
    if not key_points:
        key_points = _unique_texts(item["text"] for item in evidence)

    first_date = min(journal_dates) if journal_dates else None
    last_date = max(journal_dates) if journal_dates else None
    date_phrase = _date_phrase(first_date, last_date)
    summary = (
        f"{project_document.title} appears in {len(evidence)} matched blocks across "
        f"{len(source_records)} sources{date_phrase}. Open tasks: {len(open_tasks)}."
    )

    return {
        "card_type": "knowledge",
        "target_type": "project",
        "target": project_name,
        "title": project_document.title,
        "summary": summary,
        "date_window": {
            "since": since.isoformat() if since else None,
            "until": until.isoformat() if until else None,
        },
        "date_span": {
            "first": first_date,
            "last": last_date,
        },
        "project_path": str(project_document.path),
        "source_count": len(source_records),
        "match_count": len(evidence),
        "key_points": key_points[:5],
        "open_tasks": open_tasks[:5],
        "related_tags": related_tags[:5],
        "related_page_refs": related_page_refs[:5],
        "top_sources": list(source_records.values())[:5],
        "evidence": evidence[:evidence_limit],
    }


def _build_card_from_recall(recall: dict[str, object], *, target_type: str, title: str) -> dict[str, object]:
    top_matches = list(recall["top_matches"])
    open_tasks = [
        {
            "title": match["title"],
            "path": match["path"],
            "line_no": match["line_no"],
            "state": match["todo_state"],
            "text": match["text"],
            "journal_date": match["journal_date"],
        }
        for match in top_matches
        if match["todo_state"] in OPEN_TASK_STATES
    ]
    key_points = _unique_texts(match["text"] for match in top_matches)
    evidence = [
        {
            "title": match["title"],
            "path": match["path"],
            "line_no": match["line_no"],
            "text": match["text"],
            "journal_date": match["journal_date"],
            "match_kinds": match["match_kinds"],
        }
        for match in top_matches
    ]
    top_sources = list(recall["sources"])[:5]
    related_tags = [row["tag"] for row in list(recall["related_tags"])[:5]]
    related_page_refs = [row["page"] for row in list(recall["related_page_refs"])[:5]]

    first_date = recall["first_journal_date"]
    last_date = recall["last_journal_date"]
    date_phrase = _date_phrase(first_date, last_date)
    summary = (
        f"{title} appears in {recall['match_count']} matched blocks across "
        f"{recall['source_count']} sources{date_phrase}. "
        f"Open tasks: {len(open_tasks)}."
    )

    return {
        "card_type": "knowledge",
        "target_type": target_type,
        "target": recall["topic"],
        "title": title,
        "summary": summary,
        "date_window": recall["date_window"],
        "date_span": {
            "first": first_date,
            "last": last_date,
        },
        "source_count": recall["source_count"],
        "match_count": recall["match_count"],
        "key_points": key_points[:5],
        "open_tasks": open_tasks[:5],
        "related_tags": related_tags,
        "related_page_refs": related_page_refs,
        "top_sources": top_sources,
        "evidence": evidence,
    }


def _unique_texts(values) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = value.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        result.append(value)
    return result


def _date_phrase(first_date: str | None, last_date: str | None) -> str:
    if first_date and last_date and first_date != last_date:
        return f" from {first_date} to {last_date}"
    if first_date:
        return f" on {first_date}"
    return ""


def _project_match_kinds(in_project_page: bool, references_project: bool) -> list[str]:
    kinds: list[str] = []
    if in_project_page:
        kinds.append("project_page")
    if references_project:
        kinds.append("page_ref")
    return kinds


def _project_evidence_sort_key(item: dict[str, object]) -> tuple[int, str, str, int]:
    return (
        1 if "project_page" in item["match_kinds"] else 0,
        str(item["journal_date"] or ""),
        str(item["path"]),
        int(item["line_no"]),
    )


def _date_from_title(title: str) -> date | None:
    try:
        return date.fromisoformat(title)
    except ValueError:
        return None
