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
    data = load_config_data()
    default_graph = data.get("default_graph")
    if not default_graph:
        return None
    return Path(default_graph).expanduser()


def load_config_data() -> dict[str, object]:
    config_path = get_config_path()
    if not config_path.exists():
        return {}

    try:
        return tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}


def resolve_alias_terms(query: str) -> list[str]:
    clean_query = query.strip()
    if not clean_query:
        return []

    aliases_section = load_config_data().get("aliases")
    if not isinstance(aliases_section, dict):
        return [clean_query]

    normalized_query = clean_query.casefold()
    matched_groups: list[list[str]] = []
    for key, value in aliases_section.items():
        if not isinstance(key, str):
            continue
        terms = _alias_group_terms(key, value)
        normalized_terms = {term.casefold() for term in terms}
        if normalized_query in normalized_terms:
            matched_groups.append(terms)

    if not matched_groups:
        return [clean_query]

    merged: list[str] = []
    seen: set[str] = set()
    for group in matched_groups:
        for term in group:
            normalized = term.casefold()
            if normalized in seen:
                continue
            seen.add(normalized)
            merged.append(term)
    return merged


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


def _alias_group_terms(key: str, value: object) -> list[str]:
    terms = [key]
    if isinstance(value, str):
        terms.append(value)
    elif isinstance(value, list):
        terms.extend(item for item in value if isinstance(item, str))

    cleaned: list[str] = []
    seen: set[str] = set()
    for term in terms:
        normalized = term.strip()
        if not normalized:
            continue
        folded = normalized.casefold()
        if folded in seen:
            continue
        seen.add(folded)
        cleaned.append(normalized)
    return cleaned
