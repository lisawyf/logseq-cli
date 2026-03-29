# logseq-cli

`logseq-cli` is a local CLI for file-based Logseq graphs.

It works directly on local graph folders and is intended for local shells, scripts, and coding agents. It does not depend on Logseq Desktop, and it does not expose MCP, HTTP, daemon, or any other network interface.

## Implemented MVP

The current CLI implements these commands:

- `graph detect`
- `page list`
- `page read`
- `journal read`
- `journal append`
- `search text`
- `tasks list`

All MVP commands support `--json`.

## Supported Graphs

Supported graph type:

- file-based Logseq graphs

Expected layout:

```text
GRAPH_ROOT/
├── journals/
├── pages/
├── assets/        # optional
└── logseq/        # optional, but `logseq/config.edn` also marks a graph root
```

Supported document formats:

- Markdown `.md`
- Org-mode `.org` with limited read support

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -e ".[dev]"
```

Verify:

```bash
logseq-cli --help
pytest
```

## Usage

Detect a graph:

```bash
logseq-cli graph detect --graph ~/Documents/Logseq
```

List pages:

```bash
logseq-cli page list --graph ~/Documents/Logseq --json
```

Read a page:

```bash
logseq-cli page read "OpenClaw" --graph ~/Documents/Logseq --json
```

Read a journal:

```bash
logseq-cli journal read --date 2026-03-29 --graph ~/Documents/Logseq --json
```

Append to a journal:

```bash
logseq-cli journal append --date 2026-03-29 --graph ~/Documents/Logseq --text "Investigated parser edge case"
```

Dry-run an append:

```bash
logseq-cli journal append --date 2026-03-29 --graph ~/Documents/Logseq --text "test append" --dry-run --json
```

Search text:

```bash
logseq-cli search text "OpenClaw" --graph ~/Documents/Logseq --scope pages,journals --json
```

List tasks:

```bash
logseq-cli tasks list --graph ~/Documents/Logseq --state todo,doing --json
```

## Graph Resolution

Graph discovery order:

1. `--graph`
2. `~/.config/logseq-cli/config.toml`
3. current directory upward auto-discovery

Optional config example:

```toml
default_graph = "/Users/you/Documents/Logseq"
```

## JSON Contract

Successful responses use this envelope:

```json
{
  "ok": true,
  "command": "page read",
  "graph_root": "/path/to/graph",
  "data": {},
  "warnings": [],
  "errors": []
}
```

Failure responses keep the same top-level fields:

```json
{
  "ok": false,
  "command": "page read",
  "graph_root": "/path/to/graph",
  "data": null,
  "warnings": [],
  "errors": [
    {
      "code": "PAGE_NOT_FOUND",
      "message": "Page 'Missing Page' not found"
    }
  ]
}
```

Stable exit codes:

- `0` success
- `1` general failure
- `2` invalid arguments
- `3` graph not found
- `4` page or journal not found
- `5` write conflict
- `6` parse failure

## Current Behavior

- Page resolution tries exact filename, case-insensitive filename, normalized filename, then heading-title matching.
- Search is plain text substring search with optional `--scope` and `--limit`.
- Task extraction recognizes common Logseq-style TODO states from Markdown bullets and Org headings.
- Journal append writes a single bullet block and supports `--dry-run`.

## Known Limitations

- The CLI targets file-based graphs only.
- Org-mode support is read-oriented and intentionally partial.
- Search is lexical; there is no semantic search or date filtering.
- Write support is limited to journal append in the MVP.
