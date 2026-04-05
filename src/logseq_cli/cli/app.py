from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from logseq_cli.core.decisions import list_decisions
from logseq_cli.core.cards import build_project_card, build_tag_card, build_topic_card
from logseq_cli.core.capture import capture_project, capture_task
from logseq_cli.core.config import get_config_path, set_default_graph_path
from logseq_cli.core.errors import LogseqCliError
from logseq_cli.core.graph import resolve_graph
from logseq_cli.core.journals import append_to_journal, ensure_journal, list_journals, parse_target_date, read_journal
from logseq_cli.core.links import backlinks, outgoing
from logseq_cli.core.pages import append_to_page, append_under_heading, create_page, list_pages, resolve_page
from logseq_cli.core.recall import parse_date_window, recall_topic, timeline_topic
from logseq_cli.core.search import search_links, search_tags, search_text
from logseq_cli.core.stats import graph_stats
from logseq_cli.core.summaries import summarize_daily, summarize_journal, summarize_project, summarize_topic, summarize_weekly
from logseq_cli.core.tasks import list_tasks
from logseq_cli.utils.output import emit_failure, emit_json, make_success

app = typer.Typer(help="CLI for local file-based Logseq graphs", no_args_is_help=True)
graph_app = typer.Typer(no_args_is_help=True)
page_app = typer.Typer(no_args_is_help=True)
journal_app = typer.Typer(no_args_is_help=True)
search_app = typer.Typer(no_args_is_help=True)
tasks_app = typer.Typer(no_args_is_help=True)
links_app = typer.Typer(no_args_is_help=True)
capture_app = typer.Typer(no_args_is_help=True)
summarize_app = typer.Typer(no_args_is_help=True)
recall_app = typer.Typer(no_args_is_help=True)
timeline_app = typer.Typer(no_args_is_help=True)
cards_app = typer.Typer(no_args_is_help=True)
cards_build_app = typer.Typer(no_args_is_help=True)
decisions_app = typer.Typer(no_args_is_help=True)

app.add_typer(graph_app, name="graph")
app.add_typer(page_app, name="page")
app.add_typer(journal_app, name="journal")
app.add_typer(search_app, name="search")
app.add_typer(tasks_app, name="tasks")
app.add_typer(links_app, name="links")
app.add_typer(capture_app, name="capture")
app.add_typer(summarize_app, name="summarize")
app.add_typer(recall_app, name="recall")
app.add_typer(timeline_app, name="timeline")
app.add_typer(cards_app, name="cards")
app.add_typer(decisions_app, name="decisions")
cards_app.add_typer(cards_build_app, name="build")

GraphOption = Annotated[Path | None, typer.Option("--graph", help="Path to the graph root.")]
JsonOption = Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")]
RawOption = Annotated[bool, typer.Option("--raw", help="Emit raw document content.")]
QuietOption = Annotated[bool, typer.Option("--quiet", help="Suppress human-readable stdout output.")]


@graph_app.command("detect")
def graph_detect(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
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
    elif not quiet:
        typer.echo(str(resolved_graph.root))


@graph_app.command("stats")
def graph_stats_command(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
) -> None:
    command = "graph stats"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        data = graph_stats(resolved_graph)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Pages: {data['pages']}")
        typer.echo(f"Journals: {data['journals']}")
        typer.echo(f"Documents: {data['documents']}")
        typer.echo(f"Tasks: {data['tasks']}")


@graph_app.command("use")
def graph_use(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
) -> None:
    command = "graph use"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        config_path = set_default_graph_path(resolved_graph.root)
        data = {
            "root": str(resolved_graph.root),
            "config_path": str(config_path),
            "default_graph": str(resolved_graph.root),
        }
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(str(resolved_graph.root))


@page_app.command("list")
def page_list(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
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
    elif not quiet:
        for page in page_data:
            typer.echo(f"{page['title']} ({page['name']})")


@page_app.command("read")
def page_read(
    page_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    raw: RawOption = False,
    quiet: QuietOption = False,
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
    elif not quiet:
        typer.echo(document.content)


@page_app.command("create")
def page_create(
    page_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    text: Annotated[str, typer.Option("--text", help="Optional initial page body.")] = "",
    page_format: Annotated[str, typer.Option("--format", help="Page format: markdown or org.")] = "markdown",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be created without writing.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "page create"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        result = create_page(
            resolved_graph,
            page_name,
            text=text,
            doc_format=page_format,
            dry_run=dry_run,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    elif not quiet:
        action = "Would create" if dry_run else "Created"
        typer.echo(f"{action} {result['path']}")


@page_app.command("append")
def page_append(
    page_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    text: Annotated[str, typer.Option("--text", help="Text to append at the end of the page.")] = "",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be appended without writing.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "page append"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        result = append_to_page(
            resolved_graph,
            page_name,
            text,
            dry_run=dry_run,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    elif not quiet:
        action = "Would append to" if dry_run else "Appended to"
        typer.echo(f"{action} {result['path']}")


@page_app.command("append-under")
def page_append_under(
    page_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    heading: Annotated[str, typer.Option("--heading", help="Heading title to append under.")] = "",
    text: Annotated[str, typer.Option("--text", help="Text to append within the heading section.")] = "",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be appended without writing.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "page append-under"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        result = append_under_heading(
            resolved_graph,
            page_name,
            heading,
            text,
            dry_run=dry_run,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    elif not quiet:
        action = "Would append under" if dry_run else "Appended under"
        typer.echo(f"{action} '{result['heading']}' in {result['path']}")


@journal_app.command("read")
def journal_read(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    raw: RawOption = False,
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Read today's journal.")] = False,
    quiet: QuietOption = False,
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
    elif not quiet:
        typer.echo(document.content)


@journal_app.command("list")
def journal_list(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    limit: Annotated[int | None, typer.Option("--limit", min=1, help="Maximum number of journals to return.")] = None,
    quiet: QuietOption = False,
) -> None:
    command = "journal list"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        journals = list_journals(resolved_graph, limit=limit)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    data = {
        "journals": [
            {
                "title": document.title,
                "path": str(document.path),
                "format": document.format,
                "journal_date": document.journal_date.isoformat() if document.journal_date else None,
            }
            for document in journals
        ],
        "count": len(journals),
    }
    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        for journal in data["journals"]:
            typer.echo(journal["title"])


@journal_app.command("ensure")
def journal_ensure(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Ensure today's journal exists.")] = False,
    journal_format: Annotated[str, typer.Option("--format", help="Journal format: markdown or org.")] = "markdown",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be created without writing.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "journal ensure"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        journal_date = parse_target_date(target_date=date_value, today=today)
        result = ensure_journal(
            resolved_graph,
            journal_date,
            doc_format=journal_format,
            dry_run=dry_run,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    elif not quiet:
        action = "Would create" if dry_run and result["created"] else "Exists"
        if not dry_run and result["created"]:
            action = "Created"
        typer.echo(f"{action} {result['path']}")


@journal_app.command("append")
def journal_append(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    text: Annotated[str, typer.Option("--text", help="Text to append as a new bullet.")] = "",
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Append to today's journal.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be appended without writing.")] = False,
    quiet: QuietOption = False,
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
    elif not quiet:
        action = "Would append" if dry_run else "Appended"
        typer.echo(f"{action} to {result['path']}")
        typer.echo(result["appended_text"], nl=False)


@journal_app.command("summarize")
def journal_summarize(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Summarize today's journal.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "journal summarize"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        journal_date = parse_target_date(target_date=date_value, today=today)
        data = summarize_journal(resolved_graph, journal_date)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Journal: {data['title']}")
        typer.echo(f"Blocks: {data['block_count']}")
        typer.echo(f"Tasks: {data['task_count']}")


@search_app.command("text")
def search_text_command(
    query: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    scope: Annotated[str, typer.Option("--scope", help="Comma-separated scopes: pages,journals")] = "pages,journals",
    limit: Annotated[int, typer.Option("--limit", min=1, help="Maximum number of hits.")] = 20,
    case_sensitive: Annotated[bool, typer.Option("--case-sensitive", help="Use case-sensitive matching.")] = False,
    quiet: QuietOption = False,
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
    elif not quiet:
        for hit in hits:
            typer.echo(f"{hit.path}:{hit.line_no}: {hit.snippet}")


@search_app.command("links")
def search_links_command(
    target: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    scope: Annotated[str, typer.Option("--scope", help="Comma-separated scopes: pages,journals")] = "pages,journals",
    limit: Annotated[int, typer.Option("--limit", min=1, help="Maximum number of hits.")] = 20,
    quiet: QuietOption = False,
) -> None:
    command = "search links"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        hits = search_links(
            resolved_graph,
            target,
            scope=scope,
            limit=limit,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    data = {
        "target": target,
        "hits": hits,
        "count": len(hits),
    }
    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        for hit in hits:
            typer.echo(f"{hit['path']}:{hit['line_no']} {hit['snippet']}")


@search_app.command("tags")
def search_tags_command(
    tag: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    scope: Annotated[str, typer.Option("--scope", help="Comma-separated scopes: pages,journals")] = "pages,journals",
    limit: Annotated[int, typer.Option("--limit", min=1, help="Maximum number of hits.")] = 20,
    quiet: QuietOption = False,
) -> None:
    command = "search tags"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        hits = search_tags(
            resolved_graph,
            tag,
            scope=scope,
            limit=limit,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    data = {
        "tag": tag.lstrip("#"),
        "hits": hits,
        "count": len(hits),
    }
    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        for hit in hits:
            typer.echo(f"{hit['path']}:{hit['line_no']} {hit['snippet']}")


@tasks_app.command("list")
def tasks_list_command(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    state: Annotated[str | None, typer.Option("--state", help="Comma-separated TODO states to include.")] = None,
    quiet: QuietOption = False,
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
    elif not quiet:
        for task in tasks:
            typer.echo(f"[{task.state}] {task.text} ({task.path}:{task.line_no})")


@links_app.command("backlinks")
def links_backlinks(
    page_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
) -> None:
    command = "links backlinks"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        matches = backlinks(resolved_graph, page_name)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    data = {
        "page": page_name,
        "matches": matches,
        "count": len(matches),
    }
    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        for match in matches:
            typer.echo(f"{match['title']}:{match['line_no']} {match['text']}")


@links_app.command("outgoing")
def links_outgoing(
    page_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
) -> None:
    command = "links outgoing"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        data = outgoing(resolved_graph, page_name)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        for link in data["links"]:
            typer.echo(f"{link['page']} ({link['count']})")


@capture_app.command("quick")
def capture_quick(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    text: Annotated[str, typer.Option("--text", help="Quick capture text to append to a journal.")] = "",
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Capture into today's journal.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be captured without writing.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "capture quick"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        journal_date = parse_target_date(target_date=date_value, today=today)
        result = append_to_journal(
            resolved_graph,
            journal_date,
            text,
            dry_run=dry_run,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    elif not quiet:
        action = "Would capture into" if dry_run else "Captured into"
        typer.echo(f"{action} {result['path']}")


@capture_app.command("project")
def capture_project_command(
    project_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    text: Annotated[str, typer.Option("--text", help="Project capture text to append as a bullet.")] = "",
    create_page: Annotated[bool, typer.Option("--create-page", help="Create the project page when missing.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be captured without writing.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "capture project"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        result = capture_project(
            resolved_graph,
            project_name,
            text,
            create_missing=create_page,
            dry_run=dry_run,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    elif not quiet:
        action = "Would capture into" if dry_run else "Captured into"
        typer.echo(f"{action} {result['path']}")


@capture_app.command("task")
def capture_task_command(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    text: Annotated[str, typer.Option("--text", help="Task text to capture as a TODO.")] = "",
    project: Annotated[str | None, typer.Option("--project", help="Optional project page reference to append to the task.")] = None,
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Capture into today's journal.")] = False,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show what would be captured without writing.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "capture task"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        journal_date = parse_target_date(target_date=date_value, today=today)
        result = capture_task(
            resolved_graph,
            text,
            journal_date=journal_date,
            project_name=project,
            dry_run=dry_run,
        )
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, result))
    elif not quiet:
        action = "Would capture into" if dry_run else "Captured into"
        typer.echo(f"{action} {result['path']}")


@summarize_app.command("daily")
def summarize_daily_command(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    date_value: Annotated[str | None, typer.Option("--date", help="Journal date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Summarize today's journal.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "summarize daily"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        target_date = parse_target_date(target_date=date_value, today=today)
        data = summarize_daily(resolved_graph, target_date)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Daily summary for {data['journal_date']}")
        typer.echo(f"Blocks: {data['block_count']}")
        typer.echo(f"Tasks: {data['task_count']}")


@summarize_app.command("weekly")
def summarize_weekly_command(
    graph: GraphOption = None,
    json_output: JsonOption = False,
    date_value: Annotated[str | None, typer.Option("--date", help="Anchor date as YYYY-MM-DD.")] = None,
    today: Annotated[bool, typer.Option("--today", help="Use today's date as the weekly anchor.")] = False,
    quiet: QuietOption = False,
) -> None:
    command = "summarize weekly"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        target_date = parse_target_date(target_date=date_value, today=today)
        data = summarize_weekly(resolved_graph, target_date)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Weekly summary ending {data['end_date']}")
        typer.echo(f"Journals: {data['journal_count']}")
        typer.echo(f"Tasks: {data['task_count']}")


@summarize_app.command("project")
def summarize_project_command(
    project_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
) -> None:
    command = "summarize project"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        data = summarize_project(resolved_graph, project_name)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Project summary for {data['project_title']}")
        typer.echo(f"Sources: {data['source_count']}")
        typer.echo(f"Tasks: {data['related_task_count']}")


@summarize_app.command("topic")
def summarize_topic_command(
    topic: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    quiet: QuietOption = False,
) -> None:
    command = "summarize topic"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        data = summarize_topic(resolved_graph, topic)
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Topic summary for {data['topic']}")
        typer.echo(f"Sources: {data['source_count']}")
        typer.echo(f"Matches: {data['match_count']}")


@recall_app.command("topic")
def recall_topic_command(
    topic: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    since: Annotated[str | None, typer.Option("--since", help="Include journals on or after YYYY-MM-DD.")] = None,
    until: Annotated[str | None, typer.Option("--until", help="Include journals on or before YYYY-MM-DD.")] = None,
    limit: Annotated[int, typer.Option("--limit", min=1, help="Maximum number of top matches to return.")] = 10,
    quiet: QuietOption = False,
) -> None:
    command = "recall topic"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        since_date, until_date = parse_date_window(since=since, until=until)
        data = recall_topic(
            resolved_graph,
            topic,
            since=since_date,
            until=until_date,
            limit=limit,
        )
    except ValueError as error:
        emit_failure(
            command,
            resolved_graph,
            LogseqCliError(code="INVALID_DATE_RANGE", message=str(error), exit_code=2),
            json_output,
        )
        return
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Topic recall for {data['topic']}")
        typer.echo(f"Sources: {data['source_count']}")
        typer.echo(f"Matches: {data['match_count']}")


@timeline_app.command("topic")
def timeline_topic_command(
    topic: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    since: Annotated[str | None, typer.Option("--since", help="Include journals on or after YYYY-MM-DD.")] = None,
    until: Annotated[str | None, typer.Option("--until", help="Include journals on or before YYYY-MM-DD.")] = None,
    limit: Annotated[int, typer.Option("--limit", min=1, help="Maximum number of timeline entries to return.")] = 50,
    quiet: QuietOption = False,
) -> None:
    command = "timeline topic"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        since_date, until_date = parse_date_window(since=since, until=until)
        data = timeline_topic(
            resolved_graph,
            topic,
            since=since_date,
            until=until_date,
            limit=limit,
        )
    except ValueError as error:
        emit_failure(
            command,
            resolved_graph,
            LogseqCliError(code="INVALID_DATE_RANGE", message=str(error), exit_code=2),
            json_output,
        )
        return
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(f"Topic timeline for {data['topic']}")
        typer.echo(f"Entries: {data['entry_count']}")
        typer.echo(f"Journals: {data['journal_count']}")


@cards_build_app.command("topic")
def cards_build_topic_command(
    topic: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    since: Annotated[str | None, typer.Option("--since", help="Include journals on or after YYYY-MM-DD.")] = None,
    until: Annotated[str | None, typer.Option("--until", help="Include journals on or before YYYY-MM-DD.")] = None,
    evidence_limit: Annotated[int, typer.Option("--evidence-limit", min=1, help="Maximum number of evidence items to use.")] = 8,
    quiet: QuietOption = False,
) -> None:
    command = "cards build topic"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        since_date, until_date = parse_date_window(since=since, until=until)
        data = build_topic_card(
            resolved_graph,
            topic,
            since=since_date,
            until=until_date,
            evidence_limit=evidence_limit,
        )
    except ValueError as error:
        emit_failure(
            command,
            resolved_graph,
            LogseqCliError(code="INVALID_DATE_RANGE", message=str(error), exit_code=2),
            json_output,
        )
        return
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(data["title"])
        typer.echo(data["summary"])


@cards_build_app.command("tag")
def cards_build_tag_command(
    tag: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    since: Annotated[str | None, typer.Option("--since", help="Include journals on or after YYYY-MM-DD.")] = None,
    until: Annotated[str | None, typer.Option("--until", help="Include journals on or before YYYY-MM-DD.")] = None,
    evidence_limit: Annotated[int, typer.Option("--evidence-limit", min=1, help="Maximum number of evidence items to use.")] = 8,
    quiet: QuietOption = False,
) -> None:
    command = "cards build tag"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        since_date, until_date = parse_date_window(since=since, until=until)
        data = build_tag_card(
            resolved_graph,
            tag,
            since=since_date,
            until=until_date,
            evidence_limit=evidence_limit,
        )
    except ValueError as error:
        emit_failure(
            command,
            resolved_graph,
            LogseqCliError(code="INVALID_DATE_RANGE", message=str(error), exit_code=2),
            json_output,
        )
        return
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(data["title"])
        typer.echo(data["summary"])


@cards_build_app.command("project")
def cards_build_project_command(
    project_name: str,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    since: Annotated[str | None, typer.Option("--since", help="Include journals on or after YYYY-MM-DD.")] = None,
    until: Annotated[str | None, typer.Option("--until", help="Include journals on or before YYYY-MM-DD.")] = None,
    evidence_limit: Annotated[int, typer.Option("--evidence-limit", min=1, help="Maximum number of evidence items to use.")] = 8,
    quiet: QuietOption = False,
) -> None:
    command = "cards build project"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        since_date, until_date = parse_date_window(since=since, until=until)
        data = build_project_card(
            resolved_graph,
            project_name,
            since=since_date,
            until=until_date,
            evidence_limit=evidence_limit,
        )
    except ValueError as error:
        emit_failure(
            command,
            resolved_graph,
            LogseqCliError(code="INVALID_DATE_RANGE", message=str(error), exit_code=2),
            json_output,
        )
        return
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        typer.echo(data["title"])
        typer.echo(data["summary"])


@decisions_app.command("list")
def decisions_list_command(
    query: Annotated[str | None, typer.Argument(help="Optional topic, tag, or text filter.")] = None,
    graph: GraphOption = None,
    json_output: JsonOption = False,
    scope: Annotated[str, typer.Option("--scope", help="Comma-separated scopes: pages,journals")] = "pages,journals",
    since: Annotated[str | None, typer.Option("--since", help="Include journals on or after YYYY-MM-DD.")] = None,
    until: Annotated[str | None, typer.Option("--until", help="Include journals on or before YYYY-MM-DD.")] = None,
    limit: Annotated[int, typer.Option("--limit", min=1, help="Maximum number of decisions to return.")] = 20,
    quiet: QuietOption = False,
) -> None:
    command = "decisions list"
    resolved_graph = None
    try:
        resolved_graph = resolve_graph(graph)
        since_date, until_date = parse_date_window(since=since, until=until)
        data = list_decisions(
            resolved_graph,
            query=query,
            scope=scope,
            since=since_date,
            until=until_date,
            limit=limit,
        )
    except ValueError as error:
        emit_failure(
            command,
            resolved_graph,
            LogseqCliError(code="INVALID_DATE_RANGE", message=str(error), exit_code=2),
            json_output,
        )
        return
    except LogseqCliError as error:
        emit_failure(command, resolved_graph, error, json_output)
        return

    if json_output:
        emit_json(make_success(command, resolved_graph, data))
    elif not quiet:
        for item in data["decisions"]:
            typer.echo(f"{item['title']}:{item['line_no']} {item['text']}")
