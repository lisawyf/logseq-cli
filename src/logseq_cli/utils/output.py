from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer

from logseq_cli.core.errors import LogseqCliError
from logseq_cli.core.models import CommandResult, ErrorInfo, Graph


def serialize_for_json(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [serialize_for_json(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_for_json(item) for key, item in value.items()}
    if isinstance(value, Path):
        return str(value)
    return value


def emit_json(result: CommandResult) -> None:
    typer.echo(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


def make_success(command: str, graph: Graph | None, data: Any) -> CommandResult:
    return CommandResult(
        ok=True,
        command=command,
        graph_root=str(graph.root) if graph else None,
        data=serialize_for_json(data),
        warnings=[],
        errors=[],
    )


def make_failure(command: str, graph: Graph | None, error: LogseqCliError) -> CommandResult:
    return CommandResult(
        ok=False,
        command=command,
        graph_root=str(graph.root) if graph else None,
        data=None,
        warnings=[],
        errors=[ErrorInfo(code=error.code, message=error.message)],
    )


def emit_failure(command: str, graph: Graph | None, error: LogseqCliError, json_output: bool) -> None:
    if json_output:
        emit_json(make_failure(command, graph, error))
    else:
        typer.echo(f"{error.code}: {error.message}", err=True)
    raise typer.Exit(code=error.exit_code)
