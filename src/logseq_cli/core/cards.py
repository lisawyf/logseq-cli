from __future__ import annotations

from datetime import date

from logseq_cli.core.graph import Graph
from logseq_cli.core.recall import recall_topic

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
