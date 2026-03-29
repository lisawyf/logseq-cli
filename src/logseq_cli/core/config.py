from __future__ import annotations

import os
from pathlib import Path
import tomllib

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "logseq-cli" / "config.toml"


def get_config_path() -> Path:
    override = os.environ.get("LOGSEQ_CLI_CONFIG_PATH")
    if override:
        return Path(override).expanduser()
    return DEFAULT_CONFIG_PATH


def get_default_graph_path() -> Path | None:
    config_path = get_config_path()
    if not config_path.exists():
        return None

    try:
        data = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None

    default_graph = data.get("default_graph")
    if not default_graph:
        return None
    return Path(default_graph).expanduser()


def set_default_graph_path(graph_path: Path) -> Path:
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    escaped = str(graph_path.expanduser().resolve()).replace("\\", "\\\\").replace('"', '\\"')
    new_line = f'default_graph = "{escaped}"'

    if config_path.exists():
        existing_lines = config_path.read_text(encoding="utf-8").splitlines()
    else:
        existing_lines = []

    updated_lines: list[str] = []
    replaced = False
    for line in existing_lines:
        stripped = line.strip()
        if stripped.startswith("default_graph"):
            updated_lines.append(new_line)
            replaced = True
        else:
            updated_lines.append(line)

    if not replaced:
        if updated_lines and updated_lines[0].strip():
            updated_lines = [new_line, "", *updated_lines]
        else:
            updated_lines = [new_line, *updated_lines]

    content = "\n".join(updated_lines).rstrip() + "\n"
    config_path.write_text(content, encoding="utf-8")
    return config_path
