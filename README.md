# logseq-cli

`logseq-cli` is a local CLI for file-based Logseq graphs.

It works directly on local graph folders and is intended for local shells, scripts, and coding agents. It does not depend on Logseq Desktop, and it does not expose MCP, HTTP, daemon, or any other network interface.

## Implemented MVP

The current CLI implements these commands:

- `graph detect`
- `graph stats`
- `page list`
- `page read`
- `page create`
- `page append`
- `page append-under`
- `journal list`
- `journal ensure`
- `journal read`
- `journal append`
- `journal summarize`
- `links backlinks`
- `links outgoing`
- `capture quick`
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

Show graph stats:

```bash
logseq-cli graph stats --graph ~/Documents/Logseq --json
```

List pages:

```bash
logseq-cli page list --graph ~/Documents/Logseq --json
```

Read a page:

```bash
logseq-cli page read "OpenClaw" --graph ~/Documents/Logseq --json
```

Create a page:

```bash
logseq-cli page create "Weekly Plan" --graph ~/Documents/Logseq --text "- TODO Review goals" --json
```

Append to a page:

```bash
logseq-cli page append "Weekly Plan" --graph ~/Documents/Logseq --text "- Captured next action" --json
```

Append under a heading:

```bash
logseq-cli page append-under "Weekly Plan" --graph ~/Documents/Logseq --heading "Today" --text "- Captured next action" --json
```

Read a journal:

```bash
logseq-cli journal read --date 2026-03-29 --graph ~/Documents/Logseq --json
```

List journals:

```bash
logseq-cli journal list --graph ~/Documents/Logseq --limit 7 --json
```

Ensure a journal exists:

```bash
logseq-cli journal ensure --date 2026-03-29 --graph ~/Documents/Logseq --json
```

Summarize a journal:

```bash
logseq-cli journal summarize --date 2026-03-29 --graph ~/Documents/Logseq --json
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

Show backlinks:

```bash
logseq-cli links backlinks "OpenClaw" --graph ~/Documents/Logseq --json
```

Show outgoing links:

```bash
logseq-cli links outgoing "OpenClaw" --graph ~/Documents/Logseq --json
```

Quick capture to a journal:

```bash
logseq-cli capture quick --graph ~/Documents/Logseq --today --text "Captured item" --json
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
- Page creation is conservative: it refuses to overwrite or create pages that collide by normalized name or heading title.
- Page append performs end-of-file append only; it does not rewrite or target headings.
- Page append-under appends within the matched section and stops before the next same-or-higher-level heading.
- Search is plain text substring search with optional `--scope` and `--limit`.
- Task extraction recognizes common Logseq-style TODO states from Markdown bullets and Org headings.
- Journal list returns journals in descending date order.
- Journal ensure creates an empty journal file only when missing.
- Journal append writes a single bullet block and supports `--dry-run`.
- Journal summarize is rule-based and reports block counts, task states, page refs, and tags.
- Link inspection is based on parsed `[[Page]]` references in page and journal content.
- Capture quick is a thin wrapper around safe journal append.

## Known Limitations

- The CLI targets file-based graphs only.
- Org-mode support is read-oriented and intentionally partial.
- Search is lexical; there is no semantic search or date filtering.
- Write support is still intentionally narrow: `page create`, `page append`, `page append-under`, and `journal append`.
