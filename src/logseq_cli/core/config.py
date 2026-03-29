from __future__ import annotations

from pathlib import Path
import tomllib


CONFIG_PATH = Path.home() / ".config" / "logseq-cli" / "config.toml"


def get_default_graph_path() -> Path | None:
    if not CONFIG_PATH.exists():
        return None

    try:
        data = tomllib.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None

    default_graph = data.get("default_graph")
    if not default_graph:
        return None
    return Path(default_graph).expanduser()
