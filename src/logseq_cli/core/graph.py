from __future__ import annotations

from pathlib import Path

from logseq_cli.core.config import get_default_graph_path
from logseq_cli.core.errors import ExitCodes, LogseqCliError
from logseq_cli.core.models import Graph


SUPPORTED_SUFFIXES = {".md", ".org"}


def is_graph_root(path: Path) -> bool:
    path = path.expanduser().resolve()
    has_dirs = (path / "pages").is_dir() and (path / "journals").is_dir()
    has_config = (path / "logseq" / "config.edn").is_file()
    return has_dirs or has_config


def validate_graph(path: Path) -> Graph:
    path = path.expanduser().resolve()
    if not is_graph_root(path):
        raise LogseqCliError(
            code="GRAPH_NOT_FOUND",
            message=f"Graph root not found at '{path}'",
            exit_code=ExitCodes.GRAPH_NOT_FOUND,
        )

    return Graph(
        root=path,
        pages_dir=path / "pages",
        journals_dir=path / "journals",
        assets_dir=(path / "assets") if (path / "assets").exists() else None,
        logseq_dir=(path / "logseq") if (path / "logseq").exists() else None,
        config_path=(path / "logseq" / "config.edn")
        if (path / "logseq" / "config.edn").exists()
        else None,
    )


def discover_graph_upward(start_path: Path) -> Graph | None:
    current = start_path.expanduser().resolve()
    if current.is_file():
        current = current.parent

    for candidate in (current, *current.parents):
        if is_graph_root(candidate):
            return validate_graph(candidate)
    return None


def resolve_graph(graph_path: Path | None, start_path: Path | None = None) -> Graph:
    if graph_path is not None:
        discovered = discover_graph_upward(graph_path)
        if discovered is not None:
            return discovered
        raise LogseqCliError(
            code="GRAPH_NOT_FOUND",
            message=f"Unable to resolve graph from '{graph_path}'",
            exit_code=ExitCodes.GRAPH_NOT_FOUND,
        )

    config_path = get_default_graph_path()
    if config_path is not None:
        discovered = discover_graph_upward(config_path)
        if discovered is not None:
            return discovered

    discovered = discover_graph_upward(start_path or Path.cwd())
    if discovered is not None:
        return discovered

    raise LogseqCliError(
        code="GRAPH_NOT_FOUND",
        message="Unable to detect a Logseq graph. Pass --graph or run inside a graph.",
        exit_code=ExitCodes.GRAPH_NOT_FOUND,
    )


def iter_documents(directory: Path):
    if not directory.exists():
        return
    for path in sorted(directory.iterdir()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
            yield path
