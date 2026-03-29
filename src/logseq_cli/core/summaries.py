from __future__ import annotations

from collections import Counter
from datetime import date

from logseq_cli.core.journals import read_journal
from logseq_cli.core.models import Graph


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
