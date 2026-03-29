from __future__ import annotations

from datetime import date

from logseq_cli.core.errors import LogseqCliError
from logseq_cli.core.graph import Graph
from logseq_cli.core.journals import append_to_journal
from logseq_cli.core.pages import append_to_page, create_page, resolve_page


def capture_project(
    graph: Graph,
    project_name: str,
    text: str,
    *,
    create_missing: bool = False,
    dry_run: bool = False,
) -> dict[str, object]:
    captured_text = _as_bullet(text)

    try:
        resolve_page(graph, project_name)
    except LogseqCliError as error:
        if error.code != "PAGE_NOT_FOUND" or not create_missing:
            raise
        result = create_page(
            graph,
            project_name,
            text=captured_text,
            dry_run=dry_run,
        )
        result["project"] = project_name
        result["created_page"] = True
        return result

    result = append_to_page(
        graph,
        project_name,
        captured_text,
        dry_run=dry_run,
    )
    result["project"] = project_name
    result["created_page"] = False
    return result


def capture_task(
    graph: Graph,
    task_text: str,
    *,
    journal_date: date,
    project_name: str | None = None,
    dry_run: bool = False,
) -> dict[str, object]:
    text = _strip_list_prefix(task_text).strip()
    if project_name:
        text = f"TODO {text} [[{project_name}]]"
    else:
        text = f"TODO {text}"

    result = append_to_journal(
        graph,
        journal_date,
        text,
        dry_run=dry_run,
    )
    result["project"] = project_name
    return result


def _as_bullet(text: str) -> str:
    return f"- {_strip_list_prefix(text).strip()}"


def _strip_list_prefix(text: str) -> str:
    stripped = text.strip()
    for prefix in ("- ", "* ", "+ "):
        if stripped.startswith(prefix):
            return stripped[len(prefix):]
    return stripped
