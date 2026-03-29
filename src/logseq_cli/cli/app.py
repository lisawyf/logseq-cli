from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from logseq_cli.core.errors import LogseqCliError
from logseq_cli.core.graph import resolve_graph
from logseq_cli.core.journals import append_to_journal, parse_target_date, read_journal
from logseq_cli.core.pages import list_pages, resolve_page
from logseq_cli.core.search import search_text
from logseq_cli.core.tasks import list_tasks
from logseq_cli.utils.output import emit_failure, emit_json, make_success

app = typer.Typer(help="CLI for local file-based Logseq graphs", no_args_is_help=True)
graph_app = typer.Typer(no_args_is_help=True)
page_app = typer.Typer(no_args_is_help=True)
journal_app = typer.Typer(no_args_is_help=True)
search_app = typer.Typer(no_args_is_help=True)
tasks_app = typer.Typer(no_args_is_help=True)

app.add_typer(graph_app, name="graph")
app.add_typer(page_app, name="page")
app.add_typer(journal_app, name="journal")
app.add_typer(search_app, name="search")
app.add_typer(tasks_app, name="tasks")

GraphOption = Annotated[Path | None, typer.Option("--graph", help="Path to the graph root.")]
JsonOption = Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")]
RawOption = Annotated[bool, typer.Option("--raw", help="Emit raw document content.")]


@graph_app.command("detect")
def graph_detect(
    graph: GraphOption = None,
    json_output: JsonOption = False,
) -> None:
    command = "graph detect"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    data = {
        "root": str(resolved_graph.root),
        "pages_dir": str(resolved_graph.pages_dir),
        "journals_dir": str(resolved_graph.journals_dir),
        "config_path": str(resolved_graph.config_path) if resolved_graph.config_path else None,
    }
    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    else:
        typer.echo(str(resolved_graph.root))


@page_app.command("list")
def page_list(
    graph: GraphOption = None,
    json_output: JsonOption = False,
) -> None:
    command = "page list"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        documents = list_pages(resolved_graph)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    page_data = [
        {
            "name": document.name,
            "title": document.title,
            "path": str(document.path),
            "format": document.format,
        }
        for document in documents
    ]
    if json_output:
        emit_json(make_success(command, resolved_graph, {"pages": page_data, "count": len(page_data)}))
    else:
        for page in page_data:
            typer.echo(f"{page['title']} ({page['name']})")


@page_app.command("read")
def page_read(
    page_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    raw: RawOption = False,
) -> None:
    command = "page read"
    resolved_graph = None
    try:
        if json_output and raw:
            raise LogseqCliError(
                code="INVALID_OUTPUT_MODE",
                message="Use either --json or --raw, not both.",
                exit_code=2,
            )
        resolved_graph = resolve_graph(graph)
        document = resolve_page(resolved_graph, page_name)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    data = document.model_dump(mode="json")
    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    else:
        typer.echo(document.content)


@journal_app.command("read")
def journal_read(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    raw: RawOption = False,
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Read today's journal.")] = False,
) -> None:
    command = "journal read"
    resolved_graph = None
    try:
        if json_output and raw:
            raise LogseqCliError(
                code="INVALID_OUTPUT_MODE",
                message="Use either --json or --raw, not both.",
                exit_code=2,
            )
        resolved_graph = resolve_graph(graph)
        journal_date = parse_target_date(target_date=date_value, today=today)
        document = read_journal(resolved_graph, journal_date)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    data = document.model_dump(mode="json")
    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    else:
        typer.echo(document.content)


@journal_app.command("append")
def journal_append(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    text: Annotated[str, typer.Option("--text", help="Text to append as a new bullet.")] = "",
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Append to today's journal.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be appended without writing.")] = False,
) -> None:
    command = "journal append"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        journal_date = parse_target_date(target_date=date_value, today=today)
        result = append_to_journal(resolved_graph, journal_date, text, dry_run=dry_run)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    else:
        action = "Would append" if dry_run else "Appended"
        typer.echo(f"{action} to {result['path']}")
        typer.echo(result["appended_text"], nl=False)


@search_app.command("text")
def search_text_command(
    query: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    scope: Annotated[str, typer.Option("--scope", help="Comma-separated scopes: pages,journals")] = "pages,journals",
    limit: Annotated[int, typer.Option("--limit", min=1, help="Maximum number of hits.")] = 20,
    case_sensitive: Annotated[bool, typer.Option("--case-sensitive", help="Use case-sensitive matching.")] = False,
) -> None:
    command = "search text"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        hits = search_text(
            resolved_graph,
            query,
            scope=scope,
            limit=limit,
            case_sensitive=case_sensitive,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, {"hits": hits, "query": query, "count": len(hits)}))
    else:
        for hit in hits:
            typer.echo(f"{hit.path}:{hit.line_no}: {hit.snippet}")


@tasks_app.command("list")
def tasks_list_command(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    state: Annotated[str | None, typer.Option("--state", help="Comma-separated TODO states to include.")] = None,
) -> None:
    command = "tasks list"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        tasks = list_tasks(resolved_graph, states=state)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, {"tasks": tasks, "count": len(tasks)}))
    else:
        for task in tasks:
            typer.echo(f"[{task.state}] {task.text} ({task.path}:{task.line_no})")
