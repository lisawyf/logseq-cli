from __future__ import annotations

from logseq_cli.core.graph import iter_documents
from logseq_cli.core.models import Graph, TaskItem
from logseq_cli.core.pages import build_document


def parse_state_filter(states: str | None) -> set[str] | None:
    if not states:
        return None
    return {state.strip().upper() for state in states.split(",") if state.strip()}


def list_tasks(graph: Graph, states: str | None = None) -> list[TaskItem]:
    selected_states = parse_state_filter(states)
    tasks: list[TaskItem] = []

    for doc_type, directory in (("page", graph.pages_dir), ("journal", graph.journals_dir)):
        for path in iter_documents(directory):
            document = build_document(path, doc_type)
            for block in document.blocks:
                if not block.todo_state:
                    continue
                if selected_states is not None and block.todo_state not in selected_states:
                    continue
                tasks.append(
                    TaskItem(
                        path=document.path,
                        title=document.title,
                        doc_type=doc_type,
                        line_no=block.line_no,
                        state=block.todo_state,
                        text=block.text,
                        tags=block.tags,
                        page_refs=block.page_refs,
                        scheduled=block.scheduled,
                        deadline=block.deadline,
                    )
                )

    return tasks
