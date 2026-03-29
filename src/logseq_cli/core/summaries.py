from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

from logseq_cli.core.graph import Graph, iter_documents
from logseq_cli.core.journals import read_journal
from logseq_cli.core.pages import build_document, normalize_page_name, resolve_page
from logseq_cli.core.tasks import list_tasks
from logseq_cli.core.models import Document


def summarize_journal(graph: Graph, journal_date: date) -> dict[str, object]:
    document = read_journal(graph, journal_date)
    task_states = Counter(block.todo_state for block in document.blocks if block.todo_state)
    page_refs = sorted({ref for block in document.blocks for ref in block.page_refs})
    tags = sorted({tag for block in document.blocks for tag in block.tags})

    return {
        "title": document.title,
        "path": str(document.path),
        "journal_date": document.journal_date.isoformat() if document.journal_date else None,
        "block_count": len(document.blocks),
        "task_count": sum(task_states.values()),
        "task_states": dict(sorted(task_states.items())),
        "page_refs": page_refs,
        "tags": tags,
    }


def summarize_daily(graph: Graph, target_date: date) -> dict[str, object]:
    summary = summarize_journal(graph, target_date)
    summary["summary_type"] = "daily"
    return summary


def summarize_weekly(graph: Graph, target_date: date) -> dict[str, object]:
    start_date = target_date - timedelta(days=6)
    journal_summaries = []
    for path in iter_documents(graph.journals_dir):
        try:
            journal_date = date.fromisoformat(path.stem.replace("_", "-"))
        except ValueError:
            continue
        if start_date <= journal_date <= target_date:
            journal_summaries.append(summarize_journal(graph, journal_date))

    journal_summaries.sort(key=lambda item: item["journal_date"])

    task_states = Counter()
    page_refs: set[str] = set()
    tags: set[str] = set()
    block_count = 0
    task_count = 0
    for summary in journal_summaries:
        block_count += int(summary["block_count"])
        task_count += int(summary["task_count"])
        task_states.update(summary["task_states"])
        page_refs.update(summary["page_refs"])
        tags.update(summary["tags"])

    return {
        "summary_type": "weekly",
        "start_date": start_date.isoformat(),
        "end_date": target_date.isoformat(),
        "journal_count": len(journal_summaries),
        "journals": journal_summaries,
        "block_count": block_count,
        "task_count": task_count,
        "task_states": dict(sorted(task_states.items())),
        "page_refs": sorted(page_refs),
        "tags": sorted(tags),
    }


def summarize_project(graph: Graph, project_name: str) -> dict[str, object]:
    project_document = resolve_page(graph, project_name)
    normalized_project = normalize_page_name(project_document.title)
    documents = _iter_all_documents(graph)

    related_blocks = []
    source_documents: dict[str, dict[str, str]] = {}
    tags: set[str] = set()
    page_refs: set[str] = set()
    backlinks_count = 0

    for document in documents:
        include_document_blocks = normalize_page_name(document.title) == normalized_project
        for block in document.blocks:
            references_project = any(normalize_page_name(ref) == normalized_project for ref in block.page_refs)
            if not include_document_blocks and not references_project:
                continue

            if references_project and normalize_page_name(document.title) != normalized_project:
                backlinks_count += 1

            related_blocks.append(
                {
                    "title": document.title,
                    "path": str(document.path),
                    "doc_type": document.doc_type,
                    "line_no": block.line_no,
                    "text": block.text,
                }
            )
            source_documents[str(document.path)] = {
                "title": document.title,
                "path": str(document.path),
                "doc_type": document.doc_type,
            }
            tags.update(block.tags)
            page_refs.update(block.page_refs)

    task_states = Counter()
    related_tasks = []
    for task in list_tasks(graph):
        in_project_page = normalize_page_name(task.title) == normalized_project
        refs_project = any(normalize_page_name(ref) == normalized_project for ref in task.page_refs)
        if not in_project_page and not refs_project:
            continue
        task_states.update([task.state])
        related_tasks.append(
            {
                "title": task.title,
                "path": str(task.path),
                "doc_type": task.doc_type,
                "line_no": task.line_no,
                "state": task.state,
                "text": task.text,
            }
        )

    outgoing_refs = sorted(
        {
            ref
            for block in project_document.blocks
            for ref in block.page_refs
            if normalize_page_name(ref) != normalized_project
        }
    )

    return {
        "summary_type": "project",
        "project": project_name,
        "project_title": project_document.title,
        "project_path": str(project_document.path),
        "source_count": len(source_documents),
        "sources": sorted(source_documents.values(), key=lambda item: item["path"]),
        "related_block_count": len(related_blocks),
        "related_task_count": len(related_tasks),
        "task_states": dict(sorted(task_states.items())),
        "backlinks_count": backlinks_count,
        "outgoing_links": outgoing_refs,
        "outgoing_count": len(outgoing_refs),
        "page_refs": sorted(page_refs),
        "tags": sorted(tags),
    }


def summarize_topic(graph: Graph, topic: str) -> dict[str, object]:
    normalized_topic = _normalize_topic(topic)
    documents = _iter_all_documents(graph)

    matches = []
    source_documents: dict[str, dict[str, str]] = {}
    tags: set[str] = set()
    page_refs: set[str] = set()
    task_states = Counter()

    for document in documents:
        for block in document.blocks:
            matches_topic = _block_matches_topic(block.text, normalized_topic)
            matches_tag = normalized_topic in {tag.casefold() for tag in block.tags}
            matches_ref = normalized_topic in {normalize_page_name(ref) for ref in block.page_refs}
            if not matches_topic and not matches_tag and not matches_ref:
                continue

            matches.append(
                {
                    "title": document.title,
                    "path": str(document.path),
                    "doc_type": document.doc_type,
                    "line_no": block.line_no,
                    "text": block.text,
                }
            )
            source_documents[str(document.path)] = {
                "title": document.title,
                "path": str(document.path),
                "doc_type": document.doc_type,
            }
            tags.update(block.tags)
            page_refs.update(block.page_refs)
            if block.todo_state:
                task_states.update([block.todo_state])

    return {
        "summary_type": "topic",
        "topic": topic,
        "source_count": len(source_documents),
        "sources": sorted(source_documents.values(), key=lambda item: item["path"]),
        "match_count": len(matches),
        "task_count": sum(task_states.values()),
        "task_states": dict(sorted(task_states.items())),
        "page_refs": sorted(page_refs),
        "tags": sorted(tags),
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


def _normalize_topic(topic: str) -> str:
    return topic.strip().lstrip("#").casefold()


def _block_matches_topic(text: str, normalized_topic: str) -> bool:
    return normalized_topic in text.casefold()
