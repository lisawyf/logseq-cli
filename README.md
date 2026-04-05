# logseq-cli

`logseq-cli` is a local CLI for file-based Logseq graphs.

It works directly on local graph folders and is intended for local shells, scripts, and coding agents. It does not depend on Logseq Desktop, and it does not expose MCP, HTTP, daemon, or any other network interface.

## Implemented MVP

The current CLI implements these commands:

- `graph detect`
- `graph use`
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
- `capture project`
- `capture task`
- `decisions list`
- `lessons list`
- `cards build decision`
- `cards build lesson`
- `cards build weekly`
- `cards build project`
- `cards build topic`
- `cards build tag`
- `recall topic`
- `timeline topic`
- `summarize daily`
- `summarize weekly`
- `summarize project`
- `summarize topic`
- `search links`
- `search tags`
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
python3 -m build --sdist --wheel
```

Or use the release helper script:

```bash
./scripts/release.sh all
```

This runs tests, a few JSON smoke checks, and builds local release artifacts into `dist/`.

## Usage

Detect a graph:

```bash
logseq-cli graph detect --graph ~/Documents/Logseq
```

Set the default graph for later commands:

```bash
logseq-cli graph use --graph ~/Documents/Logseq
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

Search using an alias group:

```bash
logseq-cli search text "MBB" --graph ~/Documents/Logseq --json
```

Search page refs:

```bash
logseq-cli search links "Project Notes" --graph ~/Documents/Logseq --json
```

Search tags:

```bash
logseq-cli search tags "ops" --graph ~/Documents/Logseq --json
```

Build local release artifacts:

```bash
./scripts/release.sh build
```

Suppress human-readable output:

```bash
logseq-cli graph detect --graph ~/Documents/Logseq --quiet
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

Capture a project note:

```bash
logseq-cli capture project "Project Alpha" --graph ~/Documents/Logseq --text "Investigated issue" --json
```

Capture a task:

```bash
logseq-cli capture task --graph ~/Documents/Logseq --today --text "Follow up with team" --project "Project Alpha" --json
```

Summarize a day:

```bash
logseq-cli summarize daily --graph ~/Documents/Logseq --date 2026-03-29 --json
```

Summarize a week:

```bash
logseq-cli summarize weekly --graph ~/Documents/Logseq --date 2026-03-29 --json
```

Summarize a project:

```bash
logseq-cli summarize project "OpenClaw" --graph ~/Documents/Logseq --json
```

Summarize a topic:

```bash
logseq-cli summarize topic "ops" --graph ~/Documents/Logseq --json
```

Recall a topic across pages and journals:

```bash
logseq-cli recall topic "MBB" --graph ~/Documents/Logseq --since 2026-01-01 --json
```

Show a topic timeline across journals:

```bash
logseq-cli timeline topic "MBB" --graph ~/Documents/Logseq --since 2026-01-01 --json
```

Build a topic knowledge card:

```bash
logseq-cli cards build topic "MBB" --graph ~/Documents/Logseq --json
```

Build a tag knowledge card:

```bash
logseq-cli cards build tag "ops" --graph ~/Documents/Logseq --json
```

Build a project knowledge card:

```bash
logseq-cli cards build project "OpenClaw" --graph ~/Documents/Logseq --json
```

List decision records and extracted reasons:

```bash
logseq-cli decisions list "MBB" --graph ~/Documents/Logseq --since 2026-01-01 --json
```

List lessons, pitfalls, and best practices:

```bash
logseq-cli lessons list "MBB" --graph ~/Documents/Logseq --since 2026-01-01 --json
```

Build a decision card:

```bash
logseq-cli cards build decision "MBB" --graph ~/Documents/Logseq --json
```

Build a lesson card:

```bash
logseq-cli cards build lesson "MBB" --graph ~/Documents/Logseq --json
```

Build a weekly card:

```bash
logseq-cli cards build weekly --graph ~/Documents/Logseq --date 2026-03-29 --json
```

## Graph Resolution

Graph discovery order:

1. `--graph`
2. `~/.config/logseq-cli/config.toml`
3. current directory upward auto-discovery

Optional config example:

```toml
default_graph = "/Users/you/Documents/Logseq"

[aliases]
MBB = ["Management by blocks", "management-by-blocks"]
OpenClaw = ["Open Claw", "open-claw"]
```

After `graph use`, commands can run outside the graph directory as long as no explicit `--graph` overrides it.

Alias groups are expanded automatically in:

- `search text`
- `search links`
- `search tags`
- `summarize topic`
- `recall topic`
- `timeline topic`
- `cards build topic`
- `cards build tag`
- `decisions list`
- `lessons list`

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

## Output Modes

- `--json` emits the stable machine-readable envelope.
- `--raw` is available on read commands that can print document content directly.
- `--quiet` suppresses normal human-readable stdout output but does not disable writes or change exit codes.

## Current Behavior

- Page resolution tries exact filename, case-insensitive filename, normalized filename, then heading-title matching.
- Page creation is conservative: it refuses to overwrite or create pages that collide by normalized name or heading title.
- Page append performs end-of-file append only; it does not rewrite or target headings.
- Page append-under appends within the matched section and stops before the next same-or-higher-level heading.
- Search is plain text substring search with optional `--scope` and `--limit`.
- Search links matches parsed `[[Page]]` references.
- Search tags matches parsed Markdown and Org tags.
- Alias groups from `config.toml` expand query terms across supported search, recall, card, decision, and lesson commands.
- Task extraction recognizes common Logseq-style TODO states from Markdown bullets and Org headings.
- Journal list returns journals in descending date order.
- Journal ensure creates an empty journal file only when missing.
- Journal append writes a single bullet block and supports `--dry-run`.
- Journal summarize is rule-based and reports block counts, task states, page refs, and tags.
- Link inspection is based on parsed `[[Page]]` references in page and journal content.
- Capture quick is a thin wrapper around safe journal append.
- Capture project appends a bullet to a project page and can create the page only with `--create-page`.
- Capture task appends a `TODO` entry to a journal and can include a project page reference.
- Summaries are rule-based aggregates over parsed journal content, not free-form generated text.
- Project summaries combine the project page, references to that page, related tasks, and outgoing page refs.
- Topic summaries aggregate blocks and tasks by case-insensitive text, tag, or page-ref matches.
- Topic recall builds a compact evidence pack with top matches, source counts, related tags, related page refs, and optional journal date filtering.
- Topic timeline focuses on journal history and returns chronologically ordered entries for a topic or tag.
- Knowledge cards compress recall output into summary, key points, open tasks, and evidence that Claude Code can reuse directly.
- Project cards combine the project page, related references, open tasks, related links, and compact evidence for project-oriented Q&A.
- Decision cards compress extracted decision records and reason snippets into an answer-ready decision brief.
- Lesson cards compress extracted lessons and takeaways into an answer-ready best-practices brief.
- Weekly cards compress a 7-day journal window into key points, open tasks, related refs, and evidence blocks.
- Decision extraction uses local heuristics to pull likely decisions plus inline or child-block reason snippets across pages and journals.
- Lesson extraction uses local heuristics to pull best practices, pitfalls, notes-to-self, and experience snippets across pages and journals.

## Known Limitations

- The CLI targets file-based graphs only.
- Org-mode support is read-oriented and intentionally partial.
- Search is lexical; there is no semantic search or date filtering.
- Write support is still intentionally narrow: `page create`, `page append`, `page append-under`, and `journal append`.

## Release Files

- [CHANGELOG.md](/Users/yiyi/program/llm/logseq-cli/CHANGELOG.md)
- [RELEASE.md](/Users/yiyi/program/llm/logseq-cli/RELEASE.md)
- [knowledge-base.md](/Users/yiyi/program/llm/logseq-cli/docs/knowledge-base.md)
- [claude-skill.md](/Users/yiyi/program/llm/logseq-cli/docs/claude-skill.md)

## Install Built Artifacts

Install on the current machine from the built wheel:

```bash
python3 -m pip install dist/logseq_cli-0.2.0-py3-none-any.whl
```

Upgrade an existing install:

```bash
python3 -m pip install --upgrade dist/logseq_cli-0.2.0-py3-none-any.whl
```

Install on another machine:

1. Copy `dist/logseq_cli-0.2.0-py3-none-any.whl` to that machine.
2. Run:

```bash
python3 -m pip install logseq_cli-0.2.0-py3-none-any.whl
```

If the other machine cannot resolve dependencies from package indexes, you can either install them separately first or use the same Python environment strategy you use locally.
